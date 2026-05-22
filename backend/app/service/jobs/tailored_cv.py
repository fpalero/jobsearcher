import logging
import os
import re
import threading
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from app.core.data_unified_repository import unified_jobs_collection
from app.service.llm_config import get_llm
from app.service.jobs.md_to_ats_pdf import markdown_to_pdf

logger = logging.getLogger(__name__)

_generation_locks: dict[str, threading.Lock] = {}
_locks_lock = threading.Lock()

RESOURCES = Path(__file__).resolve().parent.parent.parent.parent / "resources"
CV_MD_PATH = RESOURCES / "CV.md"
PROMPT_PATH = RESOURCES / "prompts" / "ats-prompt.md"
APPLICATIONS_DIR = RESOURCES / "applications"

# Initialize RAG components for resume tips
RESUME_TIPS_PATH = RESOURCES / "resume-tips-for-engineering-majors.pdf"
CHROMA_PATH = RESOURCES / "chroma_db"

def _initialize_resume_tips_rag():
    """Initialize RAG system with resume tips PDF"""
    try:
        # Load and split the PDF
        loader = PyPDFLoader(str(RESUME_TIPS_PATH))
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        splits = text_splitter.split_documents(documents)
        
        # Create embeddings and vector store
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Create or load Chroma vector store
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=str(CHROMA_PATH)
        )
        
        return vectorstore.as_retriever(search_kwargs={"k": 3})
    except Exception as e:
        logger.warning(f"Failed to initialize RAG system: {e}")
        return None

_resume_tips_retriever = None
_rag_initialized = False


def _get_resume_tips_retriever():
    global _resume_tips_retriever, _rag_initialized
    if not _rag_initialized:
        _resume_tips_retriever = _initialize_resume_tips_rag()
        _rag_initialized = True
    return _resume_tips_retriever


class JobNotFoundError(Exception):
    pass


class TailoredCVError(Exception):
    pass


def _slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s-]+", "_", s)
    return s.strip("_")


def _fetch_job(job_id: str) -> dict:
    doc = unified_jobs_collection.find_one({"job_id": job_id})
    if not doc:
        raise JobNotFoundError(f"No job found with job_id={job_id}")
    return doc


def _get_or_create_paths(company: str, job_id: str) -> tuple[Path, Path, str]:
    slug = f"{_slugify(company)}-{job_id}"
    base = APPLICATIONS_DIR / slug
    md_path = base / f"cv_{slug}.md"
    pdf_path = base / "pdf" / f"cv_{slug}.pdf"
    base.mkdir(parents=True, exist_ok=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    return md_path, pdf_path, slug


def _generate_via_llm(job: dict) -> str:
    cv_text = CV_MD_PATH.read_text(encoding="utf-8")
    prompt_text = PROMPT_PATH.read_text(encoding="utf-8")
    prompt_template = ChatPromptTemplate.from_template(prompt_text)

    description = (
        job.get("description")
        or job.get("job_description")
        or job.get("description_text")
        or ""
    )
    title = job.get("title") or job.get("job_title") or ""
    company = job.get("company") or job.get("employer_name") or ""
    location = job.get("location") or job.get("job_location") or ""

    job_description_base = f"Title: {title}\nCompany: {company}\nLocation: {location}\n\n{description}"

    # Retrieve relevant resume tips if RAG is available
    job_description = job_description_base
    retriever = _get_resume_tips_retriever()
    if retriever:
        try:
            tips_docs = retriever.invoke(job_description_base)
            tips_text = "\n\n".join([doc.page_content for doc in tips_docs])
            if tips_text.strip():
                job_description = f"{job_description_base}\n\nRelevant resume tips from 'Resume Tips for Engineering Majors':\n{tips_text}"
        except Exception as e:
            logger.warning(f"Failed to retrieve resume tips: {e}")

    logger.info("Calling LLM for job_id=%s title=%s", job.get("job_id"), title)
    llm = get_llm()
    chain = prompt_template | llm
    response = chain.invoke({"cv": cv_text, "job_description": job_description})

    raw = response.content.strip()
    logger.debug("LLM raw response length=%d", len(raw))

    if raw.startswith("```"):
        raw = re.sub(r"^```\w*\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        logger.debug("Stripped markdown code fences")

    return raw


def _get_lock(key: str) -> threading.Lock:
    with _locks_lock:
        if key not in _generation_locks:
            _generation_locks[key] = threading.Lock()
        return _generation_locks[key]


def generate_tailored_pdf(job_id: str) -> Path:
    logger.info("generate_tailored_pdf called for job_id=%s", job_id)
    lock = _get_lock(job_id)
    with lock:
        job = _fetch_job(job_id)
        company = job.get("company") or "unknown"
        md_path, pdf_path, slug = _get_or_create_paths(company, job_id)
        logger.info("Paths: md=%s pdf=%s", md_path, pdf_path)

        if pdf_path.exists():
            logger.info("PDF already exists, returning cached")
            return pdf_path

        if not md_path.exists():
            logger.info("Markdown not cached, calling LLM")
            md_content = _generate_via_llm(job)
            md_path.write_text(md_content, encoding="utf-8")
            logger.info("Markdown saved to %s", md_path)

            desc_path = md_path.with_name(f"{slug}_description.md")
            if not desc_path.exists():
                desc_path.write_text(
                    f"# {job.get('title', '')} @ {company}\n\n"
                    f"**Company:** {company}\n\n"
                    f"**Link:** {job.get('apply_link', '')}\n\n"
                    f"## Job Description\n\n{job.get('description', '')}",
                    encoding="utf-8",
                )
        else:
            logger.info("Markdown already cached at %s", md_path)

        md_content = md_path.read_text(encoding="utf-8")

        try:
            logger.info("Generating PDF from Markdown via cmarker")
            markdown_to_pdf(md_content, pdf_path)
            logger.info("PDF generated successfully: %s", pdf_path)
        except Exception as e:
            logger.exception("PDF generation failed")
            raise TailoredCVError(f"Failed to generate PDF: {e}") from e

        return pdf_path

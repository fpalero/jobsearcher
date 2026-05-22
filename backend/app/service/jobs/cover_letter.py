import re
import threading
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

from app.core.data_unified_repository import unified_jobs_collection
from app.service.llm_config import get_llm
from app.service.jobs.md_to_ats_pdf import markdown_to_pdf

_generation_locks: dict[str, threading.Lock] = {}
_locks_lock = threading.Lock()

RESOURCES = Path(__file__).resolve().parent.parent.parent.parent / "resources"
CV_MD_PATH = RESOURCES / "CV.md"
PROMPT_PATH = RESOURCES / "prompts" / "cover-letter-prompt.md"
APPLICATIONS_DIR = RESOURCES / "applications"


class CoverLetterError(Exception):
    pass


def _slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s-]+", "_", s)
    return s.strip("_")


def _fetch_job(job_id: str) -> dict:
    doc = unified_jobs_collection.find_one({"job_id": job_id})
    if not doc:
        raise CoverLetterError(f"No job found with job_id={job_id}")
    return doc


def _get_or_create_paths(company: str, job_id: str) -> tuple[Path, Path, str]:
    slug = f"{_slugify(company)}-{job_id}"
    base = APPLICATIONS_DIR / slug
    md_path = base / f"cover_letter_{slug}.md"
    pdf_path = base / "pdf" / f"cover_letter_{slug}.pdf"
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

    job_description = f"Title: {title}\nCompany: {company}\nLocation: {location}\n\n{description}"

    llm = get_llm()
    chain = prompt_template | llm
    response = chain.invoke({"cv": cv_text, "job_description": job_description})
    return response.content.strip()


def _get_lock(key: str) -> threading.Lock:
    with _locks_lock:
        if key not in _generation_locks:
            _generation_locks[key] = threading.Lock()
        return _generation_locks[key]


def generate_cover_letter_pdf(job_id: str) -> Path:
    lock = _get_lock(job_id)
    with lock:
        job = _fetch_job(job_id)
        company = job.get("company") or job.get("employer_name") or "unknown"
        md_path, pdf_path, slug = _get_or_create_paths(company, job_id)

        if pdf_path.exists():
            return pdf_path

        if not md_path.exists():
            md_content = _generate_via_llm(job)
            md_path.write_text(md_content, encoding="utf-8")

        try:
            markdown_to_pdf(md_path, pdf_path)
        except Exception as e:
            raise CoverLetterError(f"Failed to convert MD to PDF: {e}") from e

        return pdf_path

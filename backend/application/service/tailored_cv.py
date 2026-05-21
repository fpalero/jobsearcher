import json
import logging
import re
import threading
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

from core.data_unified_repository import unified_jobs_collection
from application.service.llm_config import get_llm
from scripts.md_to_ats_pdf import cv_json_to_pdf

logger = logging.getLogger(__name__)

_generation_locks: dict[str, threading.Lock] = {}
_locks_lock = threading.Lock()

RESOURCES = Path(__file__).resolve().parent.parent.parent / "resources"
CV_MD_PATH = RESOURCES / "CV.md"
PROMPT_PATH = RESOURCES.parent / "docs" / "ats-prompt.md"
APPLICATIONS_DIR = RESOURCES / "applications"


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
    json_path = base / f"cv_{slug}.json"
    pdf_path = base / "pdf" / f"cv_{slug}.pdf"
    base.mkdir(parents=True, exist_ok=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    return json_path, pdf_path, slug


def _generate_via_llm(job: dict) -> dict:
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

    logger.info("Calling LLM for job_id=%s title=%s", job.get("job_id"), title)
    llm = get_llm()
    chain = prompt_template | llm
    response = chain.invoke({"cv": cv_text, "job_description": job_description})

    raw = response.content.strip()
    logger.debug("LLM raw response length=%d", len(raw))

    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        logger.debug("Stripped markdown code fences")

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error(
            "LLM returned invalid JSON. First 2000 chars: %s",
            raw[:2000],
        )
        raise TailoredCVError(
            f"LLM response is not valid JSON: {exc}\n"
            f"First 200 chars: {raw[:200]}"
        ) from exc

    if not isinstance(parsed, dict):
        logger.error(
            "LLM returned JSON %s instead of object. Raw: %s",
            type(parsed).__name__,
            raw[:500],
        )
        raise TailoredCVError(
            f"LLM returned a JSON {type(parsed).__name__}, expected a JSON object. "
            f"First 100 chars: {raw[:100]}"
        )

    return parsed


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
        json_path, pdf_path, slug = _get_or_create_paths(company, job_id)
        logger.info("Paths: json=%s pdf=%s", json_path, pdf_path)

        if pdf_path.exists():
            logger.info("PDF already exists, returning cached")
            return pdf_path

        if not json_path.exists():
            logger.info("JSON not cached, calling LLM")
            data = _generate_via_llm(job)
            json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info("JSON saved to %s", json_path)

            desc_path = json_path.with_name(f"{slug}_description.md")
            if not desc_path.exists():
                desc_path.write_text(
                    f"# {job.get('title', '')} @ {company}\n\n"
                    f"**Company:** {company}\n\n"
                    f"**Link:** {job.get('apply_link', '')}\n\n"
                    f"## Job Description\n\n{job.get('description', '')}",
                    encoding="utf-8",
                )
        else:
            logger.info("JSON already cached at %s", json_path)

        data = json.loads(json_path.read_text(encoding="utf-8"))

        try:
            logger.info("Generating PDF from JSON")
            cv_json_to_pdf(data, pdf_path)
            logger.info("PDF generated successfully: %s", pdf_path)
        except Exception as e:
            logger.exception("PDF generation failed")
            raise TailoredCVError(f"Failed to generate PDF: {e}") from e

        return pdf_path

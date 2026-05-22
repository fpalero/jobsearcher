import logging

from fastapi import APIRouter, Query, Body, HTTPException
from fastapi.responses import FileResponse
from app.service.jobs.jobs_service import get_job_offers
from app.service.jobs.tailored_cv import generate_tailored_pdf, JobNotFoundError, TailoredCVError
from app.service.jobs.cover_letter import generate_cover_letter_pdf
from app.core.data_unified_repository import (
    set_job_saved,
    set_job_applied,
    submit_job_feedback,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/")
async def get_jobs(
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    applicable: bool | None = Query(None),
    saved: bool | None = Query(None),
    applied: bool | None = Query(None),
):
    jobs, total = get_job_offers(limit=limit, skip=skip, applicable=applicable, saved=saved, applied=applied)
    return {
        "data": jobs,
        "total": total,
        "limit": limit,
        "skip": skip,
    }


@router.post("/{job_id}/save")
async def save_job(job_id: str, saved: bool = Body(..., embed=True)):
    logger.info("POST /jobs/%s/save saved=%s", job_id, saved)
    ok = set_job_saved(job_id, saved)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"jobId": job_id, "saved": saved}


@router.post("/{job_id}/apply")
async def apply_job(job_id: str, applied: bool = Body(..., embed=True)):
    logger.info("POST /jobs/%s/apply applied=%s", job_id, applied)
    ok = set_job_applied(job_id, applied)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"jobId": job_id, "applied": applied}


@router.post("/{job_id}/feedback")
async def feedback_job(job_id: str, rating: int = Body(...), reasons: list[str] = Body(default=[])):
    logger.info("POST /jobs/%s/feedback rating=%s reasons=%s", job_id, rating, reasons)
    ok = submit_job_feedback(job_id, rating, reasons)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"jobId": job_id, "feedback": {"rating": rating, "reasons": reasons}}


@router.post("/tailored-pdf")
async def tailored_pdf(job_id: str = Body(..., embed=True)):
    logger.info("POST /jobs/tailored-pdf job_id=%s", job_id)
    try:
        pdf_path = generate_tailored_pdf(job_id)
    except JobNotFoundError as e:
        logger.warning("Job not found: %s", e)
        raise HTTPException(status_code=404, detail=str(e))
    except TailoredCVError as e:
        logger.error("TailoredCVError: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error generating tailored PDF")
        raise HTTPException(status_code=500, detail=str(e))
    filename = pdf_path.stem
    logger.info("PDF generated, returning file %s.pdf", filename)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{filename}.pdf",
    )


@router.post("/cover-letter")
async def cover_letter(job_id: str = Body(..., embed=True)):
    logger.info("POST /jobs/cover-letter job_id=%s", job_id)
    try:
        pdf_path = generate_cover_letter_pdf(job_id)
    except Exception as e:
        logger.exception("Error generating cover letter")
        raise HTTPException(status_code=500, detail=str(e))
    filename = pdf_path.stem
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{filename}.pdf",
    )

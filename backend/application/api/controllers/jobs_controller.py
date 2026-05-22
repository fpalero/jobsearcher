import logging

from fastapi import APIRouter, Query, Body, HTTPException
from fastapi.responses import FileResponse
from application.service.jobs_service import get_job_offers
from application.service.tailored_cv import generate_tailored_pdf, JobNotFoundError, TailoredCVError
from application.service.cover_letter import generate_cover_letter_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/")
async def get_jobs(
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    applicable: bool | None = Query(None),
):
    jobs, total = get_job_offers(limit=limit, skip=skip, applicable=applicable)
    return {
        "data": jobs,
        "total": total,
        "limit": limit,
        "skip": skip,
    }


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

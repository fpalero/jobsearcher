from app.core.data_unified_repository import (
    get_all_jobs,
    get_applicable_jobs,
    get_saved_jobs,
    get_applied_jobs,
    get_not_applied_jobs,
    get_total_jobs_count,
    get_jobs_counts,
)
from app.application.dtos.jobs_dto import JobDTO
from app.service.transformation.job_converter import job_dto_to_fe_response


def get_job_counts() -> dict:
    return get_jobs_counts()


def get_job_offers(limit: int = 100, skip: int = 0, applicable: bool | None = None, saved: bool | None = None, applied: bool | None = None, sources: list[str] | None = None) -> tuple[list[dict], int]:
    if saved is True:
        docs = get_saved_jobs(limit=limit, skip=skip, sources=sources)
    elif applied is True:
        docs = get_applied_jobs(limit=limit, skip=skip, sources=sources)
    elif applied is False:
        docs = get_not_applied_jobs(limit=limit, skip=skip, sources=sources)
    elif applicable is True:
        docs = get_applicable_jobs(limit=limit, skip=skip, sources=sources)
    else:
        docs = get_all_jobs(limit=limit, skip=skip, sources=sources)
    total = get_total_jobs_count(applicable=applicable if applicable is True else None, sources=sources)
    results: list[dict] = []
    for doc in docs:
        dto = JobDTO.from_mongo(doc)
        results.append(job_dto_to_fe_response(dto))
    return results, total

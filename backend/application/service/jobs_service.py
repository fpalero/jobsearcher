from core.data_unified_repository import get_all_jobs, get_applicable_jobs, get_total_jobs_count
from application.dtos.jobs_dto import JobDTO
from application.service.job_converter import job_dto_to_fe_response


def get_job_offers(limit: int = 100, skip: int = 0, applicable: bool | None = None) -> tuple[list[dict], int]:
    if applicable is True:
        docs = get_applicable_jobs(limit=limit, skip=skip)
    else:
        docs = get_all_jobs(limit=limit, skip=skip)
    total = get_total_jobs_count(applicable=applicable if applicable is True else None)
    results: list[dict] = []
    for doc in docs:
        dto = JobDTO.from_mongo(doc)
        results.append(job_dto_to_fe_response(dto))
    return results, total

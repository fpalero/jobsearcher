from app.application.dtos.jobs_dto import JobDTO


def to_job_dto(item: dict, role_query: str = "") -> JobDTO:
    detected = item.get("detected_extensions") or {}
    return JobDTO(
        job_id=item.get("job_id", ""),
        title=item.get("title") or item.get("job_title", ""),
        company=item.get("company_name"),
        description=item.get("description"),
        location=item.get("location"),
        is_remote=detected.get("work_from_home"),
        posted_at=detected.get("posted_at") or item.get("post_date"),
        employment_type=detected.get("schedule_type"),
        apply_link=item.get("share_link"),
        apply_options=item.get("apply_options"),
        publisher=item.get("via"),
        google_link=item.get("share_link"),
        source_link=item.get("source_link"),
        extensions=item.get("extensions"),
        source="SerpApi",
        role_query=role_query or item.get("_role_query", ""),
    )

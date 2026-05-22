from app.application.dtos.jobs_dto import JobDTO


def to_job_dto(item: dict, role_query: str = "") -> JobDTO:
    return JobDTO(
        job_id=item.get("job_id", ""),
        title=item.get("job_title", ""),
        company=item.get("employer_name"),
        description=item.get("job_description"),
        location=item.get("job_location"),
        country=item.get("job_country"),
        city=item.get("job_city"),
        state=item.get("job_state"),
        is_remote=item.get("job_is_remote"),
        posted_at=item.get("job_posted_at"),
        posted_at_datetime=item.get("job_posted_at_datetime_utc"),
        posted_at_timestamp=item.get("job_posted_at_timestamp"),
        salary_string=item.get("job_salary_string"),
        salary_min=item.get("job_min_salary"),
        salary_max=item.get("job_max_salary"),
        salary_period=item.get("job_salary_period"),
        employment_type=item.get("job_employment_type"),
        apply_link=item.get("job_apply_link"),
        apply_is_direct=item.get("job_apply_is_direct"),
        apply_options=item.get("apply_options"),
        publisher=item.get("job_publisher"),
        employer_logo=item.get("employer_logo"),
        employer_website=item.get("employer_website"),
        employer_reviews=item.get("employer_reviews"),
        benefits=item.get("job_benefits_strings"),
        highlights=item.get("job_highlights"),
        google_link=item.get("job_google_link"),
        latitude=_safe_float(item.get("job_latitude")),
        longitude=_safe_float(item.get("job_longitude")),
        source="JSearch",
        role_query=role_query or item.get("_role_query", ""),
    )


def _safe_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

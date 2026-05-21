from application.dtos.jobs_dto import JobDTO


def to_job_dto(item: dict, role_query: str = "") -> JobDTO:
    locations = item.get("locations_derived") or []
    countries = item.get("countries_derived") or []
    employment_types = item.get("employment_type") or []

    return JobDTO(
        job_id=str(item.get("id", "")),
        title=item.get("title", ""),
        company=item.get("organization"),
        description=item.get("description_text"),
        location=", ".join(locations) if locations else None,
        country=", ".join(countries) if countries else None,
        is_remote=item.get("remote_derived"),
        posted_at=item.get("date_posted"),
        salary_string=item.get("salary_raw"),
        employment_type=", ".join(employment_types) if employment_types else None,
        apply_link=item.get("url"),
        publisher=item.get("source_domain"),
        employer_logo=item.get("organization_logo"),
        employer_website=item.get("organization_url"),
        source="LinkedIn",
        role_query=role_query or item.get("_role_query", ""),
    )

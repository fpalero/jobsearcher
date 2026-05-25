from app.application.dtos.jobs_dto import JobDTO


def to_job_dto(item: dict, role_query: str = "") -> JobDTO:
    company = item.get("startup") or item.get("company") or {}
    if isinstance(company, dict):
        company_name = company.get("name") or company.get("company_name") or None
        company_logo = company.get("logo") or company.get("logo_url") or None
    else:
        company_name = str(company) if company else None
        company_logo = None

    return JobDTO(
        job_id=str(item.get("id") or item.get("jobId") or item.get("slug", "")),
        title=item.get("title") or item.get("primaryRoleTitle", ""),
        company=company_name,
        description=item.get("description"),
        location=item.get("location"),
        is_remote=item.get("remote") is not False,
        posted_at=item.get("date") or item.get("liveStartAt") or item.get("created_at"),
        salary_string=_format_salary(item),
        salary_min=item.get("salary_min") or item.get("minimum_salary"),
        salary_max=item.get("salary_max") or item.get("maximum_salary"),
        salary_period="yearly",
        employment_type=item.get("jobType") or item.get("employment_type"),
        apply_link=item.get("url") or item.get("apply_url"),
        employer_logo=company_logo,
        employer_website=company.get("website_url") if isinstance(company, dict) else None,
        source="StartupRemoteJobs",
        role_query=role_query or item.get("_role_query", ""),
    )


def _format_salary(item: dict) -> str | None:
    salary_min = item.get("salary_min") or item.get("minimum_salary")
    salary_max = item.get("salary_max") or item.get("maximum_salary")
    if salary_min and salary_max:
        return f"${salary_min} - ${salary_max}"
    if salary_min:
        return f"From ${salary_min}"
    if salary_max:
        return f"Up to ${salary_max}"
    return item.get("salary_raw") or item.get("salary_string")

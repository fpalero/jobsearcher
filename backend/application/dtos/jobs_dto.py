from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any


@dataclass
class JobDTO:
    job_id: str
    title: str
    company: str | None = None
    description: str | None = None
    location: str | None = None
    country: str | None = None
    city: str | None = None
    state: str | None = None
    is_remote: bool | None = None
    posted_at: str | None = None
    posted_at_datetime: str | None = None
    posted_at_timestamp: int | None = None
    salary_string: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_period: str | None = None
    employment_type: str | None = None
    apply_link: str | None = None
    apply_is_direct: bool | None = None
    apply_options: list[dict] | None = None
    publisher: str | None = None
    employer_logo: str | None = None
    employer_website: str | None = None
    employer_reviews: dict | None = None
    benefits: list[str] | None = None
    highlights: dict[str, Any] | None = None
    qualifications: list[str] | None = None
    google_link: str | None = None
    source_link: str | None = None
    extensions: list[str] | None = None
    latitude: float | None = None
    longitude: float | None = None
    source: str = ""
    role_query: str = ""
    fetched_at: datetime | None = None
    match: int | None = None
    applicable: bool | None = None
    technologies: list[str] | None = None

    @classmethod
    def from_jsearch(cls, doc: dict) -> "JobDTO":
        return cls(
            job_id=doc.get("job_id", ""),
            title=doc.get("job_title", ""),
            company=doc.get("employer_name"),
            description=doc.get("job_description"),
            location=doc.get("job_location"),
            country=doc.get("job_country"),
            city=doc.get("job_city"),
            state=doc.get("job_state"),
            is_remote=doc.get("job_is_remote"),
            posted_at=doc.get("job_posted_at"),
            posted_at_datetime=doc.get("job_posted_at_datetime_utc"),
            posted_at_timestamp=doc.get("job_posted_at_timestamp"),
            salary_string=doc.get("job_salary_string"),
            salary_min=doc.get("job_min_salary"),
            salary_max=doc.get("job_max_salary"),
            salary_period=doc.get("job_salary_period"),
            employment_type=doc.get("job_employment_type"),
            apply_link=doc.get("job_apply_link"),
            apply_is_direct=doc.get("job_apply_is_direct"),
            apply_options=doc.get("apply_options"),
            publisher=doc.get("job_publisher"),
            employer_logo=doc.get("employer_logo"),
            employer_website=doc.get("employer_website"),
            employer_reviews=doc.get("employer_reviews"),
            benefits=doc.get("job_benefits_strings"),
            highlights=doc.get("job_highlights"),
            google_link=doc.get("job_google_link"),
            latitude=_safe_float(doc.get("job_latitude")),
            longitude=_safe_float(doc.get("job_longitude")),
            source=doc.get("_source", "JSearch"),
            role_query=doc.get("_role_query", ""),
            fetched_at=doc.get("_fetched_at"),
        )

    @classmethod
    def from_serpapi(cls, doc: dict) -> "JobDTO":
        detected = doc.get("detected_extensions") or {}
        return cls(
            job_id=doc.get("job_id", ""),
            title=doc.get("title") or doc.get("job_title", ""),
            company=doc.get("company_name"),
            description=doc.get("description"),
            location=doc.get("location"),
            is_remote=detected.get("work_from_home"),
            posted_at=detected.get("posted_at") or doc.get("post_date"),
            employment_type=detected.get("schedule_type"),
            apply_link=doc.get("share_link"),
            apply_options=doc.get("apply_options"),
            publisher=doc.get("via"),
            google_link=doc.get("share_link"),
            source_link=doc.get("source_link"),
            extensions=doc.get("extensions"),
            source=doc.get("_source", "SerpApi"),
            role_query=doc.get("_role_query", ""),
            fetched_at=doc.get("_fetched_at"),
        )

    @classmethod
    def from_linkedin(cls, doc: dict) -> "JobDTO":
        locations = doc.get("locations_derived") or []
        countries = doc.get("countries_derived") or []
        employment_types = doc.get("employment_type") or []
        return cls(
            job_id=str(doc.get("id", "")),
            title=doc.get("title", ""),
            company=doc.get("organization"),
            description=doc.get("description_text"),
            location=", ".join(locations) if locations else None,
            country=", ".join(countries) if countries else None,
            is_remote=doc.get("remote_derived"),
            posted_at=doc.get("date_posted"),
            salary_string=doc.get("salary_raw"),
            employment_type=", ".join(employment_types) if employment_types else None,
            apply_link=doc.get("url"),
            publisher=doc.get("source_domain"),
            employer_logo=doc.get("organization_logo"),
            employer_website=doc.get("organization_url"),
            source=doc.get("_source", "LinkedIn"),
            role_query=doc.get("_role_query", ""),
            fetched_at=doc.get("_fetched_at"),
        )

    @classmethod
    def from_mongo(cls, doc: dict) -> "JobDTO":
        source = doc.get("_source", "")
        title = doc.get("title") or doc.get("job_title") or ""
        company = doc.get("company") or doc.get("employer_name") or doc.get("organization") or None
        if not title and not company:
            if source == "JSearch":
                return cls.from_jsearch(doc)
            elif source == "SerpApi":
                return cls.from_serpapi(doc)
            elif source == "LinkedIn":
                return cls.from_linkedin(doc)
        return cls(
            job_id=doc.get("job_id") or str(doc.get("id", "")),
            title=title,
            company=company,
            description=doc.get("description") or doc.get("job_description") or doc.get("description_text"),
            location=doc.get("location") or doc.get("job_location"),
            country=doc.get("country") or doc.get("job_country"),
            city=doc.get("city") or doc.get("job_city"),
            state=doc.get("state") or doc.get("job_state"),
            is_remote=doc.get("is_remote") or doc.get("job_is_remote"),
            posted_at=doc.get("posted_at") or doc.get("job_posted_at"),
            posted_at_datetime=doc.get("posted_at_datetime") or doc.get("job_posted_at_datetime_utc"),
            posted_at_timestamp=doc.get("posted_at_timestamp") or doc.get("job_posted_at_timestamp"),
            salary_string=doc.get("salary_string") or doc.get("job_salary_string"),
            salary_min=doc.get("salary_min") or doc.get("job_min_salary"),
            salary_max=doc.get("salary_max") or doc.get("job_max_salary"),
            salary_period=doc.get("salary_period") or doc.get("job_salary_period"),
            employment_type=doc.get("employment_type") or doc.get("job_employment_type"),
            apply_link=doc.get("apply_link") or doc.get("job_apply_link"),
            apply_is_direct=doc.get("apply_is_direct") or doc.get("job_apply_is_direct"),
            apply_options=doc.get("apply_options"),
            publisher=doc.get("publisher") or doc.get("job_publisher"),
            employer_logo=doc.get("employer_logo") or doc.get("employer_logo"),
            employer_website=doc.get("employer_website") or doc.get("employer_website"),
            employer_reviews=doc.get("employer_reviews"),
            benefits=doc.get("benefits") or doc.get("job_benefits_strings"),
            highlights=doc.get("highlights") or doc.get("job_highlights"),
            qualifications=doc.get("qualifications"),
            google_link=doc.get("google_link") or doc.get("job_google_link"),
            source_link=doc.get("source_link"),
            extensions=doc.get("extensions"),
            latitude=_safe_float(doc.get("latitude") or doc.get("job_latitude")),
            longitude=_safe_float(doc.get("longitude") or doc.get("job_longitude")),
            source=source or doc.get("source", ""),
            role_query=doc.get("_role_query") or doc.get("role_query", ""),
            fetched_at=doc.get("_fetched_at"),
            match=doc.get("match"),
            applicable=doc.get("applicable"),
            technologies=doc.get("technologies"),
        )

    def to_dict(self) -> dict:
        d = {f.name: getattr(self, f.name) for f in fields(self)}
        return {k: v for k, v in d.items() if v is not None}


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

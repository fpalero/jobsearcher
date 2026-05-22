from __future__ import annotations

from app.application.dtos.jobs_dto import JobDTO


def job_dto_to_fe_response(dto: JobDTO) -> dict:
    tags = _extract_tags(dto)
    posted_date = _format_posted_date(dto)
    feedback = _extract_feedback(dto.feedback)
    return {
        "id": hash(dto.job_id) % (10**9) if dto.job_id else 0,
        "jobId": dto.job_id or "",
        "company": dto.company or "Unknown",
        "title": dto.title or "Untitled",
        "location": dto.location or "",
        "salary": dto.salary_string or "",
        "matchPercentage": dto.match or 0,
        "logoUrl": dto.employer_logo or "",
        "description": dto.description or "",
        "applyLink": dto.apply_link or "",
        "tags": tags,
        "postedDate": posted_date,
        "applicable": dto.applicable if dto.applicable is not None else True,
        "saved": dto.saved if dto.saved is not None else False,
        "applied": dto.applied if dto.applied is not None else False,
        "responsibilities": dto.responsibilities or [],
        "requirements": dto.requirements or [],
        "feedback": feedback,
    }


def _extract_tags(dto: JobDTO) -> list[str]:
    if dto.technologies:
        return dto.technologies[:10]
    tags: list[str] = []
    if dto.extensions:
        tags.extend(dto.extensions)
    if dto.highlights:
        for vals in dto.highlights.values():
            if isinstance(vals, list):
                tags.extend(str(v) for v in vals)
    if dto.qualifications:
        tags.extend(dto.qualifications)
    if dto.benefits:
        tags.extend(dto.benefits)
    seen: set[str] = set()
    unique: list[str] = []
    for t in tags:
        t = t.strip()
        if t and t not in seen:
            seen.add(t)
            unique.append(t)
    return unique[:10]


def _format_posted_date(dto: JobDTO) -> str:
    if dto.posted_at:
        return dto.posted_at
    if dto.posted_at_datetime:
        return dto.posted_at_datetime
    return ""


def _extract_feedback(feedback: dict | None) -> 'positive' | 'negative' | None:
    if not feedback:
        return None
    rating = feedback.get("rating")
    if rating == 1:
        return "positive"
    if rating == -1:
        return "negative"
    return None

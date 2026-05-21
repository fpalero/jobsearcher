from application.extractors.jsearch.jsearch_extractor import fetch_jsearch_jobs
from application.extractors.jsearch.toJobDto import to_job_dto

QUERIES = [
    "Senior Software Engineer Java",
    "Team Lead",
    "Software Architect",
    "AI Engineer",
]

COUNTRIES = ["de", "gb", "nl", "fr", "es"]

BASE_PARAMS = {
    "page": 1,
    "num_pages": 2,
    "date_posted": "week",
    "work_from_home": True,
    "employment_types": "FULLTIME",
    "job_requirements": "more_than_3_years_experience",
}

RESOURCES = {
    "jsearch": {
        "extractor": fetch_jsearch_jobs,
        "to_job_dto": to_job_dto,
        "targets": [
            {"query": query, "params": {**BASE_PARAMS, "country": country}}
            for query in QUERIES
            for country in COUNTRIES
        ],
    },
}

from application.extractors.linkedin.linkedin_extractor import fetch_linkedin_jobs
from application.extractors.linkedin.toJobDto import to_job_dto

RESOURCES = {
    "linkedin": {
        "extractor": fetch_linkedin_jobs,
        "to_job_dto": to_job_dto,
        "targets": [
            {
                "query": "Senior Software Engineer Java",
                "params": {
                    "location_filter": "Germany OR Spain OR France OR Netherlands OR Ireland OR Belgium OR Austria OR Switzerland OR Sweden OR Denmark OR Norway OR Poland OR Portugal",
                    "employment_types": "FULL_TIME",
                    "limit": 15,
                    "endpoint": "7d",
                    "include_ai": True,
                },
            },
            {
                "query": "Team Lead",
                "params": {
                    "location_filter": "Germany OR Spain OR France OR Netherlands OR Ireland OR Belgium OR Austria OR Switzerland OR Sweden OR Denmark OR Norway OR Poland OR Portugal",
                    "employment_types": "FULL_TIME",
                    "limit": 15,
                    "endpoint": "7d",
                    "include_ai": True,
                },
            },
            {
                "query": "Software Architect",
                "params": {
                    "location_filter": "Germany OR Spain OR France OR Netherlands OR Ireland OR Belgium OR Austria OR Switzerland OR Sweden OR Denmark OR Norway OR Poland OR Portugal",
                    "employment_types": "FULL_TIME",
                    "limit": 15,
                    "endpoint": "7d",
                    "include_ai": True,
                },
            },
            {
                "query": "AI Engineer",
                "params": {
                    "location_filter": "Germany OR Spain OR France OR Netherlands OR Ireland OR Belgium OR Austria OR Switzerland OR Sweden OR Denmark OR Norway OR Poland OR Portugal",
                    "employment_types": "FULL_TIME",
                    "limit": 15,
                    "endpoint": "7d",
                    "include_ai": True,
                },
            },
        ],
    },
}

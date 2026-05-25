from app.service.extractors.startupremotejobs.startupremotejobs_extractor import fetch_startupremotejobs_jobs
from app.service.extractors.startupremotejobs.toJobDto import to_job_dto

RESOURCES = {
    "startupremotejobs": {
        "extractor": fetch_startupremotejobs_jobs,
        "to_job_dto": to_job_dto,
        "targets": [
            {
                "query": "Software Engineer",
                "params": {
                    "remote": True,
                    "jobType": "full-time",
                    "description": "Java OR Kotlin OR Spring Boot",
                },
            },
        ],
    },
}

from app.service.extractors.activejobsdb.activejobsdb_extractor import fetch_activejobsdb_jobs
from app.service.extractors.activejobsdb.toJobDto import to_job_dto

RESOURCES = {
    "activejobsdb": {
        "extractor": fetch_activejobsdb_jobs,
        "to_job_dto": to_job_dto,
        "targets": [
            {
                "query": "Senior Software Engineer Java",
                "params": {
                    "location_filter": "Germany OR France OR Netherlands OR Ireland OR Belgium OR Austria OR Switzerland OR Sweden OR Denmark OR Norway OR Poland",
                    "employment_types": "FULL_TIME",
                    "remote": True,
                    "limit": 4,
                    "include_ai": True,
                },
            },
            {
                "query": "Team Lead",
                "params": {
                    "location_filter": "Germany OR France OR Netherlands OR Ireland OR Belgium OR Austria OR Switzerland OR Sweden OR Denmark OR Norway OR Poland",
                    "employment_types": "FULL_TIME",
                    "remote": True,
                    "limit": 4,
                    "include_ai": True,
                },
            },
            {
                "query": "Software Architect",
                "params": {
                    "location_filter": "Germany OR France OR Netherlands OR Ireland OR Belgium OR Austria OR Switzerland OR Sweden OR Denmark OR Norway OR Poland",
                    "employment_types": "FULL_TIME",
                    "remote": True,
                    "limit": 4,
                    "include_ai": True,
                },
            },
            {
                "query": "AI Engineer",
                "params": {
                    "location_filter": "Germany OR France OR Netherlands OR Ireland OR Belgium OR Austria OR Switzerland OR Sweden OR Denmark OR Norway OR Poland",
                    "employment_types": "FULL_TIME",
                    "remote": True,
                    "limit": 3,
                    "include_ai": True,
                },
            },
        ],
    },
}

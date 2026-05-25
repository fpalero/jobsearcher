from datetime import datetime, timezone
from app.core.data_unified_repository import unified_jobs_collection
from app.service.extractors.data_ingestion import run_ingestion
from app.service.transformation.transformation import run_pipeline
from app.service.extractors.jsearch.jsearch_data_ingestion_config import RESOURCES as JSEARCH_RESOURCES
from app.service.extractors.linkedin.linkedin_data_ingestion_config import RESOURCES as LINKEDIN_RESOURCES
from app.service.extractors.activejobsdb.activejobsdb_data_ingestion_config import RESOURCES as ACTIVEJOBSDB_RESOURCES
from app.service.extractors.startupremotejobs.startupremotejobs_data_ingestion_config import RESOURCES as STARTUPREMOTEJOBS_RESOURCES

RESOURCES = {**JSEARCH_RESOURCES, **LINKEDIN_RESOURCES, **ACTIVEJOBSDB_RESOURCES, **STARTUPREMOTEJOBS_RESOURCES}

def get_sources():
    pipelines = [
        {
            "name": "linkedin",
            "label": "LinkedIn",
            "description": "Global Talent Network",
            "query": "software engineer germany",
            "total_records": unified_jobs_collection.count_documents({"_source": "LinkedIn"}),
            "last_sync": _get_last_sync("LinkedIn"),
            "status": "idle",
        },
        {
            "name": "jsearch",
            "label": "JSearch",
            "description": "Aggregated job listings",
            "query": "developer jobs germany",
            "total_records": unified_jobs_collection.count_documents({"_source": "JSearch"}),
            "last_sync": _get_last_sync("JSearch"),
            "status": "idle",
        },
        {
            "name": "activejobsdb",
            "label": "ActiveJobsDB",
            "description": "Real-time job database",
            "query": "software engineer germany",
            "total_records": unified_jobs_collection.count_documents({"_source": "ActiveJobsDB"}),
            "last_sync": _get_last_sync("ActiveJobsDB"),
            "status": "idle",
        },
        {
            "name": "startupremotejobs",
            "label": "StartupRemoteJobs",
            "description": "Startup & remote jobs",
            "query": "software engineer remote",
            "total_records": unified_jobs_collection.count_documents({"_source": "StartupRemoteJobs"}),
            "last_sync": _get_last_sync("StartupRemoteJobs"),
            "status": "idle",
        },
        # {
        #     "name": "serpapi",
        #     "label": "SerpApi",
        #     "description": "Google Jobs",
        #     "query": "softwareentwickler deutschland",
        #     "total_records": unified_jobs_collection.count_documents({"_source": "SerpApi"}),
        #     "last_sync": _get_last_sync("SerpApi"),
        #     "status": "idle",
        # },
    ]
    return pipelines


def trigger_sync(source_name: str) -> dict:
    valid = [p["name"] for p in get_sources()]
    if source_name not in valid:
        raise ValueError(f"Source '{source_name}' does not exist. Available: {', '.join(valid)}")

    run_ingestion(RESOURCES, [source_name])

    run_pipeline()

    return {
        "source": source_name,
        "status": "completed",
        "message": f"Sync and pipeline completed for {source_name}",
    }


def stop_sync(source_name: str) -> dict:
    return {
        "source": source_name,
        "status": "stopped",
        "message": f"Sync stopped for {source_name}",
    }


def _get_last_sync(source: str) -> str | None:
    result = (
        unified_jobs_collection.find_one(
            {"_source": source},
            sort=[("_fetched_at", -1)],
            projection={"_fetched_at": 1},
        )
    )
    if result and result.get("_fetched_at"):
        return result["_fetched_at"].isoformat()
    return None

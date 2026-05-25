import os
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

MONGO_URI = os.getenv("MONGODB_URL") or os.getenv(
    "MONGO_URI", "mongodb://midzospa:3VcdcelzsTWGNkApcA6x8PsW@localhost:27017/jobsearcher?authSource=admin"
)

client = MongoClient(MONGO_URI)
db = client["jobsearcher"]
unified_jobs_collection = db["unified_jobs"]

SOURCE_LABEL_MAP = {
    "linkedin": "LinkedIn",
    "jsearch": "JSearch",
    "activejobsdb": "ActiveJobsDB",
    "serpapi": "SerpApi",
}


def _map_sources(sources: list[str] | None) -> list[str] | None:
    if not sources:
        return None
    return [SOURCE_LABEL_MAP.get(s, s) for s in sources]


def store_unified_results(results, source, role_query):
    if not results:
        return
    docs = []
    for r in results:
        r["_source"] = source
        r["_role_query"] = role_query
        r["_fetched_at"] = datetime.now(timezone.utc)
        docs.append(r)
    try:
        unified_jobs_collection.insert_many(docs, ordered=False)
        print(f"  -> Almacenados {len(docs)} resultados de {source} en MongoDB")
    except errors.BulkWriteError as bwe:
        inserted = len(docs) - len(bwe.details.get("writeErrors", []))
        print(f"  -> Almacenados {inserted} (saltados {len(docs) - inserted} duplicados) de {source}")


def get_all_jobs(limit: int = 100, skip: int = 0, sources: list[str] | None = None) -> list[dict]:
    query = {}
    mapped = _map_sources(sources)
    if mapped:
        query["_source"] = {"$in": mapped}
    cursor = unified_jobs_collection.find(query).sort([("match", -1), ("posted_at_timestamp", -1)]).skip(skip).limit(limit)
    return list(cursor)


def get_jobs_by_query(query: str, limit: int = 100, skip: int = 0) -> list[dict]:
    cursor = (
        unified_jobs_collection.find({"$text": {"$search": query}})
        .sort("_fetched_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return list(cursor)


def get_total_jobs_count(applicable: bool | None = None, sources: list[str] | None = None) -> int:
    query = {}
    if applicable is not None:
        query["applicable"] = applicable
    mapped = _map_sources(sources)
    if mapped:
        query["_source"] = {"$in": mapped}
    return unified_jobs_collection.count_documents(query)


def get_applicable_jobs(limit: int = 100, skip: int = 0, sources: list[str] | None = None) -> list[dict]:
    query: dict = {"applicable": True}
    mapped = _map_sources(sources)
    if mapped:
        query["_source"] = {"$in": mapped}
    cursor = (
        unified_jobs_collection.find(query)
        .sort("match", -1)
        .skip(skip)
        .limit(limit)
    )
    return list(cursor)


def set_job_saved(job_id: str, saved: bool) -> bool:
    result = unified_jobs_collection.update_one(
        {"job_id": job_id},
        {"$set": {"saved": saved}},
    )
    return result.modified_count > 0 or result.matched_count > 0


def set_job_applied(job_id: str, applied: bool) -> bool:
    update = {"applied": applied}
    if applied:
        update["applied_at"] = datetime.now(timezone.utc)
    else:
        update["applied_at"] = None
    result = unified_jobs_collection.update_one(
        {"job_id": job_id},
        {"$set": update},
    )
    return result.modified_count > 0 or result.matched_count > 0


def submit_job_feedback(job_id: str, rating: int, reasons: list[str] | None = None) -> bool:
    feedback = {"rating": rating, "reasons": reasons or [], "submitted_at": datetime.now(timezone.utc)}
    result = unified_jobs_collection.update_one(
        {"job_id": job_id},
        {"$set": {"feedback": feedback}},
    )
    return result.modified_count > 0 or result.matched_count > 0


def get_saved_jobs(limit: int = 100, skip: int = 0, sources: list[str] | None = None) -> list[dict]:
    query: dict = {"saved": True}
    mapped = _map_sources(sources)
    if mapped:
        query["_source"] = {"$in": mapped}
    cursor = (
        unified_jobs_collection.find(query)
        .sort("match", -1)
        .skip(skip)
        .limit(limit)
    )
    return list(cursor)


def get_not_applied_jobs(limit: int = 100, skip: int = 0, sources: list[str] | None = None) -> list[dict]:
    query: dict = {"$or": [{"applied": False}, {"applied": {"$exists": False}}]}
    mapped = _map_sources(sources)
    if mapped:
        query["_source"] = {"$in": mapped}
    cursor = (
        unified_jobs_collection.find(query)
        .sort("match", -1)
        .skip(skip)
        .limit(limit)
    )
    return list(cursor)


def get_applied_jobs(limit: int = 100, skip: int = 0, sources: list[str] | None = None) -> list[dict]:
    query: dict = {"applied": True}
    mapped = _map_sources(sources)
    if mapped:
        query["_source"] = {"$in": mapped}
    cursor = (
        unified_jobs_collection.find(query)
        .sort("applied_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return list(cursor)

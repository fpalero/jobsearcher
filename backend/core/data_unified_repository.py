import os
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MONGO_URI = os.getenv(
    "MONGO_URI", "mongodb://admin:admin123@localhost:27017/jobsearcher?authSource=admin"
)

client = MongoClient(MONGO_URI)
db = client["jobsearcher"]
unified_jobs_collection = db["unified_jobs"]


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


def get_all_jobs(limit: int = 100, skip: int = 0) -> list[dict]:
    cursor = unified_jobs_collection.find().sort("match", -1).skip(skip).limit(limit)
    return list(cursor)


def get_jobs_by_query(query: str, limit: int = 100, skip: int = 0) -> list[dict]:
    cursor = (
        unified_jobs_collection.find({"$text": {"$search": query}})
        .sort("_fetched_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return list(cursor)


def get_total_jobs_count(applicable: bool | None = None) -> int:
    query = {}
    if applicable is not None:
        query["applicable"] = applicable
    return unified_jobs_collection.count_documents(query)


def get_applicable_jobs(limit: int = 100, skip: int = 0) -> list[dict]:
    cursor = (
        unified_jobs_collection.find({"applicable": True})
        .sort("match", -1)
        .skip(skip)
        .limit(limit)
    )
    return list(cursor)

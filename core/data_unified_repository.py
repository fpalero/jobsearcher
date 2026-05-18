import os
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

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
    unified_jobs_collection.insert_many(docs)
    print(f"  -> Almacenados {len(docs)} resultados de {source} en MongoDB")

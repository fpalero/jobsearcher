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
jobs_collection = db["jobs"]


def store_results(results, source, role_query):
    if not results:
        return
    docs = []
    for r in results:
        r["_source"] = source
        r["_role_query"] = role_query
        r["_fetched_at"] = datetime.now(timezone.utc)
        docs.append(r)
    try:
        jobs_collection.insert_many(docs, ordered=False)
        print(f"  -> Almacenados {len(docs)} resultados de {source} en MongoDB")
    except errors.BulkWriteError as bwe:
        inserted = len(docs) - len(bwe.details.get("writeErrors", []))
        print(f"  -> Almacenados {inserted} (saltados {len(docs) - inserted} duplicados) de {source}")

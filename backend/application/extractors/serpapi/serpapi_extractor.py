import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MONGO_URI = os.getenv(
    "MONGO_URI", "mongodb://admin:admin123@localhost:27017/jobsearcher?authSource=admin"
)
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")

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
    jobs_collection.insert_many(docs)
    print(f"  -> Almacenados {len(docs)} resultados de {source} en MongoDB")


def fetch_europe_remote_serpapi(role_query):
    """Busca en SerpApi (Google Jobs) forzando la geolocalización en Europa."""
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_jobs",
        "q": f"{role_query} remote in Europe",
        "google_domain": "google.com",
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }

    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        return data.get("jobs_results", [])
    except Exception as e:
        print(f"Error en SerpApi para '{role_query}': {e}")
        return []

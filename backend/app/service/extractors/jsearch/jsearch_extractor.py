import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

JSEARCH_KEY = os.getenv("JSEARCH_RAPIDAPI_KEY")

BASE_URL = "https://jsearch.p.rapidapi.com/search-v2"
HEADERS = {
    "X-RapidAPI-Key": JSEARCH_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
}

SAMPLE_PATH = Path(__file__).resolve().parent.parent.parent.parent / "resources" / "sample_jsearch_response.json"


def fetch_jsearch_jobs(
    query,
    page=1,
    num_pages=1,
    date_posted="week",
    work_from_home=None,
    employment_types=None,
    country=None,
    job_requirements=None,
    radius=None,
    location=None,
    cursor=None,
    dry_run=False,
):
    if dry_run:
        with open(SAMPLE_PATH) as f:
            data = json.load(f)
            return data.get("data", [])

    params = {
        "query": query,
        "page": str(page),
        "num_pages": str(num_pages),
        "date_posted": date_posted,
    }

    if cursor:
        params["cursor"] = cursor
    if work_from_home is not None:
        params["work_from_home"] = "true" if work_from_home else "false"
    if employment_types:
        params["employment_types"] = employment_types
    if country:
        params["country"] = country
    if job_requirements:
        params["job_requirements"] = job_requirements
    if radius is not None:
        params["radius"] = str(radius)
    if location:
        params["location"] = location

    try:
        resp = requests.get(BASE_URL, headers=HEADERS, params=params)
        data = resp.json()
        inner = data.get("data", {})
        if isinstance(inner, list):
            return inner
        return inner.get("jobs", [])
    except Exception as e:
        print(f"Error en JSearch para '{query}': {e}")
        return []


def fetch_europe_remote_jsearch(role_query):
    full_query = f"{role_query} remote in Europe"
    return fetch_jsearch_jobs(
        query=full_query,
        work_from_home=True,
        num_pages=1,
        date_posted="week",
    )

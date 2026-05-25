import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent.parent.parent / ".env")

RAPIDAPI_KEY = os.getenv("JSEARCH_RAPIDAPI_KEY")

RAPIDAPI_HOST = "active-jobs-db.p.rapidapi.com"
BASE_URL = f"https://{RAPIDAPI_HOST}/active-ats-7d"

HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST,
}

SAMPLE_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "resources" / "sample_activejobsdb_response.json"


def fetch_activejobsdb_jobs(
    title_filter,
    location_filter=None,
    remote=None,
    employment_types=None,
    limit=20,
    description_type="text",
    include_ai=None,
    dry_run=False,
):
    if dry_run:
        with open(SAMPLE_PATH) as f:
            return json.load(f)

    params = {
        "title_filter": title_filter,
        "limit": str(limit),
    }

    if location_filter:
        params["location_filter"] = location_filter
    if remote is not None:
        params["remote"] = "true" if remote else "false"
    if employment_types:
        params["type_filter"] = employment_types
    if description_type:
        params["description_type"] = description_type
    if include_ai is not None:
        params["include_ai"] = "true" if include_ai else "false"

    try:
        resp = requests.get(BASE_URL, headers=HEADERS, params=params)
        data = resp.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Error en ActiveJobsDB para '{title_filter}': {e}")
        return []

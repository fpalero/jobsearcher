import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent.parent.parent / ".env")

RAPIDAPI_KEY = os.getenv("JSEARCH_RAPIDAPI_KEY")

RAPIDAPI_HOST = "startup-remote-jobs-api.p.rapidapi.com"
BASE_URL = f"https://{RAPIDAPI_HOST}/staging/api/wellfound/jobs/"

HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST,
}

SAMPLE_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "resources" / "sample_wellfound_response.json"


def fetch_startupremotejobs_jobs(
    title=None,
    remote=None,
    primaryRoleTitle=None,
    jobType=None,
    minimum_salary=None,
    maximum_salary=None,
    description=None,
    limit=20,
    dry_run=False,
):
    if dry_run:
        with open(SAMPLE_PATH) as f:
            return json.load(f)

    params = {}

    if title:
        params["title"] = title
    if remote is not None:
        params["remote"] = "true" if remote else "false"
    if primaryRoleTitle:
        params["primaryRoleTitle"] = primaryRoleTitle
    if jobType:
        params["jobType"] = jobType
    if minimum_salary is not None:
        params["minimum_salary"] = str(minimum_salary)
    if maximum_salary is not None:
        params["maximum_salary"] = str(maximum_salary)
    if description:
        params["description"] = description

    try:
        resp = requests.get(BASE_URL, headers=HEADERS, params=params)
        if not resp.ok:
            print(f"Error en StartupRemoteJobs para '{title}': HTTP {resp.status_code} - {resp.text[:500]}")
            return []
        data = resp.json()
        print(f"[StartupRemoteJobs] Response for '{title}': HTTP {resp.status_code}, type={type(data).__name__}, preview={str(data)[:300]}")
        if isinstance(data, list):
            return data[:limit]
        if isinstance(data, dict) and "results" in data:
            return data["results"][:limit]
        print(f"[StartupRemoteJobs] Unexpected format for '{title}': {str(data)[:500]}")
        return []
    except Exception as e:
        print(f"[StartupRemoteJobs] Exception for '{title}': {e}")
        return []

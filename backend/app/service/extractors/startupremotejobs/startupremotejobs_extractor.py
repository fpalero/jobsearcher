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
        data = resp.json()
        if isinstance(data, list):
            return data[:limit]
        if isinstance(data, dict) and "results" in data:
            return data["results"][:limit]
        return []
    except Exception as e:
        print(f"Error en StartupRemoteJobs para '{title}': {e}")
        return []

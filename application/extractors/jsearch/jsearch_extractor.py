import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

JSEARCH_KEY = os.getenv("JSEARCH_RAPIDAPI_KEY")


def fetch_europe_remote_jsearch(role_query):
    """Busca en JSearch usando variaciones de ubicación europeas en la consulta."""
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": JSEARCH_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    # Se añade explícitamente la región a la consulta para el motor de JSearch
    full_query = f"{role_query} remote in Europe"

    params = {
        "query": full_query,
        "page": "1",
        "num_pages": "1",
        "remote_jobs_only": "true",  # Filtro nativo de JSearch para teletrabajo
    }

    try:
        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()
        return data.get("data", [])
    except Exception as e:
        print(f"Error en JSearch para '{role_query}': {e}")
        return []

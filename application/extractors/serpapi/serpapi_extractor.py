import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MONGO_URI = os.getenv(
    "MONGO_URI", "mongodb://midzospa:3VcdcelzsTWGNkApcA6x8PsW@localhost:27017/jobsearcher?authSource=admin"
)
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
JSEARCH_KEY = os.getenv("JSEARCH_RAPIDAPI_KEY")

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


# --- Ejecución del Pipeline ---
if __name__ == "__main__":
    # Roles optimizados para tus 12+ años de experiencia reflejados en el CV
    target_roles = [
        # # --- Foco en IA y Agentes Autónomos ---
        # "Senior AI Engineer LangChain Python",
        # "AI Agent Software Engineer LangGraph",
        # "LLM Engineer Python LlamaIndex",
        # # --- Foco Híbrido y Liderazgo ---
        # "Technical Lead Java Generative AI",
        # "Senior Java Developer AI Integration",
        # # --- Foco Full-Stack e Infraestructura ---
        # "Senior Full Stack Engineer Angular Python",
        # "Cloud AI Systems Engineer AWS Docker",
        "Senior Software Engineer Spring Boot "
    ]

    print("Iniciando búsqueda de empleo remoto en Europa...\n")

    for role in target_roles:
        # j_results = fetch_europe_remote_jsearch(role)
        s_results = fetch_europe_remote_serpapi(role)

        # store_results(j_results, "JSearch", role)
        store_results(s_results, "SerpApi", role)

        # print(
        #     f"[{role}] -> Encontrados en JSearch: {len(j_results)} | Encontrados en SerpApi: {len(s_results)}"
        # )
        print(f"[{role}] -> Encontrados en SerpApi: {len(s_results)}")

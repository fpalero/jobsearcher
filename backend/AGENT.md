# Backend — JobSearcher API (FastAPI + Python 3.14)

API REST construida con FastAPI que alimenta al frontend TalentMatch. Ejecuta un pipeline ETL que ingesta ofertas de empleo de múltiples fuentes, las enriquece con LLM (aplicabilidad, tecnologías, match) y las expone vía endpoints. Corre en el puerto **8000** (interno) / **8500** (expuesto vía Docker).

## Estructura del proyecto

```
backend/
├── pyproject.toml              # Dependencias y scripts (uv)
├── uv.lock                     # Lockfile de dependencias
├── Dockerfile                  # Imagen Python 3.14-slim con deps del sistema
├── run_weekly.sh               # Script semanal: ingestión + pipeline de transformación
├── run_full_pipeline.py        # Pipeline completo en loop hasta procesar todo
├── top10.py                    # Utilidad: muestra top 10 ofertas por match score
│
├── resources/
│   ├── CV.md                   # CV del candidato en Markdown (referencia para match)
│   ├── resume-tips-for-engineering-majors.pdf  # Fuente para RAG en tailored CV
│   ├── sample_jsearch_response.json   # Fixture de prueba JSearch
│   ├── sample_linkedin_response.json  # Fixture de prueba LinkedIn
│   ├── chroma_db/              # Vector store para RAG
│   ├── pdf/
│   │   └── ats_style.css       # Estilos CSS para PDFs ATS
│   └── prompts/                # Prompts LLM (antes docs/)
│       ├── ats-prompt.md       # Prompt LLM para generación de CV adaptado
│       ├── cover-letter-prompt.md  # Prompt LLM para generación de cover letter
│       └── prompt.md           # Documento de referencia para extracción y match
│
└── app/                        # Código fuente principal
    ├── main.py                 # Entry point: arranca uvicorn en 0.0.0.0:8000
    │
    ├── application/
    │   ├── api/
    │   │   ├── main.py         # App FastAPI, registra routers /jobs y /sources
    │   │   └── controllers/
    │   │       ├── jobs_controller.py    # 7 endpoints REST de ofertas
    │   │       └── sources_controller.py # Endpoints de gestión de fuentes
    │   ├── extractors/
    │   │   ├── data_ingestion.py   # Orquestador: recorre fuentes, extrae, guarda en Mongo
    │   │   ├── jsearch/            # Extractor RapidAPI JSearch (Google for Jobs)
    │   │   ├── linkedin/           # Extractor RapidAPI LinkedIn Job Search
    │   │   └── serpapi/            # Extractor SerpApi (Google Jobs)
    │   ├── dtos/
    │   │   └── jobs_dto.py     # Dataclass JobDTO con factories por fuente
    │   └── cron/
    │       ├── jsearch_cron.sh     # Dispara ingestión JSearch
    │       └── linkedin_cron.sh    # Dispara ingestión LinkedIn
    │
    ├── service/                # Servicios de negocio (al mismo nivel que application/)
    │   ├── jobs_service.py     # Recupera ofertas de Mongo con filtros y paginación
    │   ├── applicable_service.py   # ETL Paso 1: LLM decide si la oferta es aplicable
    │   ├── technology_service.py   # ETL Paso 2: LLM extrae tecnologías del texto
    │   ├── match_service.py        # ETL Paso 3: Calcula match contra el CV del candidato
    │   ├── transformation.py       # Orquestador del pipeline de 3 pasos
    │   ├── tailored_cv.py          # Genera CV PDF adaptado (LLM + RAG + Typst)
    │   ├── cover_letter.py         # Genera cover letter PDF (LLM + Typst)
    │   ├── sources_service.py      # CRUD de fuentes de extracción
    │   ├── job_converter.py        # Convierte JobDTO → respuesta frontend
    │   └── llm_config.py           # Fábrica de cliente LLM (ChatOpenAI → OpenCode API)
    │
    ├── core/
    │   ├── data_unified_repository.py  # Acceso a colección unified_jobs (MongoDB)
    │   └── extractor_repository.py     # Acceso a colección jobs (datos raw)
    │
    ├── scripts/
    │   ├── md_to_ats_pdf.py        # Convierte Markdown → PDF formateado ATS (Typst/cmarker)
    │   ├── ensure_indexes.py       # Crea índices únicos y limpia duplicados en Mongo
    │   ├── migrate_application_folders.py  # Migración de estructura de carpetas
    │   └── update_match_applicable.py      # Batch update de campos match/applicable
    │
    └── test/
        ├── test_transformation.py      # Tests del pipeline de transformación
        └── test_linkedin_ingestion.py  # Tests de ingestión LinkedIn
```

## API Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/jobs/` | Lista ofertas (paginación, filtros: applicable, saved, applied) |
| `POST` | `/jobs/{job_id}/save` | Marcar/desmarcar como guardada |
| `POST` | `/jobs/{job_id}/apply` | Marcar/desmarcar como aplicada |
| `POST` | `/jobs/{job_id}/feedback` | Enviar feedback (rating + razones) |
| `POST` | `/jobs/tailored-pdf` | Generar CV PDF adaptado a la oferta |
| `POST` | `/jobs/cover-letter` | Generar cover letter PDF |
| `GET` | `/sources/` | Listar fuentes de extracción |
| `POST` | `/sources/{source_name}/sync` | Iniciar sincronización de una fuente |
| `POST` | `/sources/{source_name}/stop` | Detener sincronización de una fuente |

## Pipeline ETL

El pipeline se ejecuta en dos fases:

### Fase A: Extracción (Data Ingestion)
1. **JSearch** — RapidAPI, 4 roles × 5 países (de, gb, nl, fr, es), remote, full-time
2. **LinkedIn** — RapidAPI, 4 roles × 13 países europeos, full-time
3. **SerpApi** — Google Jobs, "remote in Europe"
4. Datos raw → colección `jobs` → normalizados a `JobDTO` → colección `unified_jobs`

### Fase B: Transformación (3 pasos, idempotentes)
1. **ApplicableService** — LLM decide si la oferta aplica (remoto/Alemania + inglés)
2. **TechnologyService** — LLM extrae array de tecnologías del título y descripción
3. **MatchService** — Algoritmo determinístico: compara tecnologías extraídas contra skills del CV

## Stack técnico

- **Framework:** FastAPI + Uvicorn
- **Base de datos:** MongoDB (driver: pymongo)
- **LLM:** LangChain + ChatOpenAI → OpenCode Go API (`deepseek-v4-flash`)
- **RAG:** ChromaDB + HuggingFace embeddings (`all-MiniLM-L6-v2`)
- **PDF:** Typst/cmarker (Markdown → PDF) + WeasyPrint (HTML → PDF)
- **Gestor de paquetes:** uv

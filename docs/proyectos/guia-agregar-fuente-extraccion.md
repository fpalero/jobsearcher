---
tags:
  - "#proyecto"
  - "#estado/activo"
  - "#prioridad/media"
  - "#tema/arquitectura"
  - "#tema/extractor"
fecha: 2026-05-25
---

# Guía para Agregar una Nueva Fuente de Extracción

## Visión General

Cada fuente de extracción (JSearch, LinkedIn, SerpApi) sigue el mismo patrón arquitectónico: **función extractora + función convertidora + configuración de targets**. No hay clases ni registros formales — todo se conecta mediante un diccionario `RESOURCES` y una función orquestadora.

## Estructura del extractor

Cada fuente vive en su propia carpeta bajo `backend/app/service/extractors/<nombre>/` con tres archivos obligatorios:

```
extractors/<nombre>/
├── __init__.py                          # Archivo vacío
├── <nombre>_extractor.py                # Función que llama a la API externa
├── toJobDto.py                          # Convierte raw → JobDTO
└── <nombre>_data_ingestion_config.py    # Configuración: extractor, converter, targets
```

Además, opcionalmente se puede agregar un fixture de prueba en `backend/resources/sample_<nombre>_response.json`.

## Paso a paso

### 1. Crear el extractor

**Archivo:** `backend/app/service/extractors/<nombre>/<nombre>_extractor.py`

- Define la(s) URL(s) base de la API y los headers con la API key desde variable de entorno
- Implementa una función que recibe parámetros de búsqueda y retorna `list[dict]`
- Soporta `dry_run=True` para pruebas sin llamar a la API real (carga un JSON local)
- Maneja errores con try/except y retorna lista vacía en caso de fallo

**Referencias:**
- [[backend/app/service/extractors/linkedin/linkedin_extractor.py]]
- [[backend/app/service/extractors/jsearch/jsearch_extractor.py]]

### 2. Crear el conversor a JobDTO

**Archivo:** `backend/app/service/extractors/<nombre>/toJobDto.py`

- Implementa `to_job_dto(item: dict, role_query: str = "") -> JobDTO`
- Mapea los campos del JSON de la API a los campos del `JobDTO`
- Establece `source="<NombreFuente>"` (ej: `"ActiveJobsDB"`)
- Los campos no disponibles se dejan como `None`

**Referencias:**
- [[backend/app/service/extractors/linkedin/toJobDto.py]]
- [[backend/app/service/extractors/jsearch/toJobDto.py]]
- [[backend/app/application/dtos/jobs_dto.py]] — Definición de JobDTO

### 3. Crear la configuración de targets

**Archivo:** `backend/app/service/extractors/<nombre>/<nombre>_data_ingestion_config.py`

- Importa la función extractora y la función convertidora
- Define `RESOURCES = {"<nombre>": {"extractor": <func>, "to_job_dto": <func>, "targets": [...]}}`
- Cada target tiene un `"query"` (término de búsqueda) y `"params"` (dict con argumentos para la función extractora)

**Referencias:**
- [[backend/app/service/extractors/linkedin/linkedin_data_ingestion_config.py]]
- [[backend/app/service/extractors/jsearch/jsearch_data_ingestion_config.py]]

### 4. Registrar el source label en el orquestador

**Archivo:** `backend/app/service/extractors/data_ingestion.py` — línea 24

Agrega la entrada al diccionario `source_label`:

```python
source_label = {
    "linkedin": "LinkedIn",
    "jsearch": "JSearch",
    "<nombre>": "<NombreFuente>",
}.get(source.lower(), source.capitalize())
```

### 5. Registrar la fuente en el servicio de sources

**Archivo:** `backend/app/service/sources/sources_service.py`

- Importar el `RESOURCES` del nuevo config y fusionarlo con el existente
- Agregar un nuevo entry en `get_sources()` con los metadatos de la fuente (`name`, `label`, `description`, `query`)

**Referencia:**
- [[backend/app/service/sources/sources_service.py]]

### 6. Agregar icono en el frontend (opcional)

**Archivo:** `frontend/src/app/pages/sources/sources.component.html` — línea 29

Agrega un case para el `name` de la nueva fuente en el switch de iconos:

```html
<span class="material-symbols-outlined ...">
  {{ source.name === 'linkedin' ? 'business_center' :
     source.name === 'jsearch' ? 'travel_explore' :
     source.name === '<nombre>' ? '<icono>' : 'public' }}
</span>
```

### 7. Agregar fixture de prueba (opcional)

Si se desea soporte para `dry_run=True`, colocar un JSON de respuesta sample en:

```
backend/resources/sample_<nombre>_response.json
```

## Archivos que NO requieren cambios

El resto del sistema es genérico y no necesita modificaciones:

- `frontend/src/app/services/source.service.ts` — LLama a `/api/sources/` sin importar cuántas fuentes existan
- `frontend/src/app/models/source.model.ts` — Modelo genérico con `name`, `label`, `description`, etc.
- `backend/app/application/api/controllers/sources_controller.py` — Endpoints genéricos por `{source_name}`
- `backend/app/core/extractor_repository.py` — Almacena datos raw en colección `jobs`
- `backend/app/core/data_unified_repository.py` — Almacena datos normalizados en `unified_jobs`
- `backend/app/application/dtos/jobs_dto.py` — JobDTO ya cubre todos los campos necesarios; no necesita nuevos factories

## Resumen visual

```
extractors/<nombre>/
├── __init__.py                              ← Crear (vació­o)
├── <nombre>_extractor.py                    ← Crear
├── toJobDto.py                              ← Crear
└── <nombre>_data_ingestion_config.py        ← Crear

data_ingestion.py                            ← Modificar (source_label)
sources_service.py                           ← Modificar (import + get_sources)
sources.component.html                       ← Modificar (icono)
```

## 🔗 Relacionado

- [[jobsearcher-arquitectura]] — Arquitectura general del sistema
- [[backend/AGENT.md]] — Documentación del backend
- [[frontend/AGENT.md]] — Documentación del frontend

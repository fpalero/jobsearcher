# DevOps — Infraestructura Docker

Directorio que contiene la configuración de infraestructura para desplegar la plataforma JobSearcher usando Docker Compose. Orquesta 3 servicios (MongoDB, Backend, Frontend) en una red interna compartida.

## Estructura del proyecto

```
devops/
├── docker-compose.yml    # Orquestación de 3 servicios + volúmenes + healthchecks
├── .env                  # Variables de entorno centralizadas (puertos, credenciales, URLs)
├── backend/              # Mount point vacío para el código del backend en runtime
│   └── .venv/            # Mount point para el virtualenv de Python
└── frontend/             # Mount point vacío para el código del frontend en runtime
    └── node_modules/     # Mount point para dependencias de Node
```

## Servicios definidos en docker-compose.yml

| Servicio | Imagen/Build | Puerto interno | Puerto expuesto | Descripción |
|---|---|---|---|---|
| **mongodb** | `mongo:7` (Docker Hub) | 27017 | 27017 | Base de datos MongoDB 7 con volumen persistente `mongo_data` |
| **backend** | `../backend/Dockerfile` | 8000 | 8500 | API FastAPI con hot-reload (código montado como volumen) |
| **frontend** | `../frontend/Dockerfile` | 4200 | 8501 | Angular dev server con proxy a backend |

## Dependencias entre servicios

```
mongodb (healthy) → backend (depends_on mongodb) → frontend (depends_on backend)
```

- **mongodb** tiene healthcheck vía `mongosh --eval "db.adminCommand('ping')"`
- **backend** tiene healthcheck vía `curl http://localhost:8000/health`
- **frontend** espera a que backend esté healthy antes de arrancar

## Variables de entorno (.env)

| Variable | Valor por defecto | Uso |
|---|---|---|
| `MONGO_ROOT_USER` / `MONGO_ROOT_PASS` | credenciales admin | Autenticación MongoDB |
| `MONGO_DATABASE` | `jobsearcher` | Base de datos principal |
| `MONGO_HOST` | `mongodb` | Hostname interno en la red Docker |
| `MONGO_PORT` | `27017` | Puerto interno MongoDB |
| `BACKEND_EXTERNAL_PORT` | `8500` | Puerto host para la API |
| `FRONTEND_EXTERNAL_PORT` | `8501` | Puerto host para el frontend |
| `API_URL` | `http://backend:8000` | URL que el frontend usa para llegar al backend |
| `MONGODB_URL` | `mongodb://...` | Connection string completo para el backend |
| `JSEARCH_RAPIDAPI_KEY` | (requerido) | API key para el extractor JSearch |
| `OPENCODE_GO_API_KEY` | (requerido) | API key para el servicio LLM |
| `SERPAPI_API_KEY` | (requerido) | API key para el extractor SerpApi |

## Volúmenes

| Volumen/Mount | Tipo | Propósito |
|---|---|---|
| `mongo_data` | Volumen nombrado | Persistencia de datos MongoDB |
| `./backend:/app` | Bind mount | Código del backend con hot-reload |
| `./backend/.venv:/app/.venv` | Bind mount | Virtualenv de Python (aislado del host) |
| `./frontend:/app` | Bind mount | Código del frontend con hot-reload |
| `/app/node_modules` | Volumen anónimo | node_modules dentro del contenedor |

## Comandos útiles

```bash
# Levantar todos los servicios
docker compose -f devops/docker-compose.yml up -d

# Ver logs
docker compose -f devops/docker-compose.yml logs -f

# Reconstruir imágenes
docker compose -f devops/docker-compose.yml build --no-cache

# Detener todo
docker compose -f devops/docker-compose.yml down

# Detener y eliminar volúmenes (pérdida de datos Mongo)
docker compose -f devops/docker-compose.yml down -v
```

## Notas

- Los directorios `backend/` y `frontend/` dentro de `devops/` existen solo como mount points. El código fuente real está en `../backend/` y `../frontend/`.
- MongoDB expone el puerto 27017 al host para permitir conexiones directas con herramientas como MongoDB Compass o `mongosh`.
- El backend usa `python main.py` como entrypoint (no un servidor WSGI separado; uvicorn se ejecuta programáticamente).

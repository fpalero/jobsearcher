import logging

from fastapi import FastAPI
from application.api.controllers.jobs_controller import router as jobs_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="JobSearcher API", version="0.1.0")

app.include_router(jobs_router)


@app.get("/health")
async def health():
    return {"status": "ok"}

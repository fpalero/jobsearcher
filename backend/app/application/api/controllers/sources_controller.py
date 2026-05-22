import logging

from fastapi import APIRouter, HTTPException
from app.service.sources.sources_service import get_sources, trigger_sync, stop_sync

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/")
async def list_sources():
    return {"data": get_sources()}


@router.post("/{source_name}/sync")
async def start_source_sync(source_name: str):
    logger.info("POST /sources/%s/sync", source_name)
    try:
        result = trigger_sync(source_name)
    except Exception as e:
        logger.exception("Error triggering sync for %s", source_name)
        raise HTTPException(status_code=500, detail=str(e))
    return result


@router.post("/{source_name}/stop")
async def stop_source_sync(source_name: str):
    logger.info("POST /sources/%s/stop", source_name)
    try:
        result = stop_sync(source_name)
    except Exception as e:
        logger.exception("Error stopping sync for %s", source_name)
        raise HTTPException(status_code=500, detail=str(e))
    return result

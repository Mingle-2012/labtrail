"""LabTrail - AI Research Knowledge & Experiment Workspace - Main Application"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_URL
from app.api.projects import router as projects_router
from app.api.documents import router as documents_router
from app.api.experiments import router as experiments_router
from app.api.memory import router as memory_router
from app.api.reports import router as reports_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("LabTrail backend starting...")
    try:
        from app.seekdb_service import get_client
        get_client()
        logger.info("seekdb initialized successfully")
    except Exception as e:
        logger.error("seekdb initialization failed: %s", e)
    try:
        from app.embedding_service import embed_texts
        embed_texts(["warmup"])
        logger.info("Embedding model loaded")
    except Exception as e:
        logger.error("Embedding model initialization failed: %s", e)
    from app.powercontext_service import powercontext_health
    pc_status = powercontext_health()
    if pc_status["status"] == "ready":
        logger.info("PowerContext connected at %s", pc_status["url"])
    else:
        logger.warning("PowerContext unavailable at %s: %s", pc_status["url"], pc_status.get("error", ""))
    logger.info("LabTrail backend ready")
    yield
    logger.info("LabTrail backend shutting down")


app = FastAPI(
    title="LabTrail",
    description="AI Research Knowledge & Experiment Workspace",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)
app.include_router(documents_router)
app.include_router(experiments_router)
app.include_router(memory_router)
app.include_router(reports_router)


@app.get("/api/health")
def health_check():
    status = {"status": "ok", "services": {}}
    try:
        from app.seekdb_service import get_client
        get_client()
        status["services"]["seekdb"] = "connected"
    except Exception as e:
        status["services"]["seekdb"] = f"error: {e}"
    from app.powercontext_service import powercontext_health
    pc_status = powercontext_health()
    status["services"]["powercontext"] = pc_status["status"]
    if pc_status["status"] != "ready":
        status["status"] = "degraded"
        status["services"]["powercontext_detail"] = pc_status
    return status


@app.get("/")
def root():
    return {"name": "LabTrail", "version": "1.0.0", "description": "AI Research Knowledge & Experiment Workspace"}

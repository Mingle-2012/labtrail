"""API routes for PowerContext research memory management."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.powercontext_service import (
    save_research_memory, search_research_memories,
    get_project_memories, delete_memory, get_research_context,
)

router = APIRouter(prefix="/api/memory", tags=["memory"])


class SaveMemoryRequest(BaseModel):
    project_id: str
    content: str
    memory_type: str = "conclusion"  # conclusion, decision, plan, failure, general
    tags: list[str] | None = None


class SearchMemoryRequest(BaseModel):
    project_id: str
    query: str
    n_results: int = 10


@router.post("")
def save_memory_api(req: SaveMemoryRequest):
    result = save_research_memory(
        req.project_id, req.content, req.memory_type, req.tags,
    )
    return result


@router.get("/{project_id}")
def list_memories_api(project_id: str, memory_type: str | None = None):
    return get_project_memories(project_id, memory_type)


@router.post("/search")
def search_memory_api(req: SearchMemoryRequest):
    results = search_research_memories(req.project_id, req.query, req.n_results)
    return {"results": results, "count": len(results)}


@router.get("/{project_id}/context")
def get_context_api(project_id: str):
    context = get_research_context(project_id)
    return {"project_id": project_id, "context": context}


@router.delete("/{project_id}/{memory_id}")
def delete_memory_api(project_id: str, memory_id: str):
    success = delete_memory(project_id, memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "deleted"}

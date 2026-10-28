"""API routes for project management."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.project_service import (
    create_project, get_project, list_projects, update_project, delete_project,
    get_dashboard_stats,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str
    description: str = ""
    research_direction: str = ""
    goal: str = ""


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    research_direction: Optional[str] = None
    goal: Optional[str] = None
    conclusions: Optional[list[str]] = None
    tasks: Optional[list[dict]] = None


@router.post("")
def create_project_api(req: CreateProjectRequest):
    return create_project(req.name, req.description, req.research_direction, req.goal)


@router.get("")
def list_projects_api():
    return list_projects()


@router.get("/{project_id}")
def get_project_api(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}")
def update_project_api(project_id: str, req: UpdateProjectRequest):
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    project = update_project(project_id, updates)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
def delete_project_api(project_id: str):
    if not delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "deleted"}


@router.get("/{project_id}/dashboard")
def dashboard_api(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    stats = get_dashboard_stats(project_id)
    stats["project"] = project
    return stats

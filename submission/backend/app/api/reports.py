"""API routes for weekly report generation."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.reports.generator import generate_weekly_report
from app.project_service import get_project, get_dashboard_stats
from app.experiments.service import analyze_experiments
from app.project_service import get_experiment_records

router = APIRouter(prefix="/api/reports", tags=["reports"])


class GenerateReportRequest(BaseModel):
    project_id: str
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str | None = None


@router.post("/weekly")
def generate_report_api(req: GenerateReportRequest):
    project = get_project(req.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    records = get_experiment_records(req.project_id)
    experiment_data = analyze_experiments(records) if records else None
    recent_activities = project.get("recent_activities", [])
    tasks = project.get("tasks", [])

    report = generate_weekly_report(
        project_id=req.project_id,
        project_name=project["name"],
        experiment_data=experiment_data,
        recent_activities=recent_activities,
        tasks=tasks,
        llm_api_key=req.llm_api_key,
        llm_base_url=req.llm_base_url,
        llm_model=req.llm_model,
    )
    return {"report": report, "project_name": project["name"]}

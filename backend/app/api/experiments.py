"""API routes for experiment data management and analysis."""
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Query
from pydantic import BaseModel

from app.config import UPLOAD_DIR
from app.experiments.service import (
    parse_experiment_csv, parse_wide_format_csv, analyze_experiments, get_recall_qps_data,
)
from app.project_service import (
    add_experiment_records, get_experiment_records, clear_experiment_records, get_project,
)

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


@router.post("/upload")
async def upload_experiment_csv(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    wide_format: bool = Form(False),
):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    ext = Path(file.filename).suffix.lower()
    if ext != ".csv":
        raise HTTPException(status_code=400, detail="Only CSV files are supported for experiment data")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    file_id = uuid.uuid4().hex[:12]
    upload_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    upload_path.write_bytes(content)

    try:
        if wide_format:
            records = parse_wide_format_csv(str(upload_path), project_id)
        else:
            records = parse_experiment_csv(str(upload_path), project_id)

        if not records:
            raise HTTPException(status_code=400, detail="No valid experiment records found in CSV")

        count = add_experiment_records(project_id, records)
        return {
            "file_name": file.filename,
            "records_imported": count,
            "methods": sorted(set(r["method"] for r in records)),
            "datasets": sorted(set(r["dataset"] for r in records)),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")


@router.get("/{project_id}")
def list_experiments_api(
    project_id: str,
    method: str | None = None,
    dataset: str | None = None,
    metric: str | None = None,
):
    records = get_experiment_records(project_id)
    analysis = analyze_experiments(records, filter_method=method, filter_dataset=dataset, filter_metric=metric)
    return analysis


@router.get("/{project_id}/recall-qps")
def recall_qps_api(project_id: str):
    records = get_experiment_records(project_id)
    return get_recall_qps_data(records)


@router.get("/{project_id}/summary")
def experiment_summary_api(project_id: str):
    records = get_experiment_records(project_id)
    return analyze_experiments(records)


@router.delete("/{project_id}")
def clear_experiments_api(project_id: str):
    count = clear_experiment_records(project_id)
    return {"deleted": count}

"""Project management service - stores projects, documents, and experiments metadata."""
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import DATA_DIR

logger = logging.getLogger(__name__)

PROJECTS_FILE = DATA_DIR / "projects.json"
DOCUMENTS_FILE = DATA_DIR / "documents.json"
EXPERIMENTS_FILE = DATA_DIR / "experiments.json"


def _load_json(path: Path, default: Any = None) -> Any:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default if default is not None else {}


def _save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def create_project(name: str, description: str = "", research_direction: str = "", goal: str = "") -> dict:
    projects = _load_json(PROJECTS_FILE, {})
    project_id = uuid.uuid4().hex[:12]
    now = datetime.now().isoformat()
    project = {
        "id": project_id,
        "name": name,
        "description": description,
        "research_direction": research_direction,
        "goal": goal,
        "created_at": now,
        "updated_at": now,
        "conclusions": [],
        "tasks": [],
        "recent_activities": [],
    }
    projects[project_id] = project
    _save_json(PROJECTS_FILE, projects)
    return project


def get_project(project_id: str) -> dict | None:
    projects = _load_json(PROJECTS_FILE, {})
    return projects.get(project_id)


def list_projects() -> list[dict]:
    projects = _load_json(PROJECTS_FILE, {})
    return sorted(projects.values(), key=lambda p: p.get("updated_at", ""), reverse=True)


def update_project(project_id: str, updates: dict) -> dict | None:
    projects = _load_json(PROJECTS_FILE, {})
    if project_id not in projects:
        return None
    projects[project_id].update(updates)
    projects[project_id]["updated_at"] = datetime.now().isoformat()
    _save_json(PROJECTS_FILE, projects)
    return projects[project_id]


def delete_project(project_id: str) -> bool:
    projects = _load_json(PROJECTS_FILE, {})
    if project_id in projects:
        del projects[project_id]
        _save_json(PROJECTS_FILE, projects)
        return True
    return False


def add_document_record(project_id: str, doc_name: str, doc_type: str, file_path: str, chunk_count: int) -> dict:
    documents = _load_json(DOCUMENTS_FILE, {})
    project_docs = documents.get(project_id, {})
    doc_id = uuid.uuid4().hex[:12]
    now = datetime.now().isoformat()
    record = {
        "id": doc_id,
        "project_id": project_id,
        "name": doc_name,
        "type": doc_type,
        "file_path": file_path,
        "chunk_count": chunk_count,
        "created_at": now,
    }
    project_docs[doc_id] = record
    documents[project_id] = project_docs
    _save_json(DOCUMENTS_FILE, documents)

    project = get_project(project_id)
    if project:
        activities = project.get("recent_activities", [])
        activities.insert(0, {"type": "document", "name": doc_name, "date": now, "doc_id": doc_id})
        update_project(project_id, {"recent_activities": activities[:50]})

    return record


def list_documents(project_id: str) -> list[dict]:
    documents = _load_json(DOCUMENTS_FILE, {})
    project_docs = documents.get(project_id, {})
    return sorted(project_docs.values(), key=lambda d: d.get("created_at", ""), reverse=True)


def delete_document_record(project_id: str, doc_id: str) -> bool:
    documents = _load_json(DOCUMENTS_FILE, {})
    project_docs = documents.get(project_id, {})
    if doc_id in project_docs:
        del project_docs[doc_id]
        documents[project_id] = project_docs
        _save_json(DOCUMENTS_FILE, documents)
        return True
    return False


def add_experiment_records(project_id: str, records: list[dict]) -> int:
    experiments = _load_json(EXPERIMENTS_FILE, {})
    project_exps = experiments.get(project_id, [])
    for r in records:
        r["id"] = uuid.uuid4().hex[:12]
        r["created_at"] = datetime.now().isoformat()
    project_exps.extend(records)
    experiments[project_id] = project_exps
    _save_json(EXPERIMENTS_FILE, experiments)
    return len(records)


def get_experiment_records(project_id: str) -> list[dict]:
    experiments = _load_json(EXPERIMENTS_FILE, {})
    return experiments.get(project_id, [])


def clear_experiment_records(project_id: str) -> int:
    experiments = _load_json(EXPERIMENTS_FILE, {})
    count = len(experiments.get(project_id, []))
    experiments[project_id] = []
    _save_json(EXPERIMENTS_FILE, experiments)
    return count


def get_dashboard_stats(project_id: str) -> dict:
    from app.seekdb_service import get_document_count, get_chunk_count
    documents = list_documents(project_id)
    experiments = get_experiment_records(project_id)
    doc_count = get_document_count(project_id)
    chunk_count = get_chunk_count(project_id)

    return {
        "total_documents": len(documents),
        "total_chunks": chunk_count,
        "total_experiments": len(experiments),
        "methods": sorted(set(r.get("method", "") for r in experiments if r.get("method"))),
        "datasets": sorted(set(r.get("dataset", "") for r in experiments if r.get("dataset"))),
        "recent_activities": get_project(project_id).get("recent_activities", [])[:10] if get_project(project_id) else [],
    }

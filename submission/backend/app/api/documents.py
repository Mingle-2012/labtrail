"""API routes for document management and search."""
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Body
from pydantic import BaseModel

from app.config import UPLOAD_DIR
from app.ingestion.parser import parse_file, SUPPORTED_EXTENSIONS
from app.seekdb_service import (
    add_document_chunks, search_documents, hybrid_search,
    delete_document_chunks,
)
from app.project_service import (
    add_document_record, list_documents, delete_document_record, get_project,
)

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    project_id: str = Form(...),
    file: UploadFile = File(...),
):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    max_size = 50 * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    doc_id = uuid.uuid4().hex[:12]
    upload_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
    upload_path.write_bytes(content)

    try:
        chunks = parse_file(str(upload_path), file.filename)
        if not chunks:
            upload_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="No content could be extracted from file")

        chunk_ids = add_document_chunks(project_id, doc_id, chunks)
        record = add_document_record(project_id, file.filename, ext, str(upload_path), len(chunk_ids))
        return {
            "doc_id": doc_id,
            "file_name": file.filename,
            "chunks": len(chunk_ids),
            "record": record,
        }
    except HTTPException:
        raise
    except Exception as e:
        upload_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.get("/{project_id}")
def list_documents_api(project_id: str):
    return list_documents(project_id)


@router.delete("/{project_id}/{doc_id}")
def delete_document_api(project_id: str, doc_id: str):
    deleted_chunks = delete_document_chunks(project_id, doc_id)
    deleted_record = delete_document_record(project_id, doc_id)
    return {
        "deleted_chunks": deleted_chunks,
        "deleted_record": deleted_record,
    }


class SearchRequest(BaseModel):
    query: str
    n_results: int = 10
    mode: str = "hybrid"
    where: dict | None = None


@router.post("/search")
def search_documents_api(
    project_id: str,
    req: SearchRequest = Body(...),
):
    if req.mode == "vector":
        results = search_documents(project_id, req.query, req.n_results, req.where)
    elif req.mode == "hybrid":
        results = hybrid_search(project_id, req.query, req.n_results, req.where)
    else:
        results = search_documents(project_id, req.query, req.n_results, req.where)
    return {"results": results, "count": len(results), "mode": req.mode}

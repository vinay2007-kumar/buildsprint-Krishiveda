"""Scheme RAG router: upload PDF + query."""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.config import settings
from backend.schemas import SchemeQueryRequest, SchemeQueryResponse
from backend.services import rag_service

router = APIRouter()


@router.post("/upload")
async def upload(file: UploadFile = File(...), title: str = Form("Scheme Document")):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files allowed.")
    data = await file.read()
    if len(data) > settings.MAX_FILE_SIZE:
        raise HTTPException(400, "PDF too large (max 10 MB).")
    doc_id = str(uuid.uuid4())[:8]
    save_dir = os.path.join(settings.UPLOAD_DIR, "schemes")
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"{doc_id}_{file.filename}")
    with open(path, "wb") as f:
        f.write(data)
    text = rag_service.extract_pdf_text(path)
    if len(text.strip()) < 50:
        raise HTTPException(400, "Could not extract text from PDF (scanned image?). Try a text PDF.")
    info = rag_service.ingest_document(doc_id, title, text, {"path": path})
    return {"success": True, "message": "Scheme uploaded and indexed.",
            "data": {"doc_id": doc_id, "title": title, "chunks": info["chunks"]}}


@router.post("/query", response_model=SchemeQueryResponse)
async def query(req: SchemeQueryRequest):
    lang = req.language.value if hasattr(req.language, "value") else str(req.language)
    res = rag_service.query(str(req.document_id), req.question)
    return SchemeQueryResponse(question=req.question, answer=res["answer"],
                               source_chunks=res["source_chunks"],
                               confidence=res["confidence"], language=lang)


@router.get("/list")
async def list_docs():
    from backend.services.rag_service import _STORE
    return {"success": True, "data": [
        {"doc_id": k, "title": v["title"], "chunks": len(v["chunks"])} for k, v in _STORE.items()]}


@router.get("/catalog")
async def scheme_catalog(category: str = ""):
    """Return the built-in catalog of government agricultural schemes, optionally filtered by category."""
    from backend.data.schemes import SCHEME_CATALOG, SCHEME_CATEGORIES
    schemes = SCHEME_CATALOG
    if category:
        schemes = [s for s in schemes if s["category"] == category]
    return {
        "success": True,
        "data": {
            "schemes": schemes,
            "categories": SCHEME_CATEGORIES,
            "total": len(schemes),
        },
    }

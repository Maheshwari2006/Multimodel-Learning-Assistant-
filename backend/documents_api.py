import json
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.auth.oauth2 import get_current_user
from backend.database import models
from backend.database.database import get_db
from backend.services import (MAX_UPLOAD_MB, UPLOAD_DIR, doc_dict, get_user_docs, jloads, process_document)
from document_intelligence import ALLOWED_EXTENSIONS
from document_intelligence.extractors import LEGACY_HINTS

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/supported")
def supported_types():
    return {"extensions": ALLOWED_EXTENSIONS, "max_upload_mb": MAX_UPLOAD_MB}


@router.post("/upload", status_code=201)
async def upload_document(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    original = os.path.basename(file.filename or "").strip()
    if not original:
        raise HTTPException(status_code=400, detail="The file has no name.")
    ext = os.path.splitext(original)[1].lower()
    if ext in LEGACY_HINTS:
        raise HTTPException(status_code=415, detail=LEGACY_HINTS[ext])
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"'{ext or 'this file type'}' is not supported. Supported types: {', '.join(ALLOWED_EXTENSIONS)}.",
        )

    stored_name = f"{uuid.uuid4().hex}{ext}"
    target = UPLOAD_DIR / stored_name
    limit = MAX_UPLOAD_MB * 1024 * 1024
    size = 0
    try:
        with open(target, "wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > limit:
                    raise HTTPException(status_code=413, detail=f"File is larger than the {MAX_UPLOAD_MB} MB limit.")
                out.write(chunk)
        if size == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    except HTTPException:
        target.unlink(missing_ok=True)
        raise

    doc = models.Document(
        user_id=user.id, original_name=original, stored_name=stored_name, ext=ext,
        mime_type=file.content_type, size_bytes=size, status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    background.add_task(process_document, doc.id)
    return doc_dict(doc)


@router.get("")
@router.get("/")
def list_documents(db: Session = Depends(get_db), user=Depends(get_current_user)):
    docs = (
        db.query(models.Document)
        .filter(models.Document.user_id == user.id)
        .order_by(models.Document.created_at.desc())
        .all()
    )
    return [doc_dict(d) for d in docs]


@router.get("/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc = get_user_docs(db, user, [doc_id], require_ready=False)[0]
    return doc_dict(doc)


@router.get("/{doc_id}/preview")
def preview_document(doc_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc = get_user_docs(db, user, [doc_id], require_ready=False)[0]
    rows = (
        db.query(models.DocumentChunk)
        .filter(models.DocumentChunk.document_id == doc.id)
        .order_by(models.DocumentChunk.idx)
        .limit(4)
        .all()
    )
    return {
        "document": doc_dict(doc),
        "chunks": [{"idx": r.idx, "page": r.page, "section": r.section, "kind": r.kind, "text": r.text[:700]} for r in rows],
    }


@router.post("/{doc_id}/retry")
def retry_document(doc_id: int, background: BackgroundTasks, db: Session = Depends(get_db),
                   user=Depends(get_current_user)):
    doc = get_user_docs(db, user, [doc_id], require_ready=False)[0]
    if not (UPLOAD_DIR / doc.stored_name).exists():
        raise HTTPException(status_code=410, detail="The stored file is gone. Please upload it again.")
    doc.status, doc.error = "processing", None
    db.commit()
    background.add_task(process_document, doc.id)
    return doc_dict(doc)


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc = get_user_docs(db, user, [doc_id], require_ready=False)[0]
    (UPLOAD_DIR / doc.stored_name).unlink(missing_ok=True)
    db.delete(doc)
    db.commit()
    return {"deleted": doc_id}

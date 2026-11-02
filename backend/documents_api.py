
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.auth.oauth2 import get_current_user
from backend.database import models
from backend.database.database import get_db
from backend.services import (
    MAX_UPLOAD_MB,
    UPLOAD_DIR,
    doc_dict,
    get_user_docs,
    process_document,
)
from backend.storage import (
    upload_to_storage,
    download_from_storage,
    delete_from_storage,
)
from document_intelligence import ALLOWED_EXTENSIONS
from document_intelligence.extractors import LEGACY_HINTS

router = APIRouter(prefix="/documents", tags=["Documents"])


def using_supabase():
    return bool(
        os.getenv("SUPABASE_URL")
        and os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )


@router.get("/supported")
def supported_types():
    return {
        "extensions": ALLOWED_EXTENSIONS,
        "max_upload_mb": MAX_UPLOAD_MB,
    }


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
    limit = MAX_UPLOAD_MB * 1024 * 1024
    size = 0
    file_data = bytearray()

    try:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)

            if size > limit:
                raise HTTPException(
                    status_code=413,
                    detail=f"File is larger than the {MAX_UPLOAD_MB} MB limit.",
                )

            file_data.extend(chunk)

        if size == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        if using_supabase():
            upload_to_storage(
                stored_name,
                bytes(file_data),
                file.content_type,
            )
        else:
            target = UPLOAD_DIR / stored_name
            with open(target, "wb") as out:
                out.write(file_data)

        doc = models.Document(
            user_id=user.id,
            original_name=original,
            stored_name=stored_name,
            ext=ext,
            mime_type=file.content_type,
            size_bytes=size,
            status="processing",
        )

        db.add(doc)
        db.commit()
        db.refresh(doc)

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()

        if using_supabase():
            try:
                delete_from_storage(stored_name)
            except Exception:
                pass
        else:
            (UPLOAD_DIR / stored_name).unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Unable to upload the document. Check the backend logs.",
        ) from exc

    finally:
        await file.close()

    background.add_task(process_document, doc.id)

    return doc_dict(doc)


@router.get("")
@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    docs = (
        db.query(models.Document)
        .filter(models.Document.user_id == user.id)
        .order_by(models.Document.created_at.desc())
        .all()
    )

    return [doc_dict(d) for d in docs]


@router.get("/{doc_id}")
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    doc = get_user_docs(db, user, [doc_id], require_ready=False)[0]
    return doc_dict(doc)


@router.get("/{doc_id}/preview")
def preview_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
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
        "chunks": [
            {
                "idx": r.idx,
                "page": r.page,
                "section": r.section,
                "kind": r.kind,
                "text": r.text[:700],
            }
            for r in rows
        ],
    }


@router.post("/{doc_id}/retry")
def retry_document(
    doc_id: int,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    doc = get_user_docs(db, user, [doc_id], require_ready=False)[0]

    try:
        if using_supabase():
            download_from_storage(doc.stored_name)
        elif not (UPLOAD_DIR / doc.stored_name).exists():
            raise HTTPException(
                status_code=410,
                detail="The stored file is gone. Please upload it again.",
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=410,
            detail="The stored file is unavailable. Please upload it again.",
        ) from exc

    doc.status = "processing"
    doc.error = None
    db.commit()

    background.add_task(process_document, doc.id)

    return doc_dict(doc)


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    doc = get_user_docs(db, user, [doc_id], require_ready=False)[0]

    try:
        if using_supabase():
            delete_from_storage(doc.stored_name)
        else:
            (UPLOAD_DIR / doc.stored_name).unlink(missing_ok=True)

        db.delete(doc)
        db.commit()

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to delete the document. Please try again.",
        ) from exc

    return {"deleted": doc_id}

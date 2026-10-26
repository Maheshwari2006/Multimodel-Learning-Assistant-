"""Shared helpers for the API routers (ownership checks, chunk loading, error mapping, serializers)."""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.database import models
from backend.database.database import SessionLocal
from backend.learning_logic import GenerationError
from backend.llm import LLMUnavailable

log = logging.getLogger("learning_assistant")

ROOT_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("DOCUMENT_UPLOAD_DIR", ROOT_DIR / "uploads" / "documents"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() + "Z" if dt else None


def jloads(value, default=None):
    try:
        return json.loads(value) if value else (default if default is not None else [])
    except (TypeError, ValueError):
        return default if default is not None else []


def map_llm_errors(fn):
    """Run ``fn`` and translate model failures into clear HTTP errors."""
    try:
        return fn()
    except LLMUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except GenerationError as exc:
        raise HTTPException(status_code=502, detail=f"{exc} Please try again.")


# ------------------------------------------------------------------ documents
def doc_dict(d: models.Document) -> Dict:
    return {
        "id": d.id,
        "name": d.original_name,
        "ext": d.ext,
        "size_bytes": d.size_bytes,
        "status": d.status,
        "error": d.error,
        "warnings": jloads(d.warnings),
        "page_count": d.page_count,
        "char_count": d.char_count,
        "chunk_count": d.chunk_count,
        "ocr_used": bool(d.ocr_used),
        "created_at": iso(d.created_at),
        "processed_at": iso(d.processed_at),
    }


def get_user_docs(db: Session, user, ids: Sequence[int], require_ready: bool = True) -> List[models.Document]:
    ids = list(dict.fromkeys(int(i) for i in ids))
    if not ids:
        return []
    docs = (
        db.query(models.Document)
        .filter(models.Document.user_id == user.id, models.Document.id.in_(ids))
        .all()
    )
    if len(docs) != len(ids):
        raise HTTPException(status_code=404, detail="One or more selected documents were not found.")
    if require_ready:
        pending = [d.original_name for d in docs if d.status != "ready"]
        if pending:
            raise HTTPException(
                status_code=409,
                detail="These documents are not ready yet (still processing or failed): " + ", ".join(pending),
            )
    order = {i: n for n, i in enumerate(ids)}
    return sorted(docs, key=lambda d: order[d.id])


def load_chunks(db: Session, docs: Sequence[models.Document]) -> List[Dict]:
    names = {d.id: d.original_name for d in docs}
    rows = (
        db.query(models.DocumentChunk)
        .filter(models.DocumentChunk.document_id.in_(list(names)))
        .order_by(models.DocumentChunk.document_id, models.DocumentChunk.idx)
        .all()
    )
    order = {d.id: n for n, d in enumerate(docs)}
    rows.sort(key=lambda r: (order[r.document_id], r.idx))
    return [
        {
            "document_id": r.document_id,
            "document_name": names[r.document_id],
            "idx": r.idx,
            "text": r.text,
            "page": r.page,
            "section": r.section,
            "kind": r.kind,
        }
        for r in rows
    ]


def docs_label(docs: Sequence[models.Document], limit: int = 2) -> str:
    names = [os.path.splitext(d.original_name)[0] for d in docs]
    if len(names) <= limit:
        return " + ".join(names)
    return " + ".join(names[:limit]) + f" +{len(names) - limit} more"


# ------------------------------------------------------------------ background processing
def process_document(doc_id: int) -> None:
    """Extract -> chunk -> persist. Runs after the upload response, with its own DB session."""
    from document_intelligence import ExtractionError, build_chunks, extract_file

    db = SessionLocal()
    try:
        doc = db.get(models.Document, doc_id)
        if doc is None:
            return
        doc.status, doc.error = "processing", None
        db.commit()
        try:
            result = extract_file(str(UPLOAD_DIR / doc.stored_name), doc.ext)
            chunks = build_chunks(result.units)
            if not chunks:
                raise ExtractionError("No readable text was found in this file.")
            db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id == doc.id).delete()
            db.bulk_save_objects([
                models.DocumentChunk(
                    document_id=doc.id, idx=c["idx"], text=c["text"], page=c["page"],
                    section=(c["section"] or None) and str(c["section"])[:300], kind=c["kind"],
                )
                for c in chunks
            ])
            doc.status = "ready"
            doc.page_count = result.page_count
            doc.chunk_count = len(chunks)
            doc.char_count = sum(len(c["text"]) for c in chunks)
            doc.ocr_used = result.ocr_used
            doc.warnings = json.dumps(result.warnings)
        except ExtractionError as exc:
            doc.status, doc.error = "failed", str(exc)
        except Exception:  # noqa: BLE001 - never leave a document stuck in "processing"
            log.exception("Document %s failed to process", doc_id)
            doc.status = "failed"
            doc.error = "Unexpected error while reading this file. Check the backend log for details."
        doc.processed_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()


# ------------------------------------------------------------------ retrieval + shared helpers
def text_chunks(text: str, name: str = "Pasted text") -> List[Dict]:
    """Turn pasted text into the same chunk dicts that stored documents produce."""
    from document_intelligence import Unit, build_chunks

    return [
        {"document_id": None, "document_name": name, "idx": c["idx"], "text": c["text"],
         "page": None, "section": None, "kind": c["kind"]}
        for c in build_chunks([Unit(text=text.strip())])
    ]


def spread(chunks: Sequence[Dict], n: int) -> List[Dict]:
    """``n`` chunks evenly spread through the material (used for overview-style questions)."""
    chunks = list(chunks)
    if len(chunks) <= n:
        return chunks
    return [chunks[round(i * (len(chunks) - 1) / (n - 1))] for i in range(n)] if n > 1 else chunks[:1]


_OVERVIEW = ("summar", "overview", "main point", "key point", "outline", "what is this", "what's this",
             "about this", "gist", "tl;dr", "सारांश", "सार ")


def retrieve(chunks: Sequence[Dict], query: str, k: int = 6, max_total: int = 8) -> List[Dict]:
    """BM25 retrieval. Guarantees every selected document contributes and falls back to an even spread
    for overview questions or when no keyword matches (e.g. 'what is this about?')."""
    from document_intelligence import BM25Index

    chunks = list(chunks)
    if not chunks:
        return []
    q = query.lower()
    if any(w in q for w in _OVERVIEW):
        return spread(chunks, min(max_total, len(chunks)))
    index = BM25Index([c["text"] for c in chunks])
    ranked = index.top_k(query, k)
    picked = [i for i, _ in ranked]
    if not picked:
        return spread(chunks, min(4, len(chunks)))
    doc_ids = {c["document_id"] for c in chunks}
    if len(doc_ids) > 1:                                    # multi-document questions / comparisons
        scores = index.score(query)
        for doc in doc_ids:
            if any(chunks[i]["document_id"] == doc for i in picked):
                continue
            own = sorted((i for i, c in enumerate(chunks) if c["document_id"] == doc), key=lambda i: scores[i], reverse=True)
            picked.extend(own[:2])
    picked = picked[:max_total]
    return [chunks[i] for i in sorted(set(picked), key=picked.index)]


def ids_dump(ids) -> str:
    return json.dumps([int(i) for i in (ids or [])])


def source_chunks(db: Session, user, document_ids, text: Optional[str], require_one: bool = True):
    """Resolve 'selected documents or pasted text' to (docs, chunks, label)."""
    if document_ids:
        docs = get_user_docs(db, user, document_ids)
        chunks = load_chunks(db, docs)
        if not chunks:
            raise HTTPException(status_code=409, detail="The selected documents contain no readable text.")
        return docs, chunks, docs_label(docs)
    if text and text.strip():
        return [], text_chunks(text), "Pasted text"
    if require_one:
        raise HTTPException(status_code=400, detail="Select at least one document (or provide some text).")
    return [], [], ""

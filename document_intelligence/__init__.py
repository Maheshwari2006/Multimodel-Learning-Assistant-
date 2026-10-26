"""Universal document intelligence pipeline.

Pure-Python (no FastAPI / SQLAlchemy imports) so it can be tested on its own:

    extractors  -> turn a file into ordered "units" (text + page/section metadata)
    chunker     -> split units into retrieval-sized chunks
    retriever   -> dependency-free BM25 ranking over chunks

To support a new file type, register one function in ``extractors.EXTRACTORS``.
"""
from .extractors import (  # noqa: F401
    ALLOWED_EXTENSIONS,
    ExtractionError,
    ExtractionResult,
    Unit,
    extract_file,
    ocr_available,
)
from .chunker import build_chunks  # noqa: F401
from .retriever import BM25Index, tokenize  # noqa: F401

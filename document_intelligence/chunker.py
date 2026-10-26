"""Split extraction units into retrieval-sized chunks (keeps page / section metadata)."""
from __future__ import annotations

import re
from typing import Dict, List

from .extractors import Unit

DEFAULT_CHUNK_CHARS = 1200
DEFAULT_OVERLAP = 150


def _split_long(text: str, size: int, overlap: int) -> List[str]:
    """Split on paragraph / sentence boundaries; hard-split only as a last resort."""
    if len(text) <= size:
        return [text]
    pieces = re.split(r"(?<=\n\n)|(?<=[.!?।])\s+", text)
    chunks, cur = [], ""
    for piece in pieces:
        piece = piece or ""
        while len(piece) > size:                      # a single oversize piece
            if cur:
                chunks.append(cur.strip())
                cur = ""
            chunks.append(piece[:size].strip())
            piece = piece[size - overlap:]
        if len(cur) + len(piece) + 1 > size and cur:
            chunks.append(cur.strip())
            tail = cur[-overlap:] if overlap else ""
            cur = (tail + " " + piece) if tail else piece
        else:
            cur = (cur + " " + piece) if cur else piece
    if cur.strip():
        chunks.append(cur.strip())
    return [c for c in chunks if c]


def _split_table(unit: Unit, size: int) -> List[str]:
    lines = unit.text.splitlines()
    header = unit.header or ""
    out, cur = [], []
    cur_len = 0
    for i, line in enumerate(lines):
        if cur and cur_len + len(line) + 1 > size:
            out.append("\n".join(cur))
            cur, cur_len = ([header] if header and line != header else []), len(header)
        cur.append(line)
        cur_len += len(line) + 1
    if cur:
        out.append("\n".join(cur))
    return out


def build_chunks(units: List[Unit], size: int = DEFAULT_CHUNK_CHARS, overlap: int = DEFAULT_OVERLAP) -> List[Dict]:
    """Return ordered chunk dicts: {idx, text, page, section, kind}."""
    chunks: List[Dict] = []
    for unit in units:
        if unit.kind == "table":
            parts = _split_table(unit, size)
        elif unit.kind == "code":
            parts = _split_long_lines(unit.text, size)
        else:
            parts = _split_long(unit.text, size, overlap)
        for part in parts:
            part = part.strip()
            if part:
                chunks.append({
                    "idx": len(chunks),
                    "text": part,
                    "page": unit.page,
                    "section": unit.section,
                    "kind": unit.kind,
                })
    return chunks


def _split_long_lines(text: str, size: int) -> List[str]:
    """Code / structured text: split on line boundaries so lines are never cut."""
    out, cur, n = [], [], 0
    for line in text.splitlines():
        if cur and n + len(line) + 1 > size:
            out.append("\n".join(cur))
            cur, n = [], 0
        cur.append(line[:size])
        n += len(line) + 1
    if cur:
        out.append("\n".join(cur))
    return out

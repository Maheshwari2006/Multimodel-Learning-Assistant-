"""Small dependency-free BM25 retriever (good enough for per-user local document sets).

No vector database is needed. ``tokenize`` keeps Devanagari (Hindi / Marathi) words intact.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, List, Sequence, Tuple

_TOKEN = re.compile(r"[\w\u0900-\u097F]+", re.UNICODE)
_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "are", "was", "were", "be", "it",
    "this", "that", "with", "as", "by", "at", "from", "what", "which", "who", "how", "why", "when", "do",
    "does", "me", "my", "i", "you", "about", "can", "please", "explain", "tell", "give", "show",
}


def tokenize(text: str) -> List[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]


class BM25Index:
    def __init__(self, docs: Sequence[str], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tokens = [tokenize(d) for d in docs]
        self.tf = [Counter(t) for t in self.tokens]
        self.lengths = [len(t) for t in self.tokens]
        n = max(len(docs), 1)
        self.avg = (sum(self.lengths) / n) or 1.0
        df: Counter = Counter()
        for counter in self.tf:
            df.update(counter.keys())
        self.idf: Dict[str, float] = {
            term: math.log(1 + (n - freq + 0.5) / (freq + 0.5)) for term, freq in df.items()
        }

    def score(self, query: str) -> List[float]:
        q_terms = set(tokenize(query))
        scores = []
        for i, tf in enumerate(self.tf):
            s = 0.0
            for term in q_terms:
                f = tf.get(term)
                if not f:
                    continue
                denom = f + self.k1 * (1 - self.b + self.b * self.lengths[i] / self.avg)
                s += self.idf.get(term, 0.0) * f * (self.k1 + 1) / denom
            scores.append(s)
        return scores

    def top_k(self, query: str, k: int = 6) -> List[Tuple[int, float]]:
        ranked = sorted(enumerate(self.score(query)), key=lambda x: x[1], reverse=True)
        return [(i, s) for i, s in ranked[:k] if s > 0]

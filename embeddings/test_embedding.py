import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from text_processing.cleaner import TextCleaner
from text_processing.chunker import TextChunker

from embeddings.embedding_model import (
    EmbeddingGenerator
)

with open(
    "sample.txt",
    "r",
    encoding="utf-8"
) as file:

    text = file.read()

clean_text = TextCleaner.clean_text(text)

chunks = TextChunker.chunk_text(
    clean_text,
    chunk_size=500
)

generator = EmbeddingGenerator()

embeddings = generator.generate_embeddings(
    chunks
)

print(
    "Total Chunks:",
    len(chunks)
)

print(
    "Total Embeddings:",
    len(embeddings)
)

print(
    "Embedding Dimension:",
    len(embeddings[0])
)

print(
    "\nFirst 10 Values:\n"
)

print(
    embeddings[0][:10]
)
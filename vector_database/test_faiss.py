import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except:
    pass

print("🤖 Generating Embeddings...")

import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from embeddings.embedding_model import EmbeddingGenerator
from vector_database.faiss_manager import FAISSManager

texts = [
    "Machine Learning is a branch of Artificial Intelligence.",
    "Deep Learning uses neural networks.",
    "Python is widely used in AI and Data Science."
]

print("🤖 Generating Embeddings...")

embedding_generator = EmbeddingGenerator()

embeddings = embedding_generator.generate_embeddings(
    texts
)

print("✅ Embeddings Created:", len(embeddings))

dimension = len(embeddings[0])

print("📏 Embedding Dimension:", dimension)

faiss_manager = FAISSManager(dimension)

print("📦 Adding Embeddings To FAISS...")

faiss_manager.add_embeddings(
    embeddings
)

query = "What is Artificial Intelligence?"

query_embedding = (
    embedding_generator.generate_embedding(
        query
    )
)

print("🔍 Searching Similar Chunks...")

distances, indices = (
    faiss_manager.search(
        query_embedding,
        top_k=2
    )
)

print("\n📊 Search Results:")
print("Distances:", distances)
print("Indices:", indices)

print("\n✅ FAISS Search Successful 🚀")
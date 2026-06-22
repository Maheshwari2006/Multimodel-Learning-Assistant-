import sys
import os

# Fix Unicode issues on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to Python path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from embeddings.embedding_model import EmbeddingGenerator
from vector_database.faiss_manager import FAISSManager
from semantic_search.search_engine import SemanticSearchEngine

chunks = [
    "Machine Learning is a branch of Artificial Intelligence.",
    "Deep Learning uses Neural Networks.",
    "Python is widely used in Data Science.",
    "Computer Vision processes images and videos."
]

generator = EmbeddingGenerator()

embeddings = []

for chunk in chunks:
    embeddings.append(
        generator.generate_embedding(chunk)
    )

dimension = len(embeddings[0])

faiss_db = FAISSManager(dimension)

faiss_db.add_embeddings(
    embeddings
)

search_engine = SemanticSearchEngine(
    faiss_db,
    chunks
)

query = "Explain Neural Networks"

results = search_engine.search(
    query,
    top_k=2
)

# Professional Output
print("\n" + "=" * 60)
print("      MULTIMODEL LEARNING ASSISTANT")
print("=" * 60)

print(f"\nQuery : {query}")

print("\nTop Semantic Search Results:\n")

for i, result in enumerate(results, start=1):

    print(f"Rank #{i}")
    print("-" * 50)
    print(result)
    print("-" * 50)

print("\n" + "=" * 60)
print("Search Completed Successfully")
print("=" * 60)
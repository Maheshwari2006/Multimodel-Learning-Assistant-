from embeddings.embedding_model import (
    EmbeddingGenerator
)

from vector_database.faiss_manager import (
    FAISSManager
)


class SemanticSearchEngine:

    def __init__(
        self,
        faiss_db,
        chunks
    ):

        self.faiss_db = faiss_db
        self.chunks = chunks

        self.embedding_generator = (
            EmbeddingGenerator()
        )

    def search(
        self,
        query,
        top_k=3
    ):

        query_embedding = (
            self.embedding_generator
            .generate_embedding(query)
        )

        distances, indices = (
            self.faiss_db.search(
                query_embedding,
                top_k
            )
        )

        results = []

        for idx in indices[0]:
            results.append(
                self.chunks[idx]
            )

        return results
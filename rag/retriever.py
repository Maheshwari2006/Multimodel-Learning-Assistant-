from embeddings.embedding_model import (
    EmbeddingGenerator
)


class Retriever:

    def __init__(
        self,
        faiss_manager,
        chunks
    ):

        self.faiss_manager = faiss_manager
        self.chunks = chunks

        self.embedding_generator = (
            EmbeddingGenerator()
        )

    def retrieve(
        self,
        query,
        top_k=3
    ):

        query_embedding = (
            self.embedding_generator
            .generate_embedding(query)
        )

        distances, indices = (
            self.faiss_manager.search(
                query_embedding,
                top_k
            )
        )

        results = []

        for idx in indices[0]:

            if idx < len(self.chunks):

                results.append(
                    self.chunks[idx]
                )

        return results
import faiss
import numpy as np


class FAISSManager:

    def __init__(self, dimension):

        self.dimension = dimension

        self.index = faiss.IndexFlatL2(
            dimension
        )

    def add_embeddings(
        self,
        embeddings
    ):

        vectors = np.array(
            embeddings
        ).astype("float32")

        self.index.add(vectors)

    def search(
        self,
        query_embedding,
        top_k=3
    ):

        query = np.array(
            [query_embedding]
        ).astype("float32")

        distances, indices = (
            self.index.search(
                query,
                top_k
            )
        )

        return distances, indices
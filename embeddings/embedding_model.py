from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def generate_embedding(self, text):

        return self.model.encode(text)

    def generate_embeddings(self, chunks):

        embeddings = []

        for chunk in chunks:
            embedding = self.model.encode(chunk)
            embeddings.append(embedding)

        return embeddings
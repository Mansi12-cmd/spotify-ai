from fastembed import TextEmbedding


class EmbeddingService:

    def __init__(self):
        self.model = TextEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )

    async def generate_embedding(
        self,
        text: str,
    ) -> list[float]:

        embedding = next(
            self.model.embed([text])
        )

        return embedding.tolist()
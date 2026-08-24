import uuid

from app.services.embedding_service import EmbeddingService
from app.services.memory_service import MemoryService


class MemoryRetrievalService:

    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service
        self.embedding_service = EmbeddingService()

    async def retrieve_relevant_memories(
        self,
        user_id: uuid.UUID,
        query: str,
        limit: int = 5,
        max_distance: float = 0.50,
    ) -> list[dict]:

        query_embedding = await self.embedding_service.generate_embedding(
            query
        )

        results = await self.memory_service.search_similar_memories(
            user_id=user_id,
            query_embedding=query_embedding,
            limit=limit,
        )

        memories = []

        for memory, distance in results:

            if distance > max_distance:
                continue

            memories.append(
                {
                    "id": memory.id,
                    "predicate": memory.predicate,
                    "value": memory.value,
                    "confidence": memory.confidence,
                    "distance": distance,
                }
            )

        return memories
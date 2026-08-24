import uuid

from app.services.memory_retrieval_service import MemoryRetrievalService


class ContextService:

    def __init__(
        self,
        memory_retrieval_service: MemoryRetrievalService,
    ):
        self.memory_retrieval_service = memory_retrieval_service

    async def build_memory_context(
        self,
        user_id: uuid.UUID,
        query: str,
        limit: int = 5,
        max_distance: float = 0.50,
    ) -> str:

        memories = await self.memory_retrieval_service.retrieve_relevant_memories(
            user_id=user_id,
            query=query,
            limit=limit,
            max_distance=max_distance,
        )

        if not memories:
            return ""

        lines = [
            "Relevant information about the user:"
        ]

        for memory in memories:
            predicate = memory["predicate"]
            value = memory["value"]

            lines.append(
                f"- {predicate}: {value}"
            )

        return "\n".join(lines)
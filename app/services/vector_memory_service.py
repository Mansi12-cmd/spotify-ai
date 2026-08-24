import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MemoryFact


class VectorMemoryService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_memories(
        self,
        user_id: uuid.UUID,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[MemoryFact]:

        distance = MemoryFact.embedding.cosine_distance(
            query_embedding
        )

        result = await self.db.execute(
            select(MemoryFact)
            .where(
                MemoryFact.user_id == user_id,
                MemoryFact.is_active.is_(True),
                MemoryFact.embedding.is_not(None),
            )
            .order_by(distance)
            .limit(limit)
        )

        return list(result.scalars().all())
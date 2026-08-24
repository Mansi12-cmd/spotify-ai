import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MemoryFact, MemoryHistory

from app.services.embedding_service import EmbeddingService


class MemoryService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_memory(
        self,
        user_id: uuid.UUID,
        predicate: str,
        value: str,
        confidence: float = 1.0,
        source: str = "conversation",
        source_message_id: uuid.UUID | None = None,
    ) -> MemoryFact:

        embedding_text = f"{predicate}: {value}"

        embedding = None
        

        memory = MemoryFact(
            user_id=user_id,
            predicate=predicate,
            value=value,
            confidence=confidence,
            source=source,
            source_message_id=source_message_id,
            valid_from=datetime.now(timezone.utc),
            valid_to=None,
            is_active=True,
            embedding=embedding,
        )

        self.db.add(memory)
        await self.db.flush()

        history = MemoryHistory(
            memory_fact_id=memory.id,
            user_id=user_id,
            action="created",
            old_value=None,
            new_value=value,
            reason="Memory created",
            source_message_id=source_message_id,
        )

        self.db.add(history)

        await self.db.commit()
        await self.db.refresh(memory)

        return memory

    async def get_active_memories(
        self,
        user_id: uuid.UUID,
    ) -> list[MemoryFact]:

        result = await self.db.execute(
            select(MemoryFact)
            .where(
                MemoryFact.user_id == user_id,
                MemoryFact.is_active.is_(True),
            )
            .order_by(MemoryFact.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_active_memory(
        self,
        user_id: uuid.UUID,
        predicate: str,
        value: str,
    ) -> MemoryFact | None:

        result = await self.db.execute(
            select(MemoryFact)
            .where(
                MemoryFact.user_id == user_id,
                MemoryFact.predicate == predicate,
                MemoryFact.value == value,
                MemoryFact.is_active.is_(True),
            )
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def get_memory_history(
        self,
        user_id: uuid.UUID,
    ) -> list[MemoryHistory]:

        result = await self.db.execute(
            select(MemoryHistory)
            .where(
                MemoryHistory.user_id == user_id
            )
            .order_by(MemoryHistory.created_at.asc())
        )

        return list(result.scalars().all())

    async def update_memory(
        self,
        memory_id: uuid.UUID,
        new_value: str,
        reason: str = "Memory updated",
        source_message_id: uuid.UUID | None = None,
    ) -> MemoryFact:

        # --------------------------------------------------
        # 1. Find the currently active memory
        # --------------------------------------------------

        result = await self.db.execute(
            select(MemoryFact)
            .where(
                MemoryFact.id == memory_id,
                MemoryFact.is_active.is_(True),
            )
        )

        old_memory = result.scalar_one_or_none()

        if old_memory is None:
            raise ValueError(
                f"Active memory not found: {memory_id}"
            )

        # --------------------------------------------------
        # 2. Close the old version
        # --------------------------------------------------

        now = datetime.now(timezone.utc)

        old_value = old_memory.value

        old_memory.valid_to = now
        old_memory.is_active = False
        old_memory.updated_at = now

        # --------------------------------------------------
        # 3. Create the new version
        # --------------------------------------------------

        embedding = None

        new_memory = MemoryFact(
            user_id=old_memory.user_id,
            predicate=old_memory.predicate,
            value=new_value,
            confidence=old_memory.confidence,
            source=old_memory.source,
            source_message_id=source_message_id,
            valid_from=now,
            valid_to=None,
            is_active=True,
            embedding=None,
        )

        self.db.add(new_memory)

        await self.db.flush()

        # --------------------------------------------------
        # 4. Record the transition
        # --------------------------------------------------

        history = MemoryHistory(
            memory_fact_id=new_memory.id,
            user_id=old_memory.user_id,
            action="superseded",
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            source_message_id=source_message_id,
        )

        self.db.add(history)

        await self.db.commit()
        await self.db.refresh(new_memory)

        return new_memory

    async def get_memories_at(
        self,
        user_id: uuid.UUID,
        timestamp: datetime,
    ) -> list[MemoryFact]:

        result = await self.db.execute(
            select(MemoryFact)
            .where(
                MemoryFact.user_id == user_id,
                MemoryFact.valid_from <= timestamp,
                (
                    (MemoryFact.valid_to.is_(None))
                    | (MemoryFact.valid_to > timestamp)
                ),
            )
            .order_by(MemoryFact.valid_from.asc())
        )

        return list(result.scalars().all())

    async def get_memory_versions(
        self,
        user_id: uuid.UUID,
        predicate: str,
    ) -> list[MemoryFact]:

        result = await self.db.execute(
            select(MemoryFact)
            .where(
                MemoryFact.user_id == user_id,
                MemoryFact.predicate == predicate,
            )
            .order_by(MemoryFact.valid_from.asc())
        )

        return list(result.scalars().all())

    async def search_similar_memories(
        self,
        user_id: uuid.UUID,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[tuple[MemoryFact, float]]:

        result = await self.db.execute(
            select(
                MemoryFact,
                MemoryFact.embedding.cosine_distance(query_embedding).label(
                    "distance"
                ),
            )
            .where(
                MemoryFact.user_id == user_id,
                MemoryFact.is_active.is_(True),
                MemoryFact.embedding.is_not(None),
            )
            .order_by(
                MemoryFact.embedding.cosine_distance(query_embedding)
            )
            .limit(limit)
        )

        return [
            (memory, distance)
            for memory, distance in result.all()
        ]

    async def search_memories(
        self,
        user_id: uuid.UUID,
        query: str,
        limit: int = 5,
    ) -> list[tuple[MemoryFact, float]]:

        result = await self.db.execute(
        select(MemoryFact)
        .where(
            MemoryFact.user_id == user_id,
            MemoryFact.is_active.is_(True),
        )
        .order_by(MemoryFact.created_at.desc())
        .limit(limit)
    )

        return list(result.scalars().all())
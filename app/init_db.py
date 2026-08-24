import asyncio
from pathlib import Path

from sqlalchemy import text

from app.database import engine


async def initialize_database():
    schema_path = Path(__file__).parent / "schema.sql"

    schema = schema_path.read_text(
        encoding="utf-8"
    )

    async with engine.begin() as connection:
        # Enable required PostgreSQL extensions first.
        await connection.execute(
            text('CREATE EXTENSION IF NOT EXISTS "vector"')
        )

        await connection.execute(
            text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        )

        # Execute schema statements.
        statements = [
            statement.strip()
            for statement in schema.split(";")
            if statement.strip()
        ]

        for statement in statements:
            await connection.execute(
                text(statement)
            )

    print("Database Initialized.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(
        initialize_database()
    )
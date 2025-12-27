"""
Create database tables
"""
import asyncio
from app.db.session import engine
from app.db.base import Base


async def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())

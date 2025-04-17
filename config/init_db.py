from config.database import engine, Base
from models import Status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from config.conf_logger import logger


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        required_statuses = ["waiting file", "start", "banned"]
        for name in required_statuses:
            result = await session.execute(select(Status).where(Status.name == name))
            if not result.scalars().first():
                session.add(Status(name=name))
        logger.info("DB successful in init_statuses")
        await session.commit()

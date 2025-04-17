from sqlalchemy.orm import Session
from models import Status
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from config.conf_logger import logger
from sqlalchemy import select


class StatusRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, status_data: dict) -> Status:
        try:
            db_query = Status(**status_data)
            self.db.add(db_query)
            await self.db.commit()
            await self.db.refresh(db_query)
            logger.info("DB successful in create_status")
            return db_query
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"DB Error in create_status: {e}", exc_info=True)
            return None

    async def get_all(self) -> List[Status]:
        try:
            result = await self.db.execute(select(Status))
            queries = result.scalars().all()
            logger.info("DB successful in get_all_status")
            return queries
        except SQLAlchemyError as e:
            logger.error(f"DB Error in get_all_status: {e}", exc_info=True)
            return None

    async def get_by_name(self, name: str) -> Optional[Status]:
        try:
            result = await self.db.execute(select(Status).where(Status.name == name))
            status = result.scalars().first()
            logger.info("DB successful in get_by_name_status")
            return status
        except SQLAlchemyError as e:
            logger.error(f"DB Error in get_by_name_status: {e}", exc_info=True)
            return None

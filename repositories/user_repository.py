from models import User
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from config.conf_logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_data: dict) -> User:
        try:
            db_user = User(**user_data)
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            logger.info("DB successful in create_user")
            return db_user
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"DB Error in create_user: {e}", exc_info=True)
            return None

    async def get_all(self) -> List[User]:
        try:
            result = await self.db.execute(select(User))
            users = result.scalars().all()
            logger.info("DB successful in get_all_user")
            return users
        except SQLAlchemyError as e:
            logger.error(f"DB Error in get_all_user: {e}", exc_info=True)
            return None

    async def get_by_tg_id(self, tg_id: str) -> Optional[User]:
        try:
            result = await self.db.execute(select(User).where(User.tg_id == tg_id))
            users = result.scalars().first()
            logger.info("DB successful in get_by_tg_id_user")
            return users
        except SQLAlchemyError as e:
            logger.error(f"DB Error in get_by_tg_id_user: {e}", exc_info=True)
            return None

    async def update_status_id(self, tg_id: str, status_id: int) -> Optional[User]:
        try:
            db_user = await self.get_by_tg_id(tg_id)
            if not db_user:
                logger.info("DB successful in update_status_id_user - None")
                return None
            db_user.status_id = status_id
            await self.db.commit()
            await self.db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            logger.error(f"DB Error in update_status_id_user: {e}", exc_info=True)
            return None

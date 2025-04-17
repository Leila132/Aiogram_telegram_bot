from sqlalchemy.orm import Session
from models import Query
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from config.conf_logger import logger
from sqlalchemy import select


class QueryRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, query_data: dict) -> Query:
        try:
            db_query = Query(**query_data)
            if not await self.check_dublicates(query_data):
                self.db.add(db_query)
                await self.db.commit()
                await self.db.refresh(db_query)
                logger.info("DB successful in create_query")
                return db_query
            else:
                return None
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"DB Error in create_query: {e}", exc_info=True)
            return None

    async def get_all(self) -> List:
        try:
            result = await self.db.execute(select(Query))
            queries = result.scalars().all()
            logger.info("DB successful in get_all_query")
            return queries
        except SQLAlchemyError as e:
            logger.error(f"DB Error in get_all_query: {e}", exc_info=True)
            return None

    async def check_dublicates(self, query_data: dict) -> bool:
        try:
            result = await self.db.execute(
                select(Query).where(
                    (Query.title == query_data["title"])
                    & (Query.url == query_data["url"])
                    & (Query.xpath == query_data["xpath"])
                )
            )
            queries = result.scalars().first()
            logger.info("DB successful in check_dublicates_query")
            if queries:
                return True
            else:
                return False
        except SQLAlchemyError as e:
            logger.error(f"DB Error in check_dublicates_query: {e}", exc_info=True)
            return None

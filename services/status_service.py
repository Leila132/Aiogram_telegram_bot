from repositories.status_repository import StatusRepository
from models import Status
from typing import List
from config.conf_logger import logger


class StatusService:
    def __init__(self, repository: StatusRepository):
        self.repository = repository

    async def create_status(self, query) -> Status:
        try:
            created = await self.repository.create(query)
            logger.info("SERVICE successful in create_status")
            return created
        except:
            logger.error(f"SERVICE Error in create_status", exc_info=True)
            return None

    async def get_statuses(self) -> List:
        try:
            created = await self.repository.get_all()
            logger.info("SERVICE successful in get_statuses")
            return created
        except:
            logger.error(f"SERVICE Error in get_statuses", exc_info=True)
            return None

    async def get_status_by_name(self, name: str) -> Status:
        try:
            created = await self.repository.get_by_name(name)
            logger.info("SERVICE successful in get_status_by_name")
            return created
        except:
            logger.error(f"SERVICE Error in get_status_by_name", exc_info=True)
            return None

from repositories.query_repository import QueryRepository
from config.tasks import celery_task_get_price
import asyncio


class HtmlAgentService:
    def __init__(self, repository: QueryRepository):
        self.repository = repository

    async def get_average_price_from_queries(self) -> str:
        queries = await self.repository.get_all()
        serialized = [{'url': q.url, 'xpath': q.xpath} for q in queries]
        answer = celery_task_get_price.delay(serialized)
        result = await asyncio.to_thread(answer.get, timeout=10)
        return result


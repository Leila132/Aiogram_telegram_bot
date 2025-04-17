from repositories.query_repository import QueryRepository
from schemas import TableRow
from models import Query
from config.conf_logger import logger


class QueryService:
    def __init__(self, repository: QueryRepository):
        self.repository = repository

    async def create_query(self, query: TableRow) -> Query:
        try:
            created = await self.repository.create(query.dict())
            logger.info("SERVICE successful in create_query")
            return created
        except:
            logger.error(f"SERVICE Error in create_query", exc_info=True)
            return None

    async def get_queries(self) -> str:
        try:
            queries = await self.repository.get_all()

            if not queries:
                return "В базе данных пока нет записей."

            # Формируем красивое сообщение
            message = "📋 *Список всех записей:*\n\n"

            for index, query in enumerate(queries, start=1):
                message += (
                    f"🔹 *Запись #{index}*\n"
                    f"▪ *Название:* {query.title}\n"
                    f"▪ *Ссылка:* {query.url}\n"
                    f"▪ *XPath:* `{query.xpath}`\n"
                )

            # Добавляем итоговую информацию
            message += f"📊 *Всего записей: {len(queries)}*"

            logger.info("SERVICE successful in get_queries")
            return message

        except Exception as e:
            logger.error(f"SERVICE Error in get_queries: {str(e)}", exc_info=True)
            return "Произошла ошибка в БД"

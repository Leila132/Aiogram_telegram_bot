from repositories.user_repository import UserRepository
from schemas import UserData, TableRow
from models import User
from typing import List, Optional
from services.status_service import StatusService
from services.query_service import QueryService
from repositories.status_repository import StatusRepository
from repositories.query_repository import QueryRepository
import pandas as pd
import io
from config.conf_logger import logger


class UserService:
    def __init__(
        self,
        repository_user: UserRepository,
        repository_status: Optional[StatusRepository] = None,
        repository_query: Optional[QueryRepository] = None,
    ):
        self.repository_user = repository_user
        self.status_service = (
            StatusService(repository_status) if repository_status else None
        )
        self.query_service = (
            QueryService(repository_query) if repository_query else None
        )

    async def create_or_update_user(self, query: UserData) -> User:
        user = await self.repository_user.get_by_tg_id(query["tg_id"])
        status = await self.status_service.get_status_by_name(query["status_name"])
        if user and status:
            try:
                returned = await self.repository_user.update_status_id(
                    tg_id=str(user.tg_id), status_id=status.id
                )
                logger.info("SERVICE successful in create_or_update_user")
                return returned
            except:
                logger.error(f"SERVICE Error in create_or_update_user", exc_info=True)
                return None
        elif user == None and status:
            try:
                returned = await self.repository_user.create(
                    {"tg_id": query["tg_id"], "status_id": status.id}
                )
                logger.info("SERVICE successful in create_or_update_user")
                return returned
            except:
                logger.error(f"SERVICE Error in create_or_update_user", exc_info=True)
                return None
        else:
            logger.info("SERVICE successful in create_or_update_user")
            return None

    async def get_users(self) -> List:
        try:
            returned = await self.repository.get_all()
            logger.info("SERVICE successful in get_users")
            return returned
        except:
            logger.error(f"SERVICE Error in get_users", exc_info=True)
            return None

    async def check_status(self, query: UserData) -> bool:
        try:
            user = await self.repository_user.get_by_tg_id(query["tg_id"])
            status = await self.status_service.get_status_by_name(query["status_name"])
            logger.info("SERVICE successful in check_status")
            if user.status_id == status.id:
                return True
            else:
                return False
        except:
            logger.error(f"SERVICE Error in check_status", exc_info=True)
            return None

    async def analyze_data_from_user(self, query: UserData, file_name):
        df = pd.read_excel(io.BytesIO(file_name.read()))
        fine_result = {"title": [], "url": [], "xpath": []}
        bad_result = {"title": [], "url": [], "xpath": []}
        double_result = {"title": [], "url": [], "xpath": []}
        # Обрабатываем каждую строку
        for _, row in df.iterrows():
            query_data = {
                "title": str(row.get("title", "")).strip(),
                "url": str(row.get("url", "")).strip(),
                "xpath": str(row.get("xpath", "")).strip(),
            }
            try:
                table_row = TableRow(**query_data)
                not_double = await self.query_service.create_query(table_row)
                logger.info("SERVICE successful in analyze_data_from_user")
                if not_double:
                    fine_result["title"].append(query_data["title"])
                    fine_result["url"].append(query_data["url"])
                    fine_result["xpath"].append(query_data["xpath"])
                else:
                    double_result["title"].append(query_data["title"])
                    double_result["url"].append(query_data["url"])
                    double_result["xpath"].append(query_data["xpath"])
            except:
                logger.error(f"SERVICE Error in analyze_data_from_user", exc_info=True)
                bad_result["title"].append(query_data["title"])
                bad_result["url"].append(query_data["url"])
                bad_result["xpath"].append(query_data["xpath"])
        return self._format_results(fine_result, bad_result, double_result)

    def _format_results(self, fine_result, bad_result, double_result):
        # Форматируем успешные записи
        success_msg = ""
        if fine_result["title"]:
            success_msg = (
                "✅ *Успешно обработано: {} записей*\n\n"
                "Список успешных записей:\n"
                "------------------------\n"
            ).format(len(fine_result["title"]))

            for i, (title, url, xpath) in enumerate(
                zip(fine_result["title"], fine_result["url"], fine_result["xpath"]), 1
            ):
                success_msg += (
                    f"{i}. *{title}*\n" f"   Ссылка: {url}\n" f"   XPath: {xpath}\n\n"
                )
        else:
            success_msg = "🟢 Нет успешно обработанных записей\n\n"

        # Форматируем ошибочные записи
        error_msg = ""
        if bad_result["title"]:
            error_msg = (
                "❌ *Ошибка обработки: {} записей*\n\n"
                "Проблемные записи:\n"
                "------------------\n"
            ).format(len(bad_result["title"]))

            for i, (title, url, xpath) in enumerate(
                zip(bad_result["title"], bad_result["url"], bad_result["xpath"]), 1
            ):
                error_msg += (
                    f"{i}. *{title}*\n"
                    f"   Ссылка: {url or 'НЕТ'}\n"
                    f"   XPath: {xpath or 'НЕТ'}\n\n"
                )
        else:
            error_msg = "🔴 Нет записей с ошибками\n\n"

        # Форматируем дубликатные записи
        double_msg = ""
        if double_result["title"]:
            double_msg = (
                "❌ *Дубликаты обработки: {} записей*\n\n"
                "Проблемные записи:\n"
                "------------------\n"
            ).format(len(double_result["title"]))

            for i, (title, url, xpath) in enumerate(
                zip(
                    double_result["title"], double_result["url"], double_result["xpath"]
                ),
                1,
            ):
                double_msg += (
                    f"{i}. *{title}*\n"
                    f"   Ссылка: {url or 'НЕТ'}\n"
                    f"   XPath: {xpath or 'НЕТ'}\n\n"
                )
        else:
            double_msg = "🔴 Нет записей с дубликатами\n\n"

        # Итоговое сообщение
        total_msg = (
            "📊 *Итоги обработки файла*\n"
            "=======================\n"
            f"▪ Всего записей: {len(fine_result['title']) + len(bad_result['title'])}\n"
            f"▪ Успешно: {len(fine_result['title'])}\n"
            f"▪ С ошибками: {len(bad_result['title'])}\n\n"
            f"▪ С дубликатами: {len(double_result['title'])}\n\n"
            f"{success_msg}\n{error_msg}\n{double_msg}"
        )

        return total_msg

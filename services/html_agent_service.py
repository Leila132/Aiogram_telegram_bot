from repositories.query_repository import QueryRepository
from config.conf_logger import logger
import requests
from lxml import html
import re


class HtmlAgentService:
    def __init__(self, repository: QueryRepository):
        self.repository = repository

    async def get_average_price_from_queries(self) -> str:
        try:
            queries = await self.repository.get_all()

            if not queries:
                logger.info("SERVICE successful in get_average_price_grom_queries")
                return "В базе данных пока нет записей."

            price_sum = 0
            price_positive_count = 0
            price_negative_count = 0
            for _, query in enumerate(queries, start=1):
                url = query.url
                xpath = query.xpath
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                tree = html.fromstring(response.content)
                element = tree.xpath(xpath)
                if element:
                    match = re.search(
                        r"(\d+[\.,]?\d*)", element[0].text.replace(" ", "")
                    )
                    if match:
                        price_str = match.group(1).replace(",", ".")
                        try:
                            price = float(price_str)
                            price_sum += price
                            price_positive_count += 1
                        except:
                            price_negative_count += 1
                    else:
                        price_negative_count += 1
                else:
                    price_negative_count += 1
            if price_positive_count != 0:
                avg_price = round(price_sum / price_positive_count, 2)
                message = f"Получилось найти цену у {price_positive_count} записей. Средняя цена: {avg_price} рублей"
            else:
                message = "Не получилось обработать ни одну запись"

            logger.info("SERVICE successful in get_average_price_grom_queries")
            return message
        except Exception as e:
            logger.error(
                f"SERVICE Error in get_average_price_grom_queries: {str(e)}",
                exc_info=True,
            )
            return "Произошла ошибка в БД"

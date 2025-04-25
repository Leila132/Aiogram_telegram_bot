from celery import Celery
import requests
from lxml import html
import re
from config.celery import app


@app.task
def celery_task_get_price(queries):
    try:
        if not queries:
            return "В базе данных пока нет записей."

        price_sum = 0
        price_positive_count = 0
        price_negative_count = 0
        for _, query in enumerate(queries, start=1):
            url = query["url"]
            xpath = query["xpath"]
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            tree = html.fromstring(response.content)
            element = tree.xpath(xpath)
            if element:
                match = re.search(r"(\d+[\.,]?\d*)", element[0].text.replace(" ", ""))
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

        return message
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

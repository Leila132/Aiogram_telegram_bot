"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Инициализация драйвера
driver = webdriver.Chrome()

url = "https://kazan.svetofors.ru/persikoviy-sok-sadi-altaya-3l/"
xpath = "/html/body/main/div[2]/div/div/div[2]/div[2]/div[1]/strong"

# Открытие веб-страницы
driver.get(url)
time.sleep(10)
# Нахождение элемента на странице
# xpath = "/html/body/main/div/div[2]/div/div/div[2]/div[3]/div[1]/div[1]/div[2]/div[3]/div[3]/div[2]/span[1]"
element = driver.find_element(By.XPATH, xpath)
# element = driver.find_element_by_xpath("//*[@id='layoutPage']/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div/div/div[1]/span[1]")

# Получение текста из элемента
text = element.text

# Вывод текста на экран
print(text)

# Закрытие браузера
driver.quit()
"""
import requests
from lxml import html

# 1

url = "https://kazan.svetofors.ru/persikoviy-sok-sadi-altaya-3l/"
xpath = "/html/body/main/div[2]/div/div/div[2]/div[2]/div[1]/strong"

# Загружаем HTML-страницу
response = requests.get(
    url, headers={"User-Agent": "Mozilla/5.0"}
)  # User-Agent нужен, чтобы сайт не блокировал запрос
tree = html.fromstring(response.content)

# Извлекаем текст по XPATH
element = tree.xpath(xpath)
if element:
    print(element[0].text)
else:
    print("Элемент не найден")

# 2

url = "https://naturelia.net/tovari/sadipridon-2"
xpath = "/html/body/div[2]/div/div/div[3]/div[2]/ul[2]/li[1]/h2"

# Загружаем HTML-страницу
response = requests.get(
    url, headers={"User-Agent": "Mozilla/5.0"}
)  # User-Agent нужен, чтобы сайт не блокировал запрос
tree = html.fromstring(response.content)

# Извлекаем текст по XPATH
element = tree.xpath(xpath)
print(element)
if element:
    print(element[0].text)
else:
    print("Элемент не найден")

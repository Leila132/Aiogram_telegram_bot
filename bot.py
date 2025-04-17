from aiogram import Bot, Dispatcher, executor, types
from repositories.user_repository import UserRepository
from repositories.query_repository import QueryRepository
from repositories.status_repository import StatusRepository
from config.database import get_db
from config.init_db import init_db
from services.user_service import UserService
from services.status_service import StatusService
from services.query_service import QueryService
from services.html_agent_service import HtmlAgentService
import asyncio
from config.conf_logger import logger
from dotenv import dotenv_values

config = dotenv_values()

API_TOKEN = config["API_TOKEN"]

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Создаём клавиатуру с кнопками
keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True
)  # resize_keyboard подгоняет размер кнопок
keyboard.add(types.KeyboardButton("Загрузить файл"))
keyboard.add(types.KeyboardButton("Показать все записи"))
keyboard.add(types.KeyboardButton("Посчитать среднюю цену"))


@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    logger.info("Bot: user " + str(message.from_user.id) + " press button start/help")
    await message.answer(
        "Привет! Нажми на кнопку 'Загрузить файл', и я его обработаю!",
        reply_markup=keyboard,
    )


@dp.message_handler(lambda message: message.text == "Загрузить файл")
async def up_button(message: types.Message):
    async for db in get_db():
        logger.info(
            "Bot: user " + str(message.from_user.id) + " press button 'Upload file'"
        )
        repository_user = UserRepository(db)
        repository_status = StatusRepository(db)
        service_user = UserService(
            repository_user=repository_user, repository_status=repository_status
        )
        data = {"tg_id": str(message.from_user.id), "status_name": "waiting file"}
        answer = await service_user.create_or_update_user(data)
        if answer:
            await message.answer("Запрос принят! Жду файл...", reply_markup=keyboard)
        else:
            await message.answer("Что-то я чего-то не понял...", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Посчитать среднюю цену")
async def all_button(message: types.Message):
    async for db in get_db():
        logger.info(
            "Bot: user "
            + str(message.from_user.id)
            + " press button 'Show all queries'"
        )
        repository_query = QueryRepository(db)
        html_agent_service = HtmlAgentService(repository_query)
        answer = await html_agent_service.get_average_price_grom_queries()
        await message.answer(answer, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Показать все записи")
async def all_button(message: types.Message):
    async for db in get_db():
        logger.info(
            "Bot: user " + str(message.from_user.id) + " press button 'Get avg price'"
        )
        repository_query = QueryRepository(db)
        query_service = QueryService(repository_query)
        answer = await query_service.get_queries()
        await message.answer(answer, reply_markup=keyboard)


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_xlsx(message: types.Message):
    logger.info("Bot: user " + str(message.from_user.id) + " sent document")
    if not message.document.file_name.endswith(".xlsx"):
        await message.answer("Пожалуйста, отправьте файл .xlsx", reply_markup=keyboard)
        return
    async for db in get_db():
        repository_user = UserRepository(db)
        repository_status = StatusRepository(db)
        repository_query = QueryRepository(db)
        service_user = UserService(
            repository_user=repository_user,
            repository_status=repository_status,
            repository_query=repository_query,
        )
        data = {"tg_id": str(message.from_user.id), "status_name": "waiting file"}
        answer = await service_user.check_status(data)
        if answer:
            # Скачиваем файл
            file = await bot.get_file(message.document.file_id)
            downloaded_file = await bot.download_file(file.file_path)
            result_message = await service_user.analyze_data_from_user(
                data, downloaded_file
            )
            # Разбиваем сообщение на части
            if len(result_message) > 4000:
                parts = [
                    result_message[i : i + 4000]
                    for i in range(0, len(result_message), 4000)
                ]
                for part in parts:
                    await message.answer(part, reply_markup=keyboard)
            else:
                await message.answer(result_message, reply_markup=keyboard)

            # Обновляем статус
            await service_user.create_or_update_user(
                {"tg_id": str(message.from_user.id), "status_name": "start"}
            )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    executor.start_polling(dp, skip_updates=True)

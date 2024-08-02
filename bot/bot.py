from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters.command import Command
from aiogram.enums import ParseMode
import asyncio
import aiohttp
from envparse import Env

env = Env()

API_TOKEN = env.str("TELEGRAM_TOKEN", default="TELEGRAM_TOKEN")
API_URL = "http://fastapi_app:8000/api/v1/"


dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет! Я бот. Напиши /show, чтобы показать сообщения, или отправь мне свое сообщение для записи в БД."
    )


@dp.message(Command("show"))
async def cmd_show(message: types.Message):
    page = 1
    full_list = []
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}messages/?page={page}") as response:
                if response.status == 200:
                    messages = await response.json()
                    result = messages.get("result", [])
                    if not result:
                        break
                    full_list.extend(result)
                    page += 1
                else:
                    await message.answer(
                        f"Ошибка при получении сообщений. Код статуса: {response.status}"
                    )
                    return
    if full_list:
        formatted_result = "\n".join(str(msg) for msg in full_list)
        try:
            await message.answer(formatted_result)
        except Exception as e:
            await message.answer(f"Произошла ошибка при отправке сообщения: {str(e)}")
    else:
        await message.answer("Сообщений пока нет.")


@dp.message()
async def cmd_send(message: types.Message):
    data = {"author": message.from_user.username, "text": message.text}
    if data:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{API_URL}message/", json=data) as response:
                    if response.status == 200:
                        await message.answer("Сообщение успешно отправлено.")
                    else:
                        error_message = await response.text()
                        await message.answer(
                            f"Не удалось отправить сообщение. Ошибка: {error_message}"
                        )
        except Exception as e:
            await message.answer(f"Произошла ошибка: {str(e)}")


async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
import redis
from google.genai import types as google_types
from google import genai

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = '7381587751:AAFId-MmspFToMOxlV87_OEqS98C7ddgAKE'
gemini_api = 'AIzaSyCtgCMK6wovz5H7WOeEsiV-LCVoP1tEnQM'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

client = genai.Client(api_key=gemini_api)

@dp.message(CommandStart())
async def start_command(message: Message):
    user_id = str(message.from_user.id)
    if not redis_client.exists(user_id):
        redis_client.set(user_id, json.dumps([]))
    await message.answer("Привет! Я крутой бизнескоуч. Чем могу помочь?")

@dp.message()
async def handle_message(message: Message):
    user_id = str(message.from_user.id)
    user_input = message.text

    if not redis_client.exists(user_id):
        redis_client.set(user_id, json.dumps([]))

    history = json.loads(redis_client.get(user_id))
    history.append({"role": "user", "content": user_input})

    try:
        formatted_history = "\n".join([msg["content"] for msg in history])

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=formatted_history,
            config=google_types.GenerateContentConfig(
                system_instruction="Ты профессиональный бизнес ассистент. Ты должен помогать бизнесменам всеми возможными способами. Пиши ответы без форматирования (без звёздочек)"
            )
        )

        bot_response = response.text
        print(bot_response)

        history.append({"role": "bot", "content": bot_response})
        redis_client.set(user_id, json.dumps(history))

        await message.answer(bot_response)

    except Exception as e:
        logging.error(f"Ошибка {e}")
        await message.answer("Извините, произошла ошибка. Попробуйте позже.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
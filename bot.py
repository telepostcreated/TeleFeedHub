import asyncio
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telethon import TelegramClient, sync

# Настройки для Telethon
API_ID = os.getenv("API_ID")  # Добавьте свои значения
API_HASH = os.getenv("API_HASH")  # Добавьте свои значения

# Настройки для aiogram
BOT_TOKEN = ("8814954306:AAFpwg1Kbp38LUYt4FAYXKgPMkdfLuLpVfk")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

user_channels = {}
client = TelegramClient('session_name', API_ID, API_HASH)

async def fetch_channel_posts(channel_id):
    try:
        async with client:
            # Получаем последние 10 постов
            posts = await client.get_messages(channel_id, limit=10)
            return [post for post in posts if post.date > datetime.now() - timedelta(days=2)]
    except Exception as e:
        print(f"Ошибка при получении постов: {e}")
        return []

async def get_random_post(user_id):
    channels = user_channels.get(user_id, [])
    all_posts = []
    
    for channel in channels:
        posts = await fetch_channel_posts(channel)
        all_posts.extend(posts)
    
    if all_posts:
        return random.choice(all_posts)
    return None

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет!\n\n"
        "Отправь список каналов, по одному в строке.\n\n"
        "Например:\n"
        "@meduza\n"
        "@vcnews"
    )

@dp.message(F.text.startswith("@"))
async def save_channels(message: Message):
    channels = [x.strip() for x in message.text.splitlines() if x.strip()]
    user_channels[message.from_user.id] = channels

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Сохранить", callback_data="save")
    kb.button(text="✏️ Изменить", callback_data="edit")
    kb.adjust(2)

    await message.answer(
        "Твои каналы:\n\n" + "\n".join(channels),
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data == "save")
async def save(callback: CallbackQuery):
    post = await get_random_post(callback.from_user.id)
    
    if post:
        kb = InlineKeyboardBuilder()
        kb.button(text="⬅️ Назад", callback_data="prev")
        kb.button(text="➡️ Далее", callback_data="next")
        kb.adjust(2)
        
        await callback.message.edit_text(
            f"{post.message}\n\nИсточник: {post.chat.title}",
            reply_markup=kb.as_markup()
        )
    else:
        await callback.message.edit_text("Постов не найдено")

@dp.callback_query(F.data.in_(["next", "prev"]))
async def nav(callback: CallbackQuery):
    post = await get_random_post(callback.from_user.id)
    
    if post:
        kb = InlineKeyboardBuilder()
        kb.button(text="⬅️ Назад", callback_data="prev")
        kb.button(text="➡️ Далее", callback_data="next")
        kb.adjust(2)
        
        await callback.message.edit_text(
            f"{post.message}\n\nИсточник: {post.chat.title}",
            reply_markup=kb.as_markup()
        )
    else:
        await callback.message.edit_text("Постов не найдено")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

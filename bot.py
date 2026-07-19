import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в Variables Railway")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

user_channels = {}


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
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="prev")
    kb.button(text="➡️ Далее", callback_data="next")
    kb.adjust(2)

    await callback.message.edit_text(
        "📰 Здесь позже будет случайный пост из выбранных каналов.",
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data == "edit")
async def edit(callback: CallbackQuery):
    await callback.message.edit_text(
        "Отправь список каналов заново."
    )


@dp.callback_query(F.data.in_(["next", "prev"]))
async def nav(callback: CallbackQuery):
    await callback.answer(
        "В полной версии здесь будет переключение постов."
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

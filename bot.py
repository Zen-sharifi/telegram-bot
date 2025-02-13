import logging
import asyncio
import aiosqlite
import pandas as pd
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing! Make sure it's set in Environment Variables.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

async def create_db():
    async with aiosqlite.connect("users.db") as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    name TEXT,
                    age INTEGER,
                    skill TEXT,
                    phone TEXT)''')
        await db.commit()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("👋 خوش آمدید! لطفاً اطلاعات خود را ارسال کنید.")

@dp.message()
async def register(message: types.Message):
    user_id = message.from_user.id

    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = await cursor.fetchone()

        if user:
            await message.answer("⚠️ شما قبلاً ثبت‌نام کرده‌اید!")
        else:
            user_data = message.text.split("\n")
            if len(user_data) < 4:
                await message.answer("❌ لطفاً اطلاعات را در ۴ خط ارسال کنید.")
            else:
                name, age, skill, phone = user_data
                await db.execute("INSERT INTO users (user_id, name, age, skill, phone) VALUES (?, ?, ?, ?, ?)",
                               (user_id, name, age, skill, phone))
                await db.commit()
                await message.answer("✅ اطلاعات شما ذخیره شد!")

async def main():
    await create_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

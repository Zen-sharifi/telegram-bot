import logging
import asyncio
import aiosqlite
import pandas as pd
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn

# دریافت توکن از متغیر محیطی
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing! Make sure it's set in Environment Variables.")

# راه‌اندازی ربات و دیسپچر
bot = Bot(token=TOKEN)
dp = Dispatcher()

# تنظیمات لاگ‌گیری
logging.basicConfig(level=logging.INFO)

# ایجاد دیتابیس
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

# پیام خوش‌آمدگویی
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

# ایجاد وب سرور برای فعال نگه داشتن سرویس در Render
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Bot is running!"}

async def main():
    await create_db()
    asyncio.create_task(dp.start_polling(bot))  # اجرای ربات در پس‌زمینه
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))  # اجرای وب سرور

if __name__ == "__main__":
    asyncio.run(main())

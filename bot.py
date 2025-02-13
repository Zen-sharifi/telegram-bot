import os
import logging
import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")  # دریافت توکن از متغیر محیطی

bot = Bot(token=TOKEN)
dp = Dispatcher()

# تنظیمات لاگ‌گیری
logging.basicConfig(level=logging.INFO)

# ایجاد دیتابیس کاربران
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
async def start_command(message: Message):
    await message.answer("👋 خوش آمدید! لطفاً اطلاعات خود را ارسال کنید.\n"
                         "نام و نام خانوادگی\n"
                         "سن\n"
                         "مهارت\n"
                         "شماره تماس")

# ثبت اطلاعات کاربر
@dp.message(lambda message: not message.text.startswith('/'))
async def register(message: Message):
    user_id = message.from_user.id
    user_data = message.text.split("\n")

    if len(user_data) < 4:
        await message.answer("❌ لطفاً اطلاعات را در ۴ خط ارسال کنید:\n"
                             "1️⃣ نام و نام خانوادگی\n"
                             "2️⃣ سن\n"
                             "3️⃣ مهارت یا شغل\n"
                             "4️⃣ شماره تماس")
        return

    name, age, skill, phone = user_data

    async with aiosqlite.connect("users.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, name, age, skill, phone) VALUES (?, ?, ?, ?, ?)",
                         (user_id, name, age, skill, phone))
        await db.commit()

    await message.answer("✅ اطلاعات شما ذخیره شد!")

# اجرای بات
async def main():
    await create_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

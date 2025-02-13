import logging
import asyncio
import aiosqlite
import os
from aiogram import Bot, Dispatcher, types

# دریافت توکن از متغیر محیطی (نه مستقیم در کد)
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN مقداردهی نشده است!")

# راه‌اندازی ربات و دیسپچر
bot = Bot(token=TOKEN)
dp = Dispatcher()

# تنظیمات لاگ‌گیری
logging.basicConfig(level=logging.INFO)

# ایجاد دیتابیس (استفاده از aiosqlite به‌صورت async)
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
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("👋 خوش آمدید! لطفاً اطلاعات خود را برای ثبت‌نام ارسال کنید:\n"
                         "1️⃣ نام و نام خانوادگی\n"
                         "2️⃣ سن\n"
                         "3️⃣ مهارت یا شغل\n"
                         "4️⃣ شماره تماس")

@dp.message_handler(lambda message: not message.text.startswith('/'))
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
                await message.answer("❌ لطفاً اطلاعات را در ۴ خط ارسال کنید:\n"
                                     "1️⃣ نام و نام خانوادگی\n"
                                     "2️⃣ سن\n"
                                     "3️⃣ مهارت یا شغل\n"
                                     "4️⃣ شماره تماس")
            else:
                name, age, skill, phone = user_data
                await db.execute("INSERT INTO users (user_id, name, age, skill, phone) VALUES (?, ?, ?, ?, ?)",
                               (user_id, name, age, skill, phone))
                await db.commit()
                await message.answer("✅ اطلاعات شما با موفقیت ذخیره شد!")

# اجرای ربات
async def main():
    await create_db()  # اجرای تابع ایجاد دیتابیس
    print("✅ Bot is running...")  # نمایش لاگ در Render
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

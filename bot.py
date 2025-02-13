import logging
import asyncio
import sqlite3
import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "7664252081:AAE909gJMA9fzvpeGMNT2UNdkZ3R9MpOq80"

# راه‌اندازی ربات و دیسپچر
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# تنظیمات لاگ‌گیری
logging.basicConfig(level=logging.INFO)

# ایجاد دیتابیس
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    name TEXT,
                    age INTEGER,
                    skill TEXT,
                    phone TEXT)''')
conn.commit()

# پیام خوش‌آمدگویی
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("👋 خوش آمدید! لطفاً برای ثبت‌نام اطلاعات خود را وارد کنید.\n"
                         "نام و نام خانوادگی خود را ارسال کنید:")

@dp.message_handler(lambda message: not message.text.startswith('/'))
async def register(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if user:
        await message.answer("⚠️ شما قبلاً ثبت‌نام کرده‌اید!")
    else:
        user_data = message.text.split("\n")
        if len(user_data) < 4:
            await message.answer("❌ لطفاً اطلاعات را در ۴ خط ارسال کنید: \n"
                                 "1️⃣ نام و نام خانوادگی\n"
                                 "2️⃣ سن\n"
                                 "3️⃣ مهارت یا شغل\n"
                                 "4️⃣ شماره تماس")
        else:
            name, age, skill, phone = user_data
            cursor.execute("INSERT INTO users (user_id, name, age, skill, phone) VALUES (?, ?, ?, ?, ?)",
                           (user_id, name, age, skill, phone))
            conn.commit()
            await message.answer("✅ اطلاعات شما با موفقیت ذخیره شد!")

# خروجی اکسل
@dp.message_handler(commands=['export'])
async def export_users(message: types.Message):
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()

    if not data:
        await message.answer("⚠️ هنوز هیچ کاربری ثبت‌نام نکرده است!")
        return

    df = pd.DataFrame(data, columns=["ID", "User ID", "نام", "سن", "مهارت", "شماره تماس"])
    file_path = "users.xlsx"
    df.to_excel(file_path, index=False)

    with open(file_path, "rb") as file:
        await bot.send_document(message.chat.id, file, caption="📄 لیست کاربران")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

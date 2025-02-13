import logging
import asyncio
import aiosqlite
import pandas as pd
import os
from aiogram import Bot, Dispatcher, types

TOKEN = os.getenv("BOT_TOKEN")  # دریافت توکن از متغیر محیطی
ADMIN_ID = 123456789  # آیدی تلگرام مدیر (جایگزین کن)

bot = Bot(token=TOKEN)
dp = Dispatcher()

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

# پیام خوش‌آمدگویی و دریافت اطلاعات
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("👋 خوش آمدید! لطفاً برای ثبت‌نام اطلاعات خود را وارد کنید:\n"
                         "نام و نام خانوادگی\n"
                         "سن\n"
                         "مهارت یا شغل\n"
                         "شماره تماس\n\n"
                         "📌 اطلاعات را در ۴ خط جداگانه ارسال کنید!")

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
                await message.answer("❌ لطفاً اطلاعات را در ۴ خط ارسال کنید: \n"
                                     "1️⃣ نام و نام خانوادگی\n"
                                     "2️⃣ سن\n"
                                     "3️⃣ مهارت یا شغل\n"
                                     "4️⃣ شماره تماس")
            else:
                name, age, skill, phone = user_data
                await db.execute("INSERT INTO users (user_id, name, age, skill, phone) VALUES (?, ?, ?, ?, ?)",
                               (user_id, name, age, skill, phone))
                await db.commit()
                await message.answer("✅ اطلاعات شما ذخیره شد!\n\n📢 برای دریافت اخبار، به کانال تلگرام ما بپیوندید:\n👉 [کلیک کنید](https://t.me/zensharifi)", parse_mode="Markdown")

# دریافت اطلاعات کاربران در تلگرام (فقط برای مدیر)
@dp.message_handler(commands=['users'])
async def send_users_list(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ شما اجازه دسترسی به این بخش را ندارید!")
        return

    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT name, age, skill, phone FROM users")
        users = await cursor.fetchall()

    if not users:
        await message.answer("⚠️ هنوز هیچ کاربری ثبت‌نام نکرده است!")
        return

    response = "📋 **لیست کاربران:**\n"
    for user in users:
        response += f"👤 {user[0]} | 🎂 {user[1]} | 💼 {user[2]} | 📞 {user[3]}\n"

    await message.answer(response, parse_mode="Markdown")

# دریافت خروجی اکسل (فقط برای مدیر)
@dp.message_handler(commands=['export'])
async def export_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ شما اجازه دسترسی به این بخش را ندارید!")
        return

    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM users")
        data = await cursor.fetchall()

    if not data:
        await message.answer("⚠️ هنوز هیچ کاربری ثبت‌نام نکرده است!")
        return

    df = pd.DataFrame(data, columns=["ID", "User ID", "نام", "سن", "مهارت", "شماره تماس"])
    file_path = "users.xlsx"
    df.to_excel(file_path, index=False)

    with open(file_path, "rb") as file:
        await bot.send_document(message.chat.id, file, caption="📄 لیست کاربران")

# اجرای ربات
async def main():
    await create_db()  
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

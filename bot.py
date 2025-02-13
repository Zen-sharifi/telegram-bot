import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types

# دریافت توکن از متغیر محیطی
TOKEN = os.getenv("BOT_TOKEN")

# بررسی معتبر بودن توکن
if not TOKEN:
    raise ValueError("🚨 BOT_TOKEN مقداردهی نشده است! لطفا آن را در Environment Variables تنظیم کنید.")

# راه‌اندازی ربات و Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# تنظیمات لاگ‌گیری
logging.basicConfig(level=logging.INFO)

# پیام خوش‌آمدگویی
@dp.message(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("👋 خوش آمدید! لطفاً برای ثبت‌نام اطلاعات خود را وارد کنید.")

# اجرای ربات
async def main():
    print("🚀 ربات در حال اجرا است...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

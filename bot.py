import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7851061564:AAH0L5XyBG5I5Bigbgo3LqKRigdNUL-a1EU')

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Создаем клавиатуру с веб-приложением
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть FPV Shop", 
            web_app=WebAppInfo(url="https://user1058713465-a2ywwjwz.tunnel.vk-apps.com/")
        )]
    ])
    
    await message.answer(
        "Добро пожаловать! Откройте магазин:", 
        reply_markup=markup
    )

# Функция запуска бота
async def main():
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
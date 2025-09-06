import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота (получить у @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# URL вашего FastAPI сервера
API_URL = os.getenv("API_URL", "http://localhost:8000")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚗 Открыть поддержку", 
            web_app=WebAppInfo(url=f"{API_URL}/webapp")
        )]
    ])
    
    await message.answer(
        "👋 Добро пожаловать в службу поддержки такси!\n\n"
        "Я помогу вам с:\n"
        "• Статусом поездки\n"
        "• Получением чеков\n"
        "• Работой с картами\n"
        "• Ответами на вопросы\n\n"
        "Нажмите кнопку ниже, чтобы открыть чат поддержки:",
        reply_markup=keyboard
    )

@dp.message(Command("help"))
async def help_handler(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
🤖 **Команды бота:**

/start - Начать работу с ботом
/help - Показать эту справку
/support - Открыть чат поддержки

📱 **Возможности:**
• Проверить статус поездки
• Получить чек за поездку
• Управлять картами оплаты
• Задать вопрос из FAQ
• Пожаловаться на проблему

💬 **Примеры вопросов:**
• "Где мой водитель?"
• "Пришлите чек"
• "Как считается цена?"
• "С меня списали дважды"
"""
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("support"))
async def support_handler(message: types.Message):
    """Обработчик команды /support"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💬 Открыть чат поддержки", 
            web_app=WebAppInfo(url=f"{API_URL}/webapp")
        )]
    ])
    
    await message.answer(
        "💬 Откройте чат поддержки для общения с ИИ-ассистентом:",
        reply_markup=keyboard
    )

@dp.message()
async def text_handler(message: types.Message):
    """Обработчик текстовых сообщений - перенаправляет в WebApp"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💬 Открыть чат поддержки", 
            web_app=WebAppInfo(url=f"{API_URL}/webapp")
        )]
    ])
    
    await message.answer(
        f"💬 Для обработки вашего сообщения '{message.text}' откройте чат поддержки:",
        reply_markup=keyboard
    )

async def main():
    """Запуск бота"""
    logger.info("Запуск Telegram бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

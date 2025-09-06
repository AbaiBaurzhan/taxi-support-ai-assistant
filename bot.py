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
API_URL = os.getenv("API_URL", "https://taxi-support-ai-assistant-production.up.railway.app")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚗 Открыть поддержку", 
            web_app=WebAppInfo(url=f"{API_URL}/webapp?v=2.3&cache=bust&t={int(__import__('time').time())}")
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
            web_app=WebAppInfo(url=f"{API_URL}/webapp?v=2.3&cache=bust&t={int(__import__('time').time())}")
        )]
    ])
    
    await message.answer(
        "💬 Откройте чат поддержки для общения с ИИ-ассистентом:",
        reply_markup=keyboard
    )

@dp.message()
async def text_handler(message: types.Message):
    """Обработчик текстовых сообщений - обрабатывает через API"""
    try:
        # Показываем индикатор печати
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Отправляем запрос к API
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/chat",
                json={
                    "text": message.text,
                    "user_id": str(message.from_user.id),
                    "locale": message.from_user.language_code or "RU"
                },
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response", "Извините, не удалось получить ответ.")
                    
                    # Добавляем информацию об источнике ответа
                    source = data.get("source", "unknown")
                    if source == "kb":
                        response_text += "\n\n📚 Ответ из базы знаний"
                    elif source == "llm":
                        response_text += "\n\n🤖 Ответ от ИИ"
                    
                    await message.answer(response_text)
                else:
                    await message.answer("Извините, произошла ошибка при обработке запроса.")
                    
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")
        await message.answer("Извините, произошла ошибка. Попробуйте позже.")
        
        # Предлагаем открыть WebApp как альтернативу
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="💬 Открыть чат поддержки", 
                web_app=WebAppInfo(url=f"{API_URL}/webapp?v=2.3&cache=bust&t={int(__import__('time').time())}")
            )]
        ])
        await message.answer("Или попробуйте открыть чат поддержки:", reply_markup=keyboard)

async def main():
    """Запуск бота"""
    logger.info("Запуск Telegram бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

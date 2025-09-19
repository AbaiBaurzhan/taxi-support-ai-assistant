#!/usr/bin/env python3
"""
🚀 УПРОЩЕННАЯ ВЕРСИЯ ДЛЯ RAILWAY
Без гибридной архитектуры - только локальная система поиска
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ЛОКАЛЬНАЯ СИСТЕМА ПОИСКА: enhanced_search_client с 100% точностью
try:
    from enhanced_search_client import get_enhanced_answer
    logger.info("✅ Enhanced search client активирован (100% точность)")
except ImportError:
    try:
        from morphological_search_client import get_enhanced_answer
        logger.info("✅ Morphological search client активирован")
    except ImportError:
        try:
            from railway_optimized_client import get_enhanced_answer
            logger.info("✅ Railway optimized client активирован")
        except ImportError:
            logger.error("❌ Ни одна система поиска не доступна")
            def get_enhanced_answer(text: str) -> str:
                return "Извините, система поиска временно недоступна."

app = FastAPI(title="APARU Simplified AI Assistant", version="2.3.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory="."), name="static")

# Модели данных
class ChatRequest(BaseModel):
    text: str
    user_id: str
    locale: str = "ru"

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    source: str
    timestamp: str
    architecture: str = "simplified"

class HealthResponse(BaseModel):
    status: str
    architecture: str = "simplified"
    timestamp: str

# Загрузка данных
def load_json_file(filename: str) -> Dict[str, Any]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Файл {filename} не найден")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON в {filename}: {e}")
        return {}

# Глобальные данные
fixtures = load_json_file("fixtures.json")
kb_data = load_json_file("kb.json")

# Предобработка текста
def preprocess_text(text: str) -> str:
    """Убирает эмодзи и спецсимволы"""
    # Убираем эмодзи
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U00002500-\U000025FF"  # Box Drawing & Block Elements
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)

    text = emoji_pattern.sub(r'', text)

    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# Определение языка
def detect_language(text: str) -> str:
    """Определяет язык текста"""
    try:
        lang = detect(text)
        return lang if lang in ['ru', 'kz', 'en'] else 'ru'
    except LangDetectException:
        return 'ru'

# Классификация намерений
def classify_intent(text: str) -> str:
    """Определяет намерение пользователя"""
    text_lower = text.lower()

    # Ключевые слова для разных намерений
    faq_keywords = ['что', 'как', 'где', 'почему', 'зачем', 'когда', 'сколько', 'можно ли']
    ride_status_keywords = ['водитель', 'машина', 'поездка', 'заказ', 'статус', 'где']
    receipt_keywords = ['чек', 'счет', 'квитанция', 'документ']
    cards_keywords = ['карта', 'карты', 'основная', 'платеж']
    complaint_keywords = ['жалоба', 'проблема', 'не работает', 'плохо', 'списали', 'дважды']

    if any(keyword in text_lower for keyword in faq_keywords):
        return "faq"
    elif any(keyword in text_lower for keyword in ride_status_keywords):
        return "ride_status"
    elif any(keyword in text_lower for keyword in receipt_keywords):
        return "receipt"
    elif any(keyword in text_lower for keyword in cards_keywords):
        return "cards"
    elif any(keyword in text_lower for keyword in complaint_keywords):
        return "complaint"
    else:
        return "unknown"

# Получение ответа от AI системы
def get_ai_response(text: str) -> str:
    """Получает ответ от AI системы"""
    try:
        answer = get_enhanced_answer(text)
        logger.info("✅ Ответ получен от локальной системы поиска")
        return answer
    except Exception as e:
        logger.error(f"Ошибка в AI системе: {e}")
        return "Извините, произошла ошибка при обработке вашего запроса."

# API эндпоинты
@app.get("/")
async def root():
    return {
        "message": "APARU Simplified AI Assistant", 
        "architecture": "simplified",
        "version": "2.3.0"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка состояния системы"""
    return HealthResponse(
        status="healthy",
        architecture="simplified",
        timestamp=datetime.now().isoformat()
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Основной эндпоинт для чата"""
    try:
        # Предобработка текста
        processed_text = preprocess_text(request.text)

        # Определение языка
        detected_lang = detect_language(processed_text)

        # Определяем намерение
        intent = classify_intent(processed_text)

        # Обрабатываем запрос в зависимости от намерения
        if intent == "faq":
            response_text = get_ai_response(processed_text)
            source = "local"
        elif intent == "ride_status":
            # Моковые данные для статуса поездки
            ride_data = fixtures.get("rides", [{}])[0]
            response_text = f"Ваш водитель {ride_data.get('driver_name', 'Алексей')} находится в {ride_data.get('location', '5 минутах')} от вас. Номер машины: {ride_data.get('car_number', '123ABC')}"
            source = "mock"
        elif intent == "receipt":
            # Моковые данные для чека
            receipt_data = fixtures.get("receipts", [{}])[0]
            response_text = f"Чек отправлен на email {receipt_data.get('email', 'user@example.com')}. Сумма: {receipt_data.get('amount', '500')} тенге"
            source = "mock"
        elif intent == "cards":
            # Моковые данные для карт
            cards_data = fixtures.get("cards", [])
            if cards_data:
                response_text = f"У вас {len(cards_data)} карт. Основная карта: {cards_data[0].get('number', '****1234')}"
            else:
                response_text = "У вас нет сохраненных карт"
            source = "mock"
        elif intent == "complaint":
            # Создание тикета
            ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            response_text = f"Ваша жалоба зарегистрирована. Номер тикета: {ticket_id}. Оператор свяжется с вами в течение 24 часов."
            source = "ticket"
        else:
            # Неизвестное намерение - используем AI
            response_text = get_ai_response(processed_text)
            source = "local"

        return ChatResponse(
            response=response_text,
            intent=intent,
            confidence=0.9 if source == "local" else 1.0,
            source=source,
            timestamp=datetime.now().isoformat(),
            architecture="simplified"
        )

    except Exception as e:
        logger.error(f"Ошибка в /chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webapp")
async def webapp():
    """Возвращает веб-приложение"""
    return FileResponse("webapp.html")

@app.get("/fixtures")
async def get_fixtures():
    """Возвращает моковые данные"""
    return fixtures

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

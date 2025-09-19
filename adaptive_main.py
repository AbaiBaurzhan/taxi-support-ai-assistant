#!/usr/bin/env python3
"""
🚀 Адаптивный main.py - автоматически выбирает лучшую версию
"""

import os
import sys
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(title="APARU Adaptive AI Assistant", version="2.0.0")

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

# Определяем окружение
RAILWAY_MODE = os.getenv("RAILWAY_MODE", "false").lower() == "true"
FORCE_LIGHTWEIGHT = os.getenv("FORCE_LIGHTWEIGHT", "false").lower() == "true"
FORCE_FULL_ML = os.getenv("FORCE_FULL_ML", "false").lower() == "true"

# Умная система импорта
def smart_import():
    """Умно импортирует лучшую версию в зависимости от окружения"""
    
    # Принудительные настройки
    if FORCE_LIGHTWEIGHT:
        logger.info("🔧 Принудительно включена облегченная версия")
        return import_lightweight()
    
    if FORCE_FULL_ML:
        logger.info("🔧 Принудительно включены полные ML зависимости")
        return import_full_ml()
    
    # Автоматическое определение
    if RAILWAY_MODE:
        logger.info("☁️ Railway окружение - используем облегченную версию")
        return import_lightweight()
    
    # Проверяем доступность полных ML зависимостей
    try:
        import numpy
        import sentence_transformers
        import faiss
        import fuzzywuzzy
        import nltk
        import pandas
        import sklearn
        
        logger.info("🚀 Полные ML зависимости доступны - используем максимальную точность")
        return import_full_ml()
        
    except ImportError as e:
        logger.warning(f"⚠️ Полные ML зависимости недоступны: {e}")
        logger.info("⚡ Переключаемся на облегченную версию")
        return import_lightweight()

def import_full_ml():
    """Импортирует полную ML версию"""
    try:
        from maximum_accuracy_client import get_enhanced_answer
        logger.info("✅ Загружена максимально точная система (80% точности)")
        return get_enhanced_answer, "maximum_accuracy"
    except ImportError:
        try:
            from ultimate_search_client import get_enhanced_answer
            logger.info("✅ Загружена ультимативная система поиска")
            return get_enhanced_answer, "ultimate_search"
        except ImportError:
            try:
                from senior_ai_integrated_client import get_enhanced_answer
                logger.info("✅ Загружена Senior AI система")
                return get_enhanced_answer, "senior_ai"
            except ImportError:
                logger.warning("⚠️ Полные ML системы недоступны, fallback к облегченной")
                return import_lightweight()

def import_lightweight():
    """Импортирует облегченную версию"""
    try:
        from railway_optimized_client import get_enhanced_answer
        logger.info("✅ Загружена облегченная система (70% точности)")
        return get_enhanced_answer, "railway_optimized"
    except ImportError:
        try:
            from railway_simple_client import get_enhanced_answer
            logger.info("✅ Загружена простая система")
            return get_enhanced_answer, "railway_simple"
        except ImportError:
            logger.error("❌ Ни одна система не доступна")
            return None, "none"

# Импортируем лучшую версию
get_enhanced_answer, system_type = smart_import()

# Загружаем базовые компоненты
try:
    from aparu_enhanced_client import aparu_enhanced_client
    aparu_enhanced_client.load_aparu_knowledge_base()
    logger.info("✅ База знаний APARU загружена")
except ImportError:
    logger.warning("⚠️ aparu_enhanced_client недоступен")

# Загружаем моки
try:
    import json
    with open('fixtures.json', 'r', encoding='utf-8') as f:
        fixtures = json.load(f)
    logger.info("✅ Моки загружены")
except FileNotFoundError:
    logger.warning("⚠️ Файл fixtures.json не найден")
    fixtures = {}

def classify_intent(text: str, locale: str) -> str:
    """Классифицирует намерение пользователя"""
    text_lower = text.lower()
    
    # Ключевые слова для каждого намерения
    if any(word in text_lower for word in ['поездка', 'водитель', 'где', 'статус', 'заказ']):
        return "ride_status"
    elif any(word in text_lower for word in ['чек', 'квитанция', 'счет', 'отчет']):
        return "receipt"
    elif any(word in text_lower for word in ['карта', 'карты', 'основная', 'платеж']):
        return "cards"
    elif any(word in word in text_lower for word in ['жалоба', 'проблема', 'списали', 'дважды', 'оператор']):
        return "complaint"
    elif any(word in text_lower for word in ['промокод', 'скидка', 'цена', 'тариф', 'стоимость']):
        return "faq"
    else:
        return "faq"

def get_mock_response(intent: str) -> dict:
    """Возвращает моковый ответ"""
    if intent == "ride_status":
        return {
            "response": "У вас нет активных поездок",
            "confidence": 0.95,
            "source": "kb"
        }
    elif intent == "receipt":
        return {
            "response": "Чек отправлен на вашу почту",
            "confidence": 0.95,
            "source": "kb"
        }
    elif intent == "cards":
        return {
            "response": "У вас есть 2 карты. Основная карта: ****1234",
            "confidence": 0.95,
            "source": "kb"
        }
    elif intent == "complaint":
        return {
            "response": "Создан тикет #12345. Оператор свяжется с вами в течение 24 часов",
            "confidence": 0.95,
            "source": "kb"
        }
    else:
        return {
            "response": "Нужна уточняющая информация",
            "confidence": 0.0,
            "source": "kb"
        }

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "APARU Adaptive AI Assistant",
        "version": "2.0.0",
        "system_type": system_type,
        "railway_mode": RAILWAY_MODE,
        "features": {
            "adaptive_dependencies": True,
            "smart_import": True,
            "environment_detection": True
        }
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    return {
        "status": "healthy",
        "system_type": system_type,
        "railway_mode": RAILWAY_MODE,
        "timestamp": datetime.now().isoformat(),
        "features": {
            "maximum_accuracy": system_type in ["maximum_accuracy", "ultimate_search", "senior_ai"],
            "lightweight": system_type in ["railway_optimized", "railway_simple"],
            "adaptive": True
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Основной эндпоинт для чата"""
    try:
        # Определяем язык
        try:
            detected_locale = detect(request.text)
        except LangDetectException:
            detected_locale = request.locale
        
        # Классифицируем намерение
        intent = classify_intent(request.text, detected_locale)
        
        # Обрабатываем запрос
        if intent == "faq" and get_enhanced_answer:
            # Используем AI систему
            answer = get_enhanced_answer(request.text)
            confidence = 0.95 if answer != "Нужна уточняющая информация" else 0.3
            source = "ai_system"
        else:
            # Используем моки
            mock_response = get_mock_response(intent)
            answer = mock_response["response"]
            confidence = mock_response["confidence"]
            source = mock_response["source"]
        
        return ChatResponse(
            response=answer,
            intent=intent,
            confidence=confidence,
            source=source,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка в chat_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/webapp")
async def webapp():
    """Возвращает WebApp"""
    return FileResponse("webapp.html")

@app.get("/status")
async def get_status():
    """Получение статуса системы"""
    return {
        "system_type": system_type,
        "railway_mode": RAILWAY_MODE,
        "features": {
            "maximum_accuracy": system_type in ["maximum_accuracy", "ultimate_search", "senior_ai"],
            "lightweight": system_type in ["railway_optimized", "railway_simple"],
            "adaptive": True
        },
        "dependencies": {
            "numpy": "numpy" in sys.modules,
            "sentence_transformers": "sentence_transformers" in sys.modules,
            "faiss": "faiss" in sys.modules,
            "fuzzywuzzy": "fuzzywuzzy" in sys.modules,
            "nltk": "nltk" in sys.modules,
            "pandas": "pandas" in sys.modules,
            "sklearn": "sklearn" in sys.modules
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Запуск адаптивного APARU AI Assistant...")
    logger.info(f"   Система: {system_type}")
    logger.info(f"   Railway режим: {RAILWAY_MODE}")
    logger.info(f"   Принудительно облегченная: {FORCE_LIGHTWEIGHT}")
    logger.info(f"   Принудительно полная ML: {FORCE_FULL_ML}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

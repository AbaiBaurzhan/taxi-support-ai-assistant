#!/usr/bin/env python3
"""
☁️ Легкий Railway API - только пересылка запросов
Без AI модели, только маршрутизация
"""

import requests
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(title="APARU Lightweight API", version="1.0.0")

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

# Конфигурация
LOCAL_MODEL_URL = os.getenv("LOCAL_MODEL_URL", "http://localhost:11434")
RAILWAY_MODE = os.getenv("RAILWAY_MODE", "true").lower() == "true"

class LightweightAPIClient:
    def __init__(self):
        self.local_model_available = False
        self._check_local_model()
    
    def _check_local_model(self):
        """Проверяет доступность локальной модели"""
        try:
            response = requests.get(f"{LOCAL_MODEL_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                self.local_model_available = True
                logger.info("✅ Локальная модель доступна")
            else:
                logger.warning("⚠️ Локальная модель недоступна")
        except Exception as e:
            logger.warning(f"⚠️ Локальная модель недоступна: {e}")
    
    def _query_local_model(self, question: str) -> Optional[str]:
        """Запрашивает ответ у локальной модели"""
        try:
            payload = {
                "model": "aparu-senior-ai",
                "prompt": f"Ответь на вопрос пользователя такси-агрегатора APARU: {question}",
                "stream": False
            }
            
            response = requests.post(
                f"{LOCAL_MODEL_URL}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"❌ Ошибка локальной модели: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка запроса к локальной модели: {e}")
            return None
    
    def get_answer(self, question: str) -> Dict[str, Any]:
        """Получает ответ от локальной модели"""
        if self.local_model_available:
            answer = self._query_local_model(question)
            if answer:
                return {
                    'answer': answer,
                    'source': 'local_model',
                    'confidence': 0.95,
                    'intent': 'faq'
                }
        
        # Fallback ответ
        return {
            'answer': 'Локальная модель недоступна. Проверьте подключение.',
            'source': 'error',
            'confidence': 0.0,
            'intent': 'error'
        }

# Глобальный клиент
api_client = LightweightAPIClient()

@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {
        "status": "healthy",
        "railway_mode": RAILWAY_MODE,
        "local_model_available": api_client.local_model_available,
        "local_model_url": LOCAL_MODEL_URL
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Основной эндпоинт для чата"""
    try:
        # Получаем ответ от локальной модели
        result = api_client.get_answer(request.text)
        
        return ChatResponse(
            response=result['answer'],
            intent=result['intent'],
            confidence=result['confidence'],
            source=result['source'],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка в chat_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/status")
async def get_status():
    """Получение статуса системы"""
    return {
        "railway_mode": RAILWAY_MODE,
        "local_model_available": api_client.local_model_available,
        "local_model_url": LOCAL_MODEL_URL,
        "description": "Легкий API для пересылки запросов к локальной модели"
    }

if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    
    logger.info("🚀 Запуск легкого Railway API...")
    logger.info(f"   Режим Railway: {RAILWAY_MODE}")
    logger.info(f"   URL локальной модели: {LOCAL_MODEL_URL}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

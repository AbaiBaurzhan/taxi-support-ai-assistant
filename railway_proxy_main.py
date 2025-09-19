#!/usr/bin/env python3
"""
🚀 RAILWAY PROXY АРХИТЕКТУРА APARU AI
Railway получает запросы → отправляет на локальный сервер → LLM модель
"""

import json
import re
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="APARU Railway Proxy AI", version="3.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели
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
    suggestions: List[str] = []

class HealthResponse(BaseModel):
    status: str
    architecture: str = "railway_proxy"
    timestamp: str

class RailwayProxyClient:
    def __init__(self):
        # URL локального сервера (нужно настроить)
        self.local_server_url = os.environ.get("LOCAL_SERVER_URL", "http://localhost:8001")
        self.local_available = False
        
        # Проверяем доступность локального сервера
        self._check_local_server()
        
    def _check_local_server(self):
        """Проверяет доступность локального сервера"""
        try:
            response = requests.get(f"{self.local_server_url}/health", timeout=5)
            if response.status_code == 200:
                self.local_available = True
                logger.info("✅ Локальный сервер доступен")
            else:
                logger.warning("⚠️ Локальный сервер недоступен")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к локальному серверу: {e}")
    
    def get_answer(self, question: str) -> Dict[str, Any]:
        """Получает ответ от гибридной системы"""
        start_time = datetime.now()
        
        # Используем локальный сервер с LLM
        if self.local_available:
            try:
                logger.info("🧠 Запрашиваем ответ от локального сервера...")
                response = self._query_local_server(question)
                if response and response.get('response'):
                    processing_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Ответ получен за {processing_time:.2f}с")
                    return response
            except Exception as e:
                logger.error(f"❌ Ошибка при запросе к локальному серверу: {e}")
        
        # Fallback к простому поиску
        logger.info("🔄 Fallback к простому поиску...")
        return self._simple_search(question)
    
    def _query_local_server(self, question: str) -> Dict[str, Any]:
        """Запрашивает ответ от локального сервера"""
        try:
            payload = {
                "text": question,
                "user_id": "railway_proxy",
                "locale": "ru"
            }
            
            response = requests.post(
                f"{self.local_server_url}/chat",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "answer": data.get('response', ''),
                    "category": data.get('intent', 'unknown'),
                    "confidence": data.get('confidence', 0.0),
                    "source": "local_server"
                }
            
            logger.warning(f"⚠️ Локальный сервер вернул неожиданный ответ: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка запроса к локальному серверу: {e}")
            return None
    
    def _simple_search(self, question: str) -> Dict[str, Any]:
        """Улучшенный поиск по ключевым словам (fallback)"""
        question_lower = question.lower()
        
        # Расширенная база знаний с синонимами
        simple_kb = {
            "наценка": {
                "keywords": ["наценка", "дорого", "подорожание", "повышение", "доплата", "наценкa", "наценкy"],
                "answer": "Наценка - это дополнительная плата за повышенный спрос. Она помогает привлечь больше водителей и сократить время ожидания."
            },
            "доставка": {
                "keywords": ["доставка", "курьер", "посылка", "отправить", "заказать", "доставкy", "доставкa", "заказ", "курьерская"],
                "answer": "Для заказа доставки: откройте приложение → выберите 'Доставка' → укажите адреса → подтвердите заказ."
            },
            "баланс": {
                "keywords": ["баланс", "счет", "кошелек", "пополнить", "платеж", "балaнс", "балaнc", "деньги", "оплата"],
                "answer": "Для пополнения баланса: откройте приложение → 'Профиль' → 'Пополнить баланс' → выберите способ оплаты."
            },
            "приложение": {
                "keywords": ["приложение", "программа", "софт", "апп", "работать", "приложениe", "приложениa", "не работает", "ошибка"],
                "answer": "Если приложение не работает: перезапустите, проверьте интернет, обновите до последней версии."
            }
        }
        
        # Улучшенный поиск по ключевым словам и синонимам
        for category, data in simple_kb.items():
            keywords = data["keywords"]
            answer = data["answer"]
            
            # Проверяем каждое ключевое слово
            for keyword in keywords:
                if keyword in question_lower:
                    return {
                        "answer": answer,
                        "category": category,
                        "confidence": 0.8,
                        "source": "enhanced_search"
                    }
        
        # Fallback
        return {
            "answer": "Извините, не могу найти ответ на ваш вопрос. Обратитесь в службу поддержки.",
            "category": "unknown",
            "confidence": 0.0,
            "source": "fallback"
        }

# Глобальный экземпляр
railway_proxy_client = RailwayProxyClient()

@app.get("/")
async def root():
    return {
        "message": "APARU Railway Proxy AI", 
        "status": "running", 
        "version": "3.1.0",
        "architecture": "railway_proxy",
        "local_server_available": railway_proxy_client.local_available
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        architecture="railway_proxy",
        timestamp=datetime.now().isoformat()
    )

@app.get("/webapp", response_class=HTMLResponse)
async def webapp():
    """Telegram WebApp интерфейс"""
    try:
        with open("webapp.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>WebApp не найден</h1><p>Файл webapp.html отсутствует</p>",
            status_code=404
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Основной эндпоинт для чата"""
    try:
        result = railway_proxy_client.get_answer(request.text)
        
        return ChatResponse(
            response=result["answer"],
            intent=result["category"],
            confidence=result["confidence"],
            source=result["source"],
            timestamp=datetime.now().isoformat(),
            suggestions=[]
        )
    
    except Exception as e:
        logger.error(f"Ошибка в /chat: {e}")
        return ChatResponse(
            response="Извините, произошла ошибка при обработке вашего запроса.",
            intent="error",
            confidence=0.0,
            source="error",
            timestamp=datetime.now().isoformat(),
            suggestions=[]
        )

if __name__ == "__main__":
    import uvicorn
    
    # Railway использует переменную PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

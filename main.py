#!/usr/bin/env python3
"""
🚀 ГИБРИДНАЯ АРХИТЕКТУРА APARU AI
LLM модель на ноутбуке + Railway проксирует запросы
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

app = FastAPI(title="APARU Hybrid AI Assistant", version="3.0.0")

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
    architecture: str = "hybrid"
    timestamp: str

class HybridAIClient:
    def __init__(self):
        # URL локальной LLM модели через ngrok
        self.local_model_url = os.environ.get("LOCAL_MODEL_URL", "https://32f43b95cbea.ngrok-free.app")
        self.model_name = "aparu-senior-ai"
        self.local_available = False
        
        # Проверяем доступность локальной модели
        self._check_local_model()
        
    def _check_local_model(self):
        """Проверяет доступность локальной LLM модели"""
        try:
            response = requests.get(
                f"{self.local_model_url}/api/tags", 
                timeout=10,
                headers={"ngrok-skip-browser-warning": "true"}
            )
            if response.status_code == 200:
                self.local_available = True
                logger.info("✅ Локальная LLM модель доступна")
            else:
                logger.warning("⚠️ Локальная LLM модель недоступна")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к локальной модели: {e}")
    
    def get_answer(self, question: str) -> Dict[str, Any]:
        """Получает ответ от гибридной системы"""
        start_time = datetime.now()
        
        # Используем локальную LLM модель
        if self.local_available:
            try:
                logger.info("🧠 Запрашиваем ответ от локальной LLM модели...")
                response = self._query_local_llm(question)
                if response and response.get('response'):
                    processing_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ LLM ответ получен за {processing_time:.2f}с")
                    return response
            except Exception as e:
                logger.error(f"❌ Ошибка при запросе к LLM: {e}")
        
        # Fallback к простому поиску
        logger.info("🔄 Fallback к простому поиску...")
        return self._simple_search(question)
    
    def _query_local_llm(self, question: str) -> Dict[str, Any]:
        """Запрашивает ответ от локальной LLM модели"""
        try:
            # Системный промпт для APARU
            system_prompt = """Ты — AI-ассистент службы поддержки такси-агрегатора APARU. 
Отвечай на вопросы пользователей о:
- Наценках и тарифах
- Доставке и курьерских услугах  
- Балансе и платежах
- Проблемах с приложением

Отвечай кратко, вежливо и по существу. Если не знаешь ответ, предложи обратиться в службу поддержки."""
            
            payload = {
                "model": self.model_name,
                "prompt": f"{system_prompt}\n\nВопрос: {question}",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(
                f"{self.local_model_url}/api/generate",
                json=payload,
                timeout=120,  # Увеличиваем таймаут для LLM
                headers={"ngrok-skip-browser-warning": "true"}
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '').strip()
                
                if answer:
                    return {
                        "answer": answer,
                        "category": "llm_generated",
                        "confidence": 0.9,
                        "source": "local_llm"
                    }
            
            logger.warning(f"⚠️ LLM вернул неожиданный ответ: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка запроса к LLM: {e}")
            return None
    
    def _simple_search(self, question: str) -> Dict[str, Any]:
        """Простой поиск по ключевым словам (fallback)"""
        question_lower = question.lower()
        
        # Простая база знаний
        simple_kb = {
            "наценка": "Наценка - это дополнительная плата за повышенный спрос. Она помогает привлечь больше водителей и сократить время ожидания.",
            "доставка": "Для заказа доставки: откройте приложение → выберите 'Доставка' → укажите адреса → подтвердите заказ.",
            "баланс": "Для пополнения баланса: откройте приложение → 'Профиль' → 'Пополнить баланс' → выберите способ оплаты.",
            "приложение": "Если приложение не работает: перезапустите, проверьте интернет, обновите до последней версии."
        }
        
        # Поиск по ключевым словам
        for keyword, answer in simple_kb.items():
            if keyword in question_lower:
                return {
                    "answer": answer,
                    "category": keyword,
                    "confidence": 0.8,
                    "source": "simple_search"
                }
        
        # Fallback
        return {
            "answer": "Извините, не могу найти ответ на ваш вопрос. Обратитесь в службу поддержки.",
            "category": "unknown",
            "confidence": 0.0,
            "source": "fallback"
        }

# Глобальный экземпляр
hybrid_client = HybridAIClient()

@app.get("/")
async def root():
    return {
        "message": "APARU Hybrid AI Assistant", 
        "status": "running", 
        "version": "3.0.0",
        "architecture": "hybrid",
        "local_model_available": hybrid_client.local_available
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        architecture="hybrid",
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
        result = hybrid_client.get_answer(request.text)
        
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
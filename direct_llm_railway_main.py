#!/usr/bin/env python3
"""
🚀 ПРЯМОЙ LLM КЛИЕНТ ДЛЯ RAILWAY
Railway напрямую подключается к локальной LLM модели
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

app = FastAPI(title="APARU Direct LLM Railway", version="4.0.0")

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
    architecture: str = "direct_llm_railway"
    timestamp: str
    local_llm_available: bool = False

class DirectLLMClient:
    def __init__(self):
        # URL локальной LLM модели
        self.local_llm_url = os.environ.get("LOCAL_LLM_URL", "http://172.20.10.5:8001")
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://172.20.10.5:11434")
        self.model_name = "aparu-senior-ai"
        self.llm_available = False
        
        # Проверяем доступность локальной LLM
        self._check_local_llm()
        
    def _check_local_llm(self):
        """Проверяет доступность локальной LLM модели"""
        try:
            # Проверяем локальный сервер
            response = requests.get(f"{self.local_llm_url}/health", timeout=5)
            if response.status_code == 200:
                self.llm_available = True
                logger.info("✅ Локальная LLM модель доступна")
            else:
                logger.warning(f"⚠️ Локальная LLM модель недоступна: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к локальной LLM модели: {e}")
    
    def get_llm_response(self, question: str) -> Dict[str, Any]:
        """Получает ответ от локальной LLM модели"""
        if not self.llm_available:
            logger.error("❌ Локальная LLM модель недоступна")
            return None
        
        try:
            logger.info("🧠 Запрашиваем ответ от локальной LLM модели...")
            start_time = datetime.now()
            
            payload = {
                "text": question,
                "user_id": "railway_direct",
                "locale": "ru"
            }
            
            response = requests.post(
                f"{self.local_llm_url}/chat",
                json=payload,
                timeout=60  # Увеличиваем таймаут для LLM
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ LLM ответ получен за {processing_time:.2f}с")
                return {
                    "answer": data.get("response"),
                    "category": data.get("intent", "llm_generated"),
                    "confidence": data.get("confidence", 0.9),
                    "source": "local_llm_model",
                    "processing_time": processing_time
                }
            else:
                logger.warning(f"⚠️ Локальная LLM модель вернула ошибку: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка при запросе к локальной LLM модели: {e}")
            return None
    
    def get_hybrid_response(self, question: str) -> Dict[str, Any]:
        """Гибридный ответ: LLM + fallback"""
        # Сначала пытаемся получить LLM ответ
        llm_result = self.get_llm_response(question)
        
        if llm_result:
            return llm_result
        
        # Fallback к простому поиску
        logger.info("🔄 Fallback к простому поиску...")
        return self._simple_search(question)
    
    def _simple_search(self, question: str) -> Dict[str, Any]:
        """Простой поиск по ключевым словам (fallback)"""
        question_lower = question.lower()
        
        # Простая база знаний
        simple_kb = {
            "наценка": "Наценка - дополнительная плата за высокий спрос. Помогает привлечь больше водителей.",
            "доставка": "Для доставки: приложение → Доставка → укажите адреса → подтвердите заказ.",
            "баланс": "Пополнить баланс: Профиль → Пополнить → выберите способ оплаты.",
            "приложение": "Приложение не работает? Перезапустите, проверьте интернет, обновите версию."
        }
        
        # Поиск по ключевым словам
        for keyword, answer in simple_kb.items():
            if keyword in question_lower:
                return {
                    "answer": answer,
                    "category": keyword,
                    "confidence": 0.8,
                    "source": "simple_search",
                    "processing_time": 0.1
                }
        
        # Fallback
        return {
            "answer": "Извините, не могу найти ответ. Обратитесь в службу поддержки.",
            "category": "unknown",
            "confidence": 0.0,
            "source": "fallback",
            "processing_time": 0.1
        }

# Глобальный экземпляр
direct_llm_client = DirectLLMClient()

@app.get("/")
async def root():
    return {
        "message": "APARU Direct LLM Railway", 
        "status": "running", 
        "version": "4.0.0",
        "architecture": "direct_llm_railway",
        "local_llm_available": direct_llm_client.llm_available
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        architecture="direct_llm_railway",
        timestamp=datetime.now().isoformat(),
        local_llm_available=direct_llm_client.llm_available
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
        result = direct_llm_client.get_hybrid_response(request.text)
        
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

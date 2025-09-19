#!/usr/bin/env python3
"""
🚀 ЛОКАЛЬНЫЙ СЕРВЕР С LLM МОДЕЛЬЮ
Принимает запросы от Railway и обрабатывает их через LLM
"""

import json
import re
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="APARU Local LLM Server", version="3.1.0")

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
    architecture: str = "local_llm"
    timestamp: str

class LocalLLMClient:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_name = "aparu-senior-ai"
        self.llm_available = False
        
        # Проверяем доступность Ollama
        self._check_ollama()
        
    def _check_ollama(self):
        """Проверяет доступность Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.llm_available = True
                logger.info("✅ Ollama доступен")
            else:
                logger.warning("⚠️ Ollama недоступен")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к Ollama: {e}")
    
    def get_answer(self, question: str) -> Dict[str, Any]:
        """Получает ответ от LLM модели"""
        start_time = datetime.now()
        
        # Используем LLM модель
        if self.llm_available:
            try:
                logger.info("🧠 Запрашиваем ответ от LLM модели...")
                response = self._query_llm(question)
                if response and response.get('response'):
                    processing_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ LLM ответ получен за {processing_time:.2f}с")
                    return response
            except Exception as e:
                logger.error(f"❌ Ошибка при запросе к LLM: {e}")
        
        # Fallback к простому поиску
        logger.info("🔄 Fallback к простому поиску...")
        return self._simple_search(question)
    
    def _query_llm(self, question: str) -> Dict[str, Any]:
        """Запрашивает оптимизированный ответ от LLM модели"""
        try:
            # Оптимизированный системный промпт для быстрых ответов
            system_prompt = """Ты — AI-ассистент службы поддержки такси APARU. 
Отвечай КРАТКО и ТОЧНО на вопросы о:
- Наценках и тарифах
- Доставке и курьерских услугах  
- Балансе и платежах
- Проблемах с приложением

Правила:
1. Отвечай только по существу
2. Максимум 2-3 предложения
3. Используй простые слова
4. Если не знаешь - скажи "Обратитесь в поддержку"

Примеры хороших ответов:
- "Наценка - дополнительная плата за высокий спрос"
- "Для доставки: приложение → Доставка → адреса → заказ"
- "Пополнить баланс: Профиль → Пополнить → способ оплаты"
- "Приложение не работает? Перезапустите и обновите" """
            
            # СУПЕР-ОПТИМИЗИРОВАННЫЕ параметры для максимальной скорости
            payload = {
                "model": self.model_name,
                "prompt": f"{system_prompt}\n\n{question}:",
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Очень низкая температура
                    "num_predict": 100,  # Очень короткие ответы
                    "num_ctx": 256,      # Минимальный контекст
                    "repeat_penalty": 1.0,
                    "top_k": 10,         # Минимальный выбор
                    "top_p": 0.8,        # Минимальная вероятность
                    "stop": ["\n", ".", "!", "?"]  # Ранние стоп-слова
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=20  # Максимально короткий таймаут
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '').strip()
                
                if answer:
                    return {
                        "answer": answer,
                        "category": "llm_generated",
                        "confidence": 0.95,
                        "source": "super_optimized_llm"
                    }
            
            logger.warning(f"⚠️ LLM вернул неожиданный ответ: {response.status_code}")
            return None
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ LLM таймаут (>20с)")
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
local_llm_client = LocalLLMClient()

@app.get("/")
async def root():
    return {
        "message": "APARU Local LLM Server", 
        "status": "running", 
        "version": "3.1.0",
        "architecture": "local_llm",
        "llm_available": local_llm_client.llm_available
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        architecture="local_llm",
        timestamp=datetime.now().isoformat()
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Основной эндпоинт для чата"""
    try:
        result = local_llm_client.get_answer(request.text)
        
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
    
    # Локальный сервер на порту 8001, доступный извне
    port = int(os.environ.get("LOCAL_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
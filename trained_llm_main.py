#!/usr/bin/env python3
"""
🧠 УЛУЧШЕННАЯ LLM СИСТЕМА С ОБУЧЕНИЕМ НА ВАРИАЦИЯХ
LLM использует question_variations и keywords для точного поиска ответов
"""

import json
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

app = FastAPI(title="APARU Trained LLM AI", version="6.0.0")

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
    architecture: str = "trained_llm"
    timestamp: str
    llm_available: bool = False

class TrainedLLMClient:
    def __init__(self):
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.model_name = "aparu-senior-ai"
        self.ollama_available = False
        
        # Загружаем базу знаний с вариациями и ключевыми словами
        self.knowledge_base = self._load_knowledge_base()
        
        # Проверяем доступность Ollama
        self._check_ollama_model()
    
    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Загружает базу знаний с вариациями и ключевыми словами"""
        try:
            with open("BZ.txt", "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"✅ Загружена база знаний: BZ.txt ({len(data)} вопросов)")
                return data
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            return []
    
    def _check_ollama_model(self):
        """Проверяет доступность Ollama и модели"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if any(m["name"].startswith(self.model_name) for m in models):
                    self.ollama_available = True
                    logger.info(f"✅ Ollama и модель '{self.model_name}' доступны")
                else:
                    logger.warning(f"⚠️ Модель '{self.model_name}' не найдена в Ollama")
            else:
                logger.warning(f"⚠️ Ollama недоступен: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к Ollama: {e}")
    
    def find_best_answer(self, question: str) -> Dict[str, Any]:
        """Находит лучший ответ используя обученную LLM"""
        start_time = datetime.now()
        
        # Используем обученную LLM для поиска
        if self.ollama_available:
            try:
                logger.info("🧠 Используем обученную LLM для поиска ответа...")
                result = self._trained_llm_search(question)
                if result:
                    processing_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ LLM поиск завершен за {processing_time:.2f}с")
                    return result
            except Exception as e:
                logger.error(f"❌ Ошибка LLM поиска: {e}")
        
        # Fallback к простому поиску по ключевым словам
        logger.info("🔄 Fallback к поиску по ключевым словам...")
        return self._keyword_search(question)
    
    def _trained_llm_search(self, question: str) -> Dict[str, Any]:
        """Использует обученную LLM для поиска ответа по вариациям и ключевым словам"""
        try:
            # Создаем обучающий промпт с вариациями и ключевыми словами
            training_prompt = self._create_training_prompt(question)
            
            payload = {
                "model": self.model_name,
                "prompt": training_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,   # Низкая температура для точности
                    "num_predict": 10,    # Короткий ответ
                    "num_ctx": 1024,      # Достаточный контекст
                    "repeat_penalty": 1.0,
                    "top_k": 3,           # Несколько вариантов
                    "top_p": 0.8,         # Умеренная вероятность
                    "stop": ["\n\n", "Ответ:", "Категория:", "Объяснение:"]  # Стоп-слова
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=15  # Увеличенный таймаут для обучения
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '').strip()
                
                # Парсим ответ LLM
                result = self._parse_llm_response(answer, question)
                if result:
                    return result
                
                logger.warning(f"⚠️ LLM вернул неожиданный ответ: {answer}")
                return None
            
            logger.warning(f"⚠️ LLM вернул ошибку: {response.status_code}")
            return None
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ LLM поиск таймаут (>15с)")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка LLM поиска: {e}")
            return None
    
    def _create_training_prompt(self, question: str) -> str:
        """Создает обучающий промпт с вариациями и ключевыми словами"""
        prompt = f"""Ты — AI-ассистент службы поддержки такси APARU. Твоя задача — найти подходящий ответ на вопрос пользователя.

ВОПРОС ПОЛЬЗОВАТЕЛЯ: "{question}"

БАЗА ЗНАНИЙ APARU (с вариациями вопросов и ключевыми словами):"""

        for i, item in enumerate(self.knowledge_base, 1):
            variations = item.get("question_variations", [])
            keywords = item.get("keywords", [])
            answer = item.get("answer", "")
            
            prompt += f"\n\n{i}. ВАРИАЦИИ ВОПРОСОВ:"
            for variation in variations[:5]:  # Берем первые 5 вариаций
                prompt += f"\n   - {variation}"
            
            prompt += f"\n   КЛЮЧЕВЫЕ СЛОВА: {', '.join(keywords)}"
            prompt += f"\n   ОТВЕТ: {answer[:200]}..."
        
        prompt += f"""

ИНСТРУКЦИИ:
1. Проанализируй вопрос пользователя: "{question}"
2. Найди в базе знаний пункт, который наиболее точно соответствует вопросу
3. Сравни вопрос с вариациями вопросов и ключевыми словами
4. Если найден подходящий пункт, верни его номер (1, 2, 3, и т.д.)
5. Если ни один пункт не подходит, верни "0"

Твой ответ (только номер):"""

        return prompt
    
    def _parse_llm_response(self, answer: str, question: str) -> Optional[Dict[str, Any]]:
        """Парсит ответ LLM и возвращает соответствующий ответ из базы знаний"""
        try:
            # Ищем число в ответе
            import re
            numbers = re.findall(r'\d+', answer)
            if numbers:
                num = int(numbers[0])
                if 1 <= num <= len(self.knowledge_base):
                    # Получаем ответ из базы знаний
                    kb_item = self.knowledge_base[num - 1]
                    return {
                        "answer": kb_item.get("answer", "Ответ не найден"),
                        "category": f"Категория {num}",
                        "confidence": 0.95,
                        "source": "trained_llm_search"
                    }
                elif num == 0:
                    return {
                        "answer": "Извините, не могу найти точный ответ на ваш вопрос в базе знаний. Пожалуйста, уточните или обратитесь в службу поддержки.",
                        "category": "unknown",
                        "confidence": 0.5,
                        "source": "trained_llm_no_match"
                    }
            return None
        except:
            return None
    
    def _keyword_search(self, question: str) -> Dict[str, Any]:
        """Fallback поиск по ключевым словам"""
        question_lower = question.lower()
        
        best_match = None
        best_score = 0
        
        for item in self.knowledge_base:
            keywords = item.get("keywords", [])
            variations = item.get("question_variations", [])
            
            # Подсчитываем совпадения ключевых слов
            keyword_matches = 0
            for keyword in keywords:
                if keyword.lower() in question_lower:
                    keyword_matches += 1
            
            # Подсчитываем совпадения вариаций
            variation_matches = 0
            for variation in variations:
                if variation.lower() in question_lower:
                    variation_matches += 1
            
            # Общий счет
            total_score = keyword_matches + variation_matches
            
            if total_score > best_score:
                best_score = total_score
                best_match = item
        
        if best_match and best_score > 0:
            return {
                "answer": best_match.get("answer", "Ответ не найден"),
                "category": "keyword_match",
                "confidence": min(0.9, best_score * 0.2),
                "source": "keyword_search"
            }
        
        # Fallback
        return {
            "answer": "Извините, не могу найти ответ на ваш вопрос. Обратитесь в службу поддержки.",
            "category": "unknown",
            "confidence": 0.0,
            "source": "fallback"
        }

# Глобальный экземпляр
trained_llm_client = TrainedLLMClient()

@app.get("/")
async def root():
    return {
        "message": "APARU Trained LLM AI", 
        "status": "running", 
        "version": "6.0.0",
        "architecture": "trained_llm",
        "llm_available": trained_llm_client.ollama_available
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        architecture="trained_llm",
        timestamp=datetime.now().isoformat(),
        llm_available=trained_llm_client.ollama_available
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
        result = trained_llm_client.find_best_answer(request.text)
        
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

#!/usr/bin/env python3
"""
🎯 LLM СИСТЕМА ВЫБОРА ГОТОВЫХ ОТВЕТОВ
LLM только выбирает подходящий ответ из базы, не генерирует новый
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

app = FastAPI(title="APARU Answer Selection LLM", version="8.0.0")

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
    architecture: str = "answer_selection_llm"
    timestamp: str
    llm_available: bool = False

class AnswerSelectionLLMClient:
    def __init__(self):
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.model_name = "aparu-senior-ai"
        self.ollama_available = False
        
        # Загружаем базу знаний
        self.knowledge_base = self._load_knowledge_base()
        
        # Проверяем доступность Ollama
        self._check_ollama_model()
    
    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Загружает базу знаний"""
        try:
            with open("BZ.txt", "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"✅ Загружена база знаний: BZ.txt ({len(data)} ответов)")
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
        """Находит лучший готовый ответ используя LLM для выбора"""
        start_time = datetime.now()
        
        # Используем LLM для выбора готового ответа
        if self.ollama_available:
            try:
                logger.info("🎯 Используем LLM для выбора готового ответа...")
                result = self._llm_answer_selection(question)
                if result:
                    processing_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ LLM выбор завершен за {processing_time:.2f}с")
                    return result
            except Exception as e:
                logger.error(f"❌ Ошибка LLM выбора: {e}")
        
        # Fallback к поиску по ключевым словам
        logger.info("🔄 Fallback к поиску по ключевым словам...")
        return self._keyword_search(question)
    
    def _llm_answer_selection(self, question: str) -> Dict[str, Any]:
        """LLM выбирает подходящий готовый ответ из базы"""
        try:
            # Создаем промпт для выбора ответа
            selection_prompt = self._create_selection_prompt(question)
            
            payload = {
                "model": self.model_name,
                "prompt": selection_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,   # Минимальная температура для точности
                    "num_predict": 3,      # Только номер ответа
                    "num_ctx": 512,       # Достаточный контекст
                    "repeat_penalty": 1.0,
                    "top_k": 1,           # Только лучший вариант
                    "top_p": 0.1,         # Минимальная вероятность
                    "stop": ["\n", ".", "!", "?", "Ответ:", "Категория:", "Объяснение:"]  # Стоп-слова
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=10  # Короткий таймаут
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '').strip()
                
                # Парсим номер выбранного ответа
                selected_num = self._parse_selected_answer(answer)
                if selected_num:
                    # Возвращаем готовый ответ из базы
                    if 1 <= selected_num <= len(self.knowledge_base):
                        kb_item = self.knowledge_base[selected_num - 1]
                        return {
                            "answer": kb_item.get("answer", "Ответ не найден"),
                            "category": f"Ответ {selected_num}",
                            "confidence": 0.95,
                            "source": "llm_answer_selection"
                        }
                
                logger.warning(f"⚠️ LLM вернул неожиданный ответ: '{answer}'")
                return None
            
            logger.warning(f"⚠️ LLM вернул ошибку: {response.status_code}")
            return None
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ LLM выбор таймаут (>10с)")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка LLM выбора: {e}")
            return None
    
    def _create_selection_prompt(self, question: str) -> str:
        """Создает промпт для выбора подходящего ответа"""
        prompt = f"""Вопрос пользователя: "{question}"

Доступные готовые ответы:

"""
        
        for i, item in enumerate(self.knowledge_base, 1):
            variations = item.get("question_variations", [])
            keywords = item.get("keywords", [])
            answer_preview = item.get("answer", "")[:100] + "..."
            
            prompt += f"{i}. ВАРИАЦИИ ВОПРОСОВ:\n"
            for variation in variations[:3]:  # Показываем первые 3 вариации
                prompt += f"   - {variation}\n"
            
            prompt += f"   КЛЮЧЕВЫЕ СЛОВА: {', '.join(keywords[:5])}\n"
            prompt += f"   ОТВЕТ: {answer_preview}\n\n"
        
        prompt += f"""Задача: Выбери номер ответа (1-{len(self.knowledge_base)}), который лучше всего подходит для вопроса: "{question}"

Учитывай:
- Совпадение ключевых слов
- Похожесть на вариации вопросов
- Смысловую близость

Номер ответа:"""

        return prompt
    
    def _parse_selected_answer(self, answer: str) -> Optional[int]:
        """Парсит номер выбранного ответа"""
        try:
            # Ищем число в ответе
            import re
            numbers = re.findall(r'\d+', answer)
            if numbers:
                num = int(numbers[0])
                if 1 <= num <= len(self.knowledge_base):
                    return num
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
answer_selection_client = AnswerSelectionLLMClient()

@app.get("/")
async def root():
    return {
        "message": "APARU Answer Selection LLM", 
        "status": "running", 
        "version": "8.0.0",
        "architecture": "answer_selection_llm",
        "llm_available": answer_selection_client.ollama_available
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        architecture="answer_selection_llm",
        timestamp=datetime.now().isoformat(),
        llm_available=answer_selection_client.ollama_available
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
        result = answer_selection_client.find_best_answer(request.text)
        
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

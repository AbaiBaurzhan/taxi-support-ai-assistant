#!/usr/bin/env python3
"""
🚀 Профессиональный FAQ-ассистент APARU - FastAPI сервер
API endpoints: POST /ask, GET /health
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from professional_faq_assistant import ProfessionalFAQAssistant, ask_question, expand_knowledge, get_statistics

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Professional FAQ Assistant APARU",
    description="Профессиональный FAQ-ассистент с гибридным поиском",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class AskRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    locale: str = "ru"

class AskResponse(BaseModel):
    answer: str
    confidence: float
    category: Optional[str] = None
    suggestions: list = []
    request_id: str
    source: str
    timestamp: str

class ExpandRequest(BaseModel):
    question: str
    answer: str
    category: str = "general"

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    statistics: Dict[str, Any]

class StatisticsResponse(BaseModel):
    statistics: Dict[str, Any]

# Инициализируем ассистент
assistant = ProfessionalFAQAssistant()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка здоровья системы"""
    try:
        stats = get_statistics()
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            statistics=stats
        )
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

@app.post("/ask", response_model=AskResponse)
async def ask_faq(request: AskRequest):
    """Основной endpoint для вопросов"""
    try:
        logger.info(f"Получен вопрос: {request.question}")
        
        # Получаем ответ от ассистента
        result = ask_question(request.question)
        
        # Формируем ответ
        response = AskResponse(
            answer=result['answer'],
            confidence=result['confidence'],
            category=result.get('category'),
            suggestions=result.get('suggestions', []),
            request_id=result['request_id'],
            source=result.get('source', 'unknown'),
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Ответ отправлен: confidence={result['confidence']:.2f}")
        return response
        
    except Exception as e:
        logger.error(f"Ошибка обработки вопроса: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/expand")
async def expand_knowledge_base(request: ExpandRequest):
    """Дополнение базы знаний"""
    try:
        logger.info(f"Дополнение базы: {request.question[:50]}...")
        
        expand_knowledge(request.question, request.answer, request.category)
        
        return {
            "status": "success",
            "message": "База знаний дополнена",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка дополнения базы: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/statistics", response_model=StatisticsResponse)
async def get_system_statistics():
    """Получение статистики системы"""
    try:
        stats = get_statistics()
        return StatisticsResponse(statistics=stats)
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "Professional FAQ Assistant APARU",
        "version": "1.0.0",
        "endpoints": {
            "ask": "POST /ask - Задать вопрос",
            "health": "GET /health - Проверка здоровья",
            "expand": "POST /expand - Дополнить базу знаний",
            "statistics": "GET /statistics - Статистика системы"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Запуск профессионального FAQ-ассистента APARU")
    logger.info("📊 Статистика системы:")
    
    stats = get_statistics()
    logger.info(f"   Записей в базе: {stats['total_records']}")
    logger.info(f"   Эмбеддинги: {'✅' if stats['embeddings_available'] else '❌'}")
    logger.info(f"   Fuzzy search: {'✅' if stats['fuzzy_available'] else '❌'}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Используем другой порт, чтобы не конфликтовать с main.py
        log_level="info"
    )

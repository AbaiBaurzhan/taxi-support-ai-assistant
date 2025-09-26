#!/usr/bin/env python3
"""
🚀 RAILWAY-ОПТИМИЗИРОВАННАЯ СИСТЕМА ВЫБОРА ОТВЕТОВ
Без LLM, только морфологический поиск + fallback
"""

import json
import logging
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

app = FastAPI(title="APARU Railway Optimized", version="11.0.0")

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
    architecture: str = "railway_optimized"
    timestamp: str

class RailwayOptimizedClient:
    def __init__(self):
        # Загружаем базу знаний
        self.knowledge_base = self._load_knowledge_base()
        
        # Морфологические формы для поиска
        self.morphological_forms = {
            "наценка": ["наценка", "наценки", "наценку", "наценкой", "доплата", "доплаты", "надбавка", "надбавки", "коэффициент", "коэффициента"],
            "комфорт": ["комфорт", "комфорта", "тариф", "тарифа", "класс", "класса"],
            "расценка": ["расценка", "расценки", "стоимость", "стоимости", "цена", "цены", "цену"],
            "доставка": ["доставка", "доставки", "курьер", "курьера", "посылка", "посылки"],
            "предварительный": ["предварительный", "предварительного", "заказ", "заказа", "заранее"],
            "водитель": ["водитель", "водителя", "работа", "работы", "заказы", "заказ"],
            "баланс": ["баланс", "баланса", "пополнить", "пополнения", "оплата", "оплаты", "счет", "счета", "деньги"],
            "приложение": ["приложение", "приложения", "ошибка", "ошибки", "не работает", "глючит", "тормозит", "обновить"],
            "промокод": ["промокод", "промокода", "скидка", "скидки", "бонус", "бонуса"],
            "отмена": ["отмена", "отмены", "отменить", "отмены"]
        }
        
        logger.info(f"✅ Загружена база знаний: {len(self.knowledge_base)} ответов")
    
    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Загружает базу знаний для поиска ответов"""
        try:
            with open("BZ.txt", "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"✅ Загружена база знаний: BZ.txt ({len(data)} ответов)")
                return data
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            return []
    
    def find_best_answer(self, question: str) -> Dict[str, Any]:
        """Находит лучший ответ из базы знаний"""
        start_time = datetime.now()
        
        try:
            # 1. Пробуем морфологический поиск
            logger.info("🔍 Используем морфологический поиск...")
            result = self._enhanced_morphological_search(question)
            
            if result:
                processing_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Морфологический поиск завершен за {processing_time:.2f}с")
                return result
            
            # 2. Fallback к простому поиску по ключевым словам
            logger.info("🔄 Fallback к простому поиску...")
            result = self._enhanced_simple_search(question)
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Fallback завершен за {processing_time:.2f}с")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            return {
                "answer": "Извините, произошла ошибка при обработке вашего запроса.",
                "category": "error",
                "confidence": 0.0,
                "source": "error"
            }
    
    def _enhanced_morphological_search(self, question: str) -> Optional[Dict[str, Any]]:
        """Улучшенный морфологический поиск"""
        question_lower = question.lower()
        
        # Ищем точные совпадения с морфологическими формами
        for base_word, forms in self.morphological_forms.items():
            for form in forms:
                if form in question_lower:
                    # Находим соответствующую категорию в базе знаний
                    category = self._find_category_by_keyword(base_word)
                    if category:
                        return {
                            "answer": category["answer"],
                            "category": f"morphological_match_{base_word}",
                            "confidence": 0.9,
                            "source": "morphological_search"
                        }
        
        return None
    
    def _find_category_by_keyword(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Находит категорию по ключевому слову"""
        keyword_mapping = {
            "наценка": 0, "доплата": 0, "надбавка": 0, "коэффициент": 0,
            "комфорт": 1, "тариф": 1, "класс": 1,
            "расценка": 2, "стоимость": 2, "цена": 2,
            "доставка": 3, "заказ": 3,
            "предварительный": 4, "заранее": 4,
            "водитель": 5, "работа": 5,
            "баланс": 6, "пополнить": 6, "оплата": 6, "счет": 6, "деньги": 6,
            "приложение": 7, "ошибка": 7, "глючит": 7, "тормозит": 7,
            "промокод": 8, "скидка": 8, "бонус": 8,
            "отмена": 9, "отменить": 9
        }
        
        category_index = keyword_mapping.get(keyword)
        if category_index is not None and category_index < len(self.knowledge_base):
            return self.knowledge_base[category_index]
        
        return None
    
    def _enhanced_simple_search(self, question: str) -> Dict[str, Any]:
        """Улучшенный простой поиск по ключевым словам (fallback)"""
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
railway_client = RailwayOptimizedClient()

@app.get("/")
async def root():
    return {
        "message": "APARU Railway Optimized", 
        "status": "running", 
        "version": "11.0.0",
        "architecture": "railway_optimized"
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        architecture="railway_optimized",
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
        result = railway_client.find_best_answer(request.text)
        
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

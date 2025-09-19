#!/usr/bin/env python3
"""
🚀 УЛУЧШЕННАЯ ИИ МОДЕЛЬ APARU
Использует все доступные библиотеки для максимальной точности
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

# ML библиотеки
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from fuzzywuzzy import fuzz, process
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем NLTK данные
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

app = FastAPI(title="APARU Enhanced AI Assistant", version="3.0.0")

# CORS
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
    architecture: str = "enhanced"
    timestamp: str

# Расширенная база знаний
ENHANCED_KB = {
    "наценка": {
        "answer": "Здравствуйте. Наценка является частью тарифной системы Компании и её наличие регулируется объёмом спроса на рассматриваемый момент. В вашем случае наблюдался повышенный спрос на услуги из-за погодных условий. Данная мера необходима для привлечения дополнительных водителей на выполнение заказов, что в свою очередь сокращает время ожидания для вас. Стоимость оплаты поездки рассчитывается согласно показаниям таксометра. Благодарим за обращение! С уважением, команда АПАРУ.",
        "keywords": ["наценка", "наценки", "наценку", "наценкой", "дорого", "подорожание", "повышение", "доплата", "почему так дорого", "откуда доплата", "повысили цену", "зачем доплачивать"],
        "synonyms": ["дорого", "подорожание", "повышение", "доплата", "повысили", "подняли цену"],
        "variations": ["наценкa", "наценкy", "наценкi", "наценкe", "наценкoй"]
    },
    "доставка": {
        "answer": "Для заказа доставки через приложение APARU: 1) Откройте приложение 2) Выберите раздел 'Доставка' 3) Укажите адрес отправления и получения 4) Выберите тип доставки 5) Подтвердите заказ. Курьер свяжется с вами для уточнения деталей.",
        "keywords": ["доставка", "доставки", "доставку", "доставкой", "курьер", "посылка", "отправить", "заказать", "доставить", "передать"],
        "synonyms": ["курьер", "посылка", "отправить", "заказать", "доставить", "передать", "отправка"],
        "variations": ["доставкy", "доставкa", "доставкi", "доставкe", "доставкoй"]
    },
    "баланс": {
        "answer": "Для пополнения баланса в приложении APARU: 1) Откройте приложение 2) Перейдите в раздел 'Профиль' 3) Выберите 'Пополнить баланс' 4) Выберите способ оплаты 5) Введите сумму 6) Подтвердите операцию. Баланс пополнится в течение нескольких минут.",
        "keywords": ["баланс", "баланса", "балансу", "балансом", "счет", "кошелек", "пополнить", "платеж", "деньги", "средства"],
        "synonyms": ["счет", "кошелек", "пополнить", "платеж", "деньги", "средства", "финансы"],
        "variations": ["балaнс", "балaнc", "балaнсу", "балaнсом", "балaнca"]
    },
    "приложение": {
        "answer": "Если приложение APARU не работает: 1) Перезапустите приложение 2) Проверьте подключение к интернету 3) Обновите приложение до последней версии 4) Очистите кэш приложения 5) Переустановите приложение. Если проблема не решается, обратитесь в службу поддержки.",
        "keywords": ["приложение", "приложения", "приложению", "приложением", "программа", "софт", "апп", "работать", "не работает", "глючит", "висит"],
        "synonyms": ["программа", "софт", "апп", "работать", "не работает", "глючит", "висит", "тормозит"],
        "variations": ["приложениe", "приложениa", "приложениy", "приложениi", "приложениoм"]
    }
}

class EnhancedAIModel:
    def __init__(self):
        self.stemmer = SnowballStemmer('russian')
        self.stop_words = set(stopwords.words('russian'))
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=list(self.stop_words),
            ngram_range=(1, 2)
        )
        self._prepare_knowledge_base()
        
    def _prepare_knowledge_base(self):
        """Подготавливает базу знаний для поиска"""
        self.questions = []
        self.answers = []
        self.categories = []
        
        for category, data in ENHANCED_KB.items():
            # Основной вопрос
            self.questions.append(f"Что такое {category}?")
            self.answers.append(data["answer"])
            self.categories.append(category)
            
            # Добавляем вариации вопросов
            for keyword in data["keywords"]:
                if keyword != category:  # Избегаем дублирования
                    self.questions.append(f"Как {keyword}?")
                    self.answers.append(data["answer"])
                    self.categories.append(category)
        
        # Обучаем TF-IDF
        self.tfidf_matrix = self.vectorizer.fit_transform(self.questions)
        logger.info(f"✅ База знаний подготовлена: {len(self.questions)} вопросов")
    
    def normalize_text(self, text: str) -> str:
        """Нормализует текст"""
        # Убираем эмодзи и спецсимволы
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def find_best_match(self, query: str) -> Dict[str, Any]:
        """Находит лучший ответ на вопрос"""
        normalized_query = self.normalize_text(query)
        
        # 1. Прямой поиск по ключевым словам
        direct_match = self._direct_search(normalized_query)
        if direct_match["confidence"] > 0.8:
            return direct_match
        
        # 2. Fuzzy поиск
        fuzzy_match = self._fuzzy_search(normalized_query)
        if fuzzy_match["confidence"] > 0.6:
            return fuzzy_match
        
        # 3. TF-IDF поиск
        tfidf_match = self._tfidf_search(normalized_query)
        if tfidf_match["confidence"] > 0.5:
            return tfidf_match
        
        # 4. Fallback
        return {
            "answer": "Извините, не могу найти ответ на ваш вопрос. Обратитесь в службу поддержки.",
            "category": "unknown",
            "confidence": 0.0,
            "source": "fallback",
            "suggestions": self._get_suggestions(normalized_query)
        }
    
    def _direct_search(self, query: str) -> Dict[str, Any]:
        """Прямой поиск по ключевым словам"""
        for category, data in ENHANCED_KB.items():
            # Проверяем основные ключевые слова
            for keyword in data["keywords"]:
                if keyword in query:
                    return {
                        "answer": data["answer"],
                        "category": category,
                        "confidence": 0.9,
                        "source": "direct"
                    }
            
            # Проверяем синонимы
            for synonym in data["synonyms"]:
                if synonym in query:
                    return {
                        "answer": data["answer"],
                        "category": category,
                        "confidence": 0.8,
                        "source": "synonym"
                    }
            
            # Проверяем вариации (опечатки)
            for variation in data["variations"]:
                if variation in query:
                    return {
                        "answer": data["answer"],
                        "category": category,
                        "confidence": 0.7,
                        "source": "variation"
                    }
        
        return {"confidence": 0.0}
    
    def _fuzzy_search(self, query: str) -> Dict[str, Any]:
        """Fuzzy поиск"""
        best_score = 0
        best_match = None
        
        for category, data in ENHANCED_KB.items():
            # Проверяем все ключевые слова
            all_keywords = data["keywords"] + data["synonyms"] + data["variations"]
            
            for keyword in all_keywords:
                score = fuzz.partial_ratio(query, keyword)
                if score > best_score:
                    best_score = score
                    best_match = {
                        "answer": data["answer"],
                        "category": category,
                        "confidence": score / 100,
                        "source": "fuzzy"
                    }
        
        return best_match if best_match and best_match["confidence"] > 0.6 else {"confidence": 0.0}
    
    def _tfidf_search(self, query: str) -> Dict[str, Any]:
        """TF-IDF поиск"""
        try:
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            
            if best_score > 0.3:
                return {
                    "answer": self.answers[best_idx],
                    "category": self.categories[best_idx],
                    "confidence": float(best_score),
                    "source": "tfidf"
                }
        except Exception as e:
            logger.error(f"Ошибка TF-IDF поиска: {e}")
        
        return {"confidence": 0.0}
    
    def _get_suggestions(self, query: str) -> List[str]:
        """Получает предложения похожих вопросов"""
        suggestions = []
        
        for category, data in ENHANCED_KB.items():
            # Добавляем основные вопросы
            suggestions.append(f"Что такое {category}?")
            
            # Добавляем популярные варианты
            for keyword in data["keywords"][:3]:  # Только первые 3
                if keyword != category:
                    suggestions.append(f"Как {keyword}?")
        
        return suggestions[:5]  # Максимум 5 предложений

# Глобальный экземпляр модели
ai_model = EnhancedAIModel()

@app.get("/")
async def root():
    return {"message": "APARU Enhanced AI Assistant", "status": "running", "version": "3.0.0"}

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        architecture="enhanced",
        timestamp=datetime.now().isoformat()
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Основной эндпоинт для чата"""
    try:
        result = ai_model.find_best_match(request.text)
        
        return ChatResponse(
            response=result["answer"],
            intent=result["category"],
            confidence=result["confidence"],
            source=result["source"],
            timestamp=datetime.now().isoformat(),
            suggestions=result.get("suggestions", [])
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

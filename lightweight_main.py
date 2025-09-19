#!/usr/bin/env python3
"""
🚀 ЛЕГКАЯ ВЕРСИЯ ДЛЯ RAILWAY
Без тяжелых ML библиотек - только FastAPI
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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="APARU Lightweight AI Assistant", version="3.0.0")

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
    architecture: str = "lightweight"
    timestamp: str

# Простая база знаний (без ML)
SIMPLE_KB = {
    "наценка": {
        "answer": "Здравствуйте. Наценка является частью тарифной системы Компании и её наличие регулируется объёмом спроса на рассматриваемый момент. В вашем случае наблюдался повышенный спрос на услуги из-за погодных условий. Данная мера необходима для привлечения дополнительных водителей на выполнение заказов, что в свою очередь сокращает время ожидания для вас. Стоимость оплаты поездки рассчитывается согласно показаниям таксометра. Благодарим за обращение! С уважением, команда АПАРУ.",
        "keywords": ["наценка", "наценки", "наценку", "наценкой", "дорого", "подорожание", "повышение", "доплата", "почему так дорого", "откуда доплата", "повысили цену", "зачем доплачивать"],
        "synonyms": ["дорого", "подорожание", "повышение", "доплата", "повысили", "подняли цену"]
    },
    "доставка": {
        "answer": "Для заказа доставки через приложение APARU: 1) Откройте приложение 2) Выберите раздел 'Доставка' 3) Укажите адрес отправления и получения 4) Выберите тип доставки 5) Подтвердите заказ. Курьер свяжется с вами для уточнения деталей.",
        "keywords": ["доставка", "доставки", "доставку", "доставкой", "курьер", "посылка", "отправить", "заказать", "доставить", "передать"],
        "synonyms": ["курьер", "посылка", "отправить", "заказать", "доставить", "передать", "отправка"]
    },
    "баланс": {
        "answer": "Для пополнения баланса в приложении APARU: 1) Откройте приложение 2) Перейдите в раздел 'Профиль' 3) Выберите 'Пополнить баланс' 4) Выберите способ оплаты 5) Введите сумму 6) Подтвердите операцию. Баланс пополнится в течение нескольких минут.",
        "keywords": ["баланс", "баланса", "балансу", "балансом", "счет", "кошелек", "пополнить", "платеж", "деньги", "средства"],
        "synonyms": ["счет", "кошелек", "пополнить", "платеж", "деньги", "средства", "финансы"]
    },
    "приложение": {
        "answer": "Если приложение APARU не работает: 1) Перезапустите приложение 2) Проверьте подключение к интернету 3) Обновите приложение до последней версии 4) Очистите кэш приложения 5) Переустановите приложение. Если проблема не решается, обратитесь в службу поддержки.",
        "keywords": ["приложение", "приложения", "приложению", "приложением", "программа", "софт", "апп", "работать", "не работает", "глючит", "висит"],
        "synonyms": ["программа", "софт", "апп", "работать", "не работает", "глючит", "висит", "тормозит"]
    }
}

class LightweightAI:
    def __init__(self):
        logger.info("✅ Легкая система поиска инициализирована")
        
    def normalize_text(self, text: str) -> str:
        """Простая нормализация текста"""
        # Убираем эмодзи и спецсимволы
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def find_best_match(self, query: str) -> Dict[str, Any]:
        """Простой поиск без ML"""
        normalized_query = self.normalize_text(query)
        
        # Прямой поиск по ключевым словам
        for category, data in SIMPLE_KB.items():
            # Проверяем основные ключевые слова
            for keyword in data["keywords"]:
                if keyword in normalized_query:
                    return {
                        "answer": data["answer"],
                        "category": category,
                        "confidence": 0.9,
                        "source": "direct"
                    }
            
            # Проверяем синонимы
            for synonym in data["synonyms"]:
                if synonym in normalized_query:
                    return {
                        "answer": data["answer"],
                        "category": category,
                        "confidence": 0.8,
                        "source": "synonym"
                    }
        
        # Fallback
        return {
            "answer": "Извините, не могу найти ответ на ваш вопрос. Обратитесь в службу поддержки.",
            "category": "unknown",
            "confidence": 0.0,
            "source": "fallback",
            "suggestions": ["Что такое наценка?", "Как заказать доставку?", "Как пополнить баланс?", "Приложение не работает"]
        }

# Глобальный экземпляр
ai_model = LightweightAI()

@app.get("/")
async def root():
    return {"message": "APARU Lightweight AI Assistant", "status": "running", "version": "3.0.0"}

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        architecture="lightweight",
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

#!/usr/bin/env python3
"""
🚀 УЛЬТРА-ПРОСТАЯ ВЕРСИЯ ДЛЯ RAILWAY
Минимум кода - максимум надежности
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json

app = FastAPI(title="APARU Ultra Simple AI", version="2.5.0")

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

# Простые ответы с синонимами
SIMPLE_ANSWERS = {
    "наценка": "Наценка - это дополнительная плата за повышенный спрос. Она помогает привлечь больше водителей и сократить время ожидания.",
    "доставка": "Для заказа доставки: откройте приложение → выберите 'Доставка' → укажите адреса → подтвердите заказ.",
    "баланс": "Для пополнения баланса: откройте приложение → 'Профиль' → 'Пополнить баланс' → выберите способ оплаты.",
    "приложение": "Если приложение не работает: перезапустите, проверьте интернет, обновите до последней версии."
}

# Синонимы для улучшенного поиска
SYNONYMS = {
    "наценка": ["дорого", "подорожание", "повышение", "доплата", "наценкa", "наценкy"],
    "доставка": ["курьер", "посылка", "отправить", "заказать", "доставкy", "доставкa"],
    "баланс": ["счет", "кошелек", "пополнить", "платеж", "балaнс", "балaнc"],
    "приложение": ["программа", "софт", "апп", "работать", "приложениe", "приложениa"]
}

@app.get("/")
async def root():
    return {"message": "APARU Ultra Simple AI", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    text = request.text.lower()
    
    # Улучшенный поиск с синонимами
    for keyword, answer in SIMPLE_ANSWERS.items():
        # Прямой поиск по ключевому слову
        if keyword in text:
            return ChatResponse(
                response=answer,
                intent="faq",
                confidence=0.9,
                source="simple",
                timestamp=datetime.now().isoformat()
            )
        
        # Поиск по синонимам
        if keyword in SYNONYMS:
            for synonym in SYNONYMS[keyword]:
                if synonym in text:
                    return ChatResponse(
                        response=answer,
                        intent="faq",
                        confidence=0.8,
                        source="synonym",
                        timestamp=datetime.now().isoformat()
                    )
    
    # Fallback
    return ChatResponse(
        response="Извините, не могу найти ответ. Обратитесь в службу поддержки.",
        intent="unknown",
        confidence=0.0,
        source="fallback",
        timestamp=datetime.now().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Railway использует переменную PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

#!/usr/bin/env python3
"""
🎯 УЛУЧШЕННАЯ СИСТЕМА ВЫБОРА ОТВЕТОВ С МОРФОЛОГИЕЙ
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

app = FastAPI(title="APARU Enhanced Answer Selection", version="10.0.0")

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
    architecture: str = "enhanced_answer_selection"
    timestamp: str
    llm_available: bool = False

class SimpleAnswerSelectionClient:
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.morphological_forms = self._create_morphological_forms()
        
    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Загружает базу знаний"""
        try:
            with open('BZ.txt', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            return []
    
    def _create_morphological_forms(self) -> Dict[str, List[str]]:
        """Создает словарь морфологических форм"""
        return {
            # Наценка
            "наценка": ["наценка", "наценки", "наценку", "наценкой", "наценке", "наценках"],
            "доплата": ["доплата", "доплаты", "доплату", "доплатой", "доплате", "доплатах"],
            "надбавка": ["надбавка", "надбавки", "надбавку", "надбавкой", "надбавке", "надбавках"],
            "коэффициент": ["коэффициент", "коэффициенты", "коэффициента", "коэффициентом", "коэффициенте", "коэффициентах"],
            
            # Комфорт
            "комфорт": ["комфорт", "комфорты", "комфорта", "комфортом", "комфорте", "комфортах"],
            "тариф": ["тариф", "тарифы", "тарифа", "тарифом", "тарифе", "тарифах"],
            "класс": ["класс", "классы", "класса", "классом", "классе", "классах"],
            
            # Расценка
            "расценка": ["расценка", "расценки", "расценку", "расценкой", "расценке", "расценках"],
            "стоимость": ["стоимость", "стоимости", "стоимостью", "стоимости", "стоимости", "стоимостях"],
            "цена": ["цена", "цены", "цену", "ценой", "цене", "ценах"],
            
            # Доставка
            "доставка": ["доставка", "доставки", "доставку", "доставкой", "доставке", "доставках"],
            "заказ": ["заказ", "заказы", "заказа", "заказом", "заказе", "заказах"],
            
            # Предварительный заказ
            "предварительный": ["предварительный", "предварительные", "предварительного", "предварительным", "предварительном", "предварительных"],
            "заранее": ["заранее"],
            
            # Водитель
            "водитель": ["водитель", "водители", "водителя", "водителем", "водителе", "водителях"],
            "заказы": ["заказы", "заказов", "заказам", "заказами", "заказах", "заказах"],
            
            # Баланс
            "баланс": ["баланс", "балансы", "баланса", "балансом", "балансе", "балансах"],
            "пополнить": ["пополнить", "пополняю", "пополняешь", "пополняет", "пополняем", "пополняете", "пополняют"],
            "оплатить": ["оплатить", "оплачиваю", "оплачиваешь", "оплачивает", "оплачиваем", "оплачиваете", "оплачивают"],
            
            # Приложение
            "приложение": ["приложение", "приложения", "приложения", "приложением", "приложении", "приложениях"],
            "обновить": ["обновить", "обновляю", "обновляешь", "обновляет", "обновляем", "обновляете", "обновляют"],
            
            # Промокод
            "промокод": ["промокод", "промокоды", "промокода", "промокодом", "промокоде", "промокодах"],
            "скидка": ["скидка", "скидки", "скидку", "скидкой", "скидке", "скидках"],
            "бонус": ["бонус", "бонусы", "бонуса", "бонусом", "бонусе", "бонусах"],
            
            # Отмена
            "отменить": ["отменить", "отменяю", "отменяешь", "отменяет", "отменяем", "отменяете", "отменяют"],
            "отмена": ["отмена", "отмены", "отмену", "отменой", "отмене", "отменах"]
        }
    
    def _llm_search_answer(self, question: str) -> Dict[str, Any]:
        """LLM поиск ответа"""
        try:
            prompt = f"""Вопрос: "{question}"

Выбери номер ответа:
1 - наценка
2 - комфорт  
3 - расценка
4 - доставка
5 - предварительный заказ
6 - водитель
7 - баланс
8 - приложение
9 - промокод
10 - отмена

Номер:"""
            
            response = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "llama2:7b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,
                        "num_predict": 2,
                        "num_ctx": 128,
                        "top_k": 1,
                        "top_p": 0.1,
                        "stop": ["\n", ".", " "]
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                llm_response = response.json()["response"].strip()
                category_number = int(llm_response) if llm_response.isdigit() else 0
                
                if 1 <= category_number <= 10:
                    answer = self.knowledge_base[category_number - 1]["answer"]
                    return {
                        "answer": answer,
                        "category": f"Ответ {category_number}",
                        "confidence": 0.95,
                        "source": "enhanced_llm"
                    }
            
            raise Exception("LLM не вернул валидный ответ")
            
        except Exception as e:
            logger.error(f"❌ LLM ошибка: {e}")
            raise e
    
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
            "водитель": 5, "заказы": 5,
            "баланс": 6, "пополнить": 6, "оплатить": 6,
            "приложение": 7, "обновить": 7,
            "промокод": 8, "скидка": 8, "бонус": 8,
            "отменить": 9, "отмена": 9
        }
        
        if keyword in keyword_mapping:
            category_index = keyword_mapping[keyword]
            if category_index < len(self.knowledge_base):
                return self.knowledge_base[category_index]
        
        return None
    
    def _partial_match_search(self, question: str) -> Optional[Dict[str, Any]]:
        """Поиск по частичным совпадениям"""
        question_lower = question.lower()
        question_words = question_lower.split()
        
        # Ищем частичные совпадения
        for i, item in enumerate(self.knowledge_base):
            for keyword in item["keywords"]:
                keyword_lower = keyword.lower()
                
                # Точное совпадение
                if keyword_lower in question_lower:
                    return {
                        "answer": item["answer"],
                        "category": f"partial_match_{i+1}",
                        "confidence": 0.8,
                        "source": "partial_search"
                    }
                
                # Частичное совпадение (минимум 3 символа)
                if len(keyword_lower) >= 3:
                    for word in question_words:
                        if len(word) >= 3 and keyword_lower in word:
                            return {
                                "answer": item["answer"],
                                "category": f"partial_match_{i+1}",
                                "confidence": 0.6,
                                "source": "partial_search"
                            }
        
        return None
    
    def find_best_answer(self, question: str) -> Dict[str, Any]:
        """Находит лучший ответ с улучшенной системой"""
        start_time = datetime.now()
        
        try:
            # 1. Пробуем LLM
            logger.info("🎯 Используем улучшенную LLM...")
            result = self._llm_search_answer(question)
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ LLM выбор завершен за {processing_time:.2f}с")
            return result
            
        except Exception as e:
            logger.error(f"❌ LLM выбор таймаут (>5с)")
            
            # 2. Морфологический поиск
            logger.info("🔄 Пробуем морфологический поиск...")
            result = self._enhanced_morphological_search(question)
            if result:
                processing_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Морфологический поиск завершен за {processing_time:.2f}с")
                return result
            
            # 3. Частичный поиск
            logger.info("🔄 Пробуем частичный поиск...")
            result = self._partial_match_search(question)
            if result:
                processing_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Частичный поиск завершен за {processing_time:.2f}с")
                return result
            
            # 4. Fallback
            logger.info("🔄 Fallback ответ...")
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"❌ Fallback ответ за {processing_time:.2f}с")
            
            return {
                "answer": "Извините, не могу найти ответ на ваш вопрос. Обратитесь в службу поддержки.",
                "category": "unknown",
                "confidence": 0.0,
                "source": "fallback"
            }

# Глобальный экземпляр
simple_answer_client = SimpleAnswerSelectionClient()

@app.on_event("startup")
async def startup_event():
    """Прогрев LLM при старте приложения"""
    try:
        logger.info("🔥 Прогрев LLM...")
        requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "llama2:7b",
                "prompt": "1",
                "stream": False,
                "options": {"num_predict": 1, "temperature": 0.0}
            },
            timeout=20
        )
        logger.info("✅ LLM прогрет успешно")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось прогреть LLM: {e}")

@app.get("/")
async def root():
    return {
        "message": "APARU Enhanced Answer Selection", 
        "status": "running", 
        "version": "10.0.0",
        "features": ["LLM Selection", "Morphological Search", "Partial Match", "Fallback"]
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка здоровья системы"""
    try:
        # Проверяем LLM
        llm_available = False
        try:
            response = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
            llm_available = response.status_code == 200
        except:
            pass
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            llm_available=llm_available
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Основной эндпоинт для чата"""
    try:
        logger.info(f"📨 Получен вопрос: {request.text}")
        
        # Обрабатываем вопрос
        result = simple_answer_client.find_best_answer(request.text)
        
        # Формируем ответ
        response = ChatResponse(
            response=result["answer"],
            intent=result["category"],
            confidence=result["confidence"],
            source=result["source"],
            timestamp=datetime.now().isoformat(),
            suggestions=[]
        )
        
        logger.info(f"✅ Ответ отправлен: {result['source']}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки вопроса: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/webapp", response_class=HTMLResponse)
async def webapp():
    """Telegram WebApp интерфейс"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>APARU Support</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }
            .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; }
            .header { text-align: center; margin-bottom: 20px; }
            .chat-container { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; }
            .message { margin-bottom: 10px; padding: 10px; border-radius: 10px; }
            .user-message { background: #007bff; color: white; margin-left: 20%; }
            .bot-message { background: #f8f9fa; color: black; margin-right: 20%; }
            .input-container { display: flex; gap: 10px; }
            .input-field { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            .send-button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .quick-buttons { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
            .quick-button { padding: 8px 16px; background: #e9ecef; border: 1px solid #ddd; border-radius: 20px; cursor: pointer; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚕 APARU Support</h1>
                <p>Улучшенная система поддержки с морфологией</p>
            </div>
            
            <div class="quick-buttons">
                <button class="quick-button" onclick="sendQuickMessage('Что такое наценка?')">Наценка</button>
                <button class="quick-button" onclick="sendQuickMessage('Как пополнить баланс?')">Баланс</button>
                <button class="quick-button" onclick="sendQuickMessage('Что такое комфорт?')">Комфорт</button>
                <button class="quick-button" onclick="sendQuickMessage('Как отменить заказ?')">Отмена</button>
                <button class="quick-button" onclick="sendQuickMessage('Приложение не работает')">Приложение</button>
            </div>
            
            <div class="chat-container" id="chatContainer">
                <div class="message bot-message">
                    <strong>APARU Support:</strong> Здравствуйте! Я помогу вам с вопросами по такси APARU. Задайте ваш вопрос или выберите быструю кнопку.
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" class="input-field" id="messageInput" placeholder="Задайте ваш вопрос..." onkeypress="handleKeyPress(event)">
                <button class="send-button" onclick="sendMessage()">Отправить</button>
            </div>
        </div>

        <script>
            const chatContainer = document.getElementById('chatContainer');
            const messageInput = document.getElementById('messageInput');
            
            function addMessage(text, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                messageDiv.innerHTML = `<strong>${isUser ? 'Вы:' : 'APARU Support:'}</strong> ${text}`;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;
                
                addMessage(message, true);
                messageInput.value = '';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            text: message,
                            user_id: 'webapp_user',
                            locale: 'ru'
                        })
                    });
                    
                    const data = await response.json();
                    addMessage(data.response);
                    
                } catch (error) {
                    addMessage('Извините, произошла ошибка. Попробуйте еще раз.');
                }
            }
            
            function sendQuickMessage(message) {
                messageInput.value = message;
                sendMessage();
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            // Инициализация Telegram WebApp
            if (window.Telegram && window.Telegram.WebApp) {
                window.Telegram.WebApp.ready();
                window.Telegram.WebApp.expand();
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
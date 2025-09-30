import json
import re
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# Импорт улучшенного морфологического анализатора
try:
    from enhanced_morphological_analyzer import enhance_classification_with_morphology, enhanced_analyzer
    MORPHOLOGY_AVAILABLE = True
    print("✅ Улучшенный морфологический анализатор загружен")
except ImportError:
    MORPHOLOGY_AVAILABLE = False
    print("⚠️ Морфологический анализатор недоступен")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Taxi Support AI Assistant", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory="."), name="static")

# Модели данных
class ChatRequest(BaseModel):
    text: str
    user_id: str
    locale: str = "ru"

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    source: str  # "kb" или "llm"
    timestamp: str

# Загрузка данных
def load_json_file(filename: str) -> Dict[str, Any]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Файл {filename} не найден")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON в {filename}: {e}")
        return {}

# Глобальные данные
fixtures = load_json_file("fixtures.json")
kb_data = load_json_file("kb.json")

# Предобработка текста
def preprocess_text(text: str) -> str:
    """Убирает эмодзи и спецсимволы"""
    # Убираем эмодзи
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    text = emoji_pattern.sub('', text)
    
    # Убираем лишние пробелы и спецсимволы
    text = re.sub(r'[^\w\s\-.,!?]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# Определение языка
def detect_language(text: str) -> str:
    """Определяет язык текста"""
    try:
        lang = detect(text)
        if lang in ['ru', 'kk']:
            return 'ru'  # Русский/казахский
        elif lang == 'en':
            return 'en'
        else:
            return 'ru'  # По умолчанию русский
    except LangDetectException:
        return 'ru'

# Классификация интентов
def classify_intent(text: str) -> tuple[str, float]:
    """Классифицирует запрос пользователя"""
    text_lower = text.lower()
    
    # FAQ интенты
    faq_keywords = ['цена', 'стоимость', 'тариф', 'расчет', 'сколько стоит', 
                   'промокод', 'скидка', 'промо', 'код', 'ввести',
                   'отменить', 'отмена', 'отказ',
                   'связаться', 'позвонить', 'водитель', 'контакт',
                   'не приехал', 'опоздал', 'ждать', 'проблема']
    
    # Статус поездки
    ride_status_keywords = ['где водитель', 'статус', 'поездка', 'заказ', 'ожидание']
    
    # Чек
    receipt_keywords = ['чек', 'квитанция', 'документ', 'справка']
    
    # Карты
    cards_keywords = ['карта', 'карты', 'основная', 'платеж', 'оплата']
    
    # Жалобы
    complaint_keywords = ['списали дважды', 'двойное списание', 'жалоба', 'проблема', 'неправильно']
    
    # Подсчет совпадений
    faq_score = sum(1 for keyword in faq_keywords if keyword in text_lower)
    ride_score = sum(1 for keyword in ride_status_keywords if keyword in text_lower)
    receipt_score = sum(1 for keyword in receipt_keywords if keyword in text_lower)
    cards_score = sum(1 for keyword in cards_keywords if keyword in text_lower)
    complaint_score = sum(1 for keyword in complaint_keywords if keyword in text_lower)
    
    scores = {
        'faq': faq_score,
        'ride_status': ride_score,
        'receipt': receipt_score,
        'cards': cards_score,
        'complaint': complaint_score
    }
    
    max_intent = max(scores, key=scores.get)
    max_score = scores[max_intent]
    
    # Если нет четкого интента, считаем FAQ
    if max_score == 0:
        return 'faq', 0.5
    
    confidence = min(max_score / 3.0, 1.0)  # Нормализуем до 1.0
    return max_intent, confidence

# Моки для такси
def get_ride_status(user_id: str) -> Dict[str, Any]:
    """Получает статус поездки пользователя"""
    user_rides = fixtures.get("rides", {}).get(user_id, {})
    if not user_rides:
        return {"status": "no_rides", "message": "У вас нет активных поездок"}
    
    return user_rides

def send_receipt(user_id: str) -> Dict[str, Any]:
    """Отправляет чек пользователю"""
    user_receipts = fixtures.get("receipts", {}).get(user_id, [])
    if not user_receipts:
        return {"status": "no_receipts", "message": "У вас нет чеков для отправки"}
    
    latest_receipt = user_receipts[-1]
    return {
        "status": "sent",
        "receipt": latest_receipt,
        "message": f"Чек отправлен на email. Сумма: {latest_receipt['amount']} тенге"
    }

def list_cards(user_id: str) -> Dict[str, Any]:
    """Получает список карт пользователя"""
    user_cards = fixtures.get("cards", {}).get(user_id, [])
    if not user_cards:
        return {"status": "no_cards", "message": "У вас нет привязанных карт"}
    
    return {"status": "success", "cards": user_cards}

def escalate_to_human(user_id: str, description: str) -> Dict[str, Any]:
    """Эскалирует запрос к оператору"""
    tickets = fixtures.get("tickets", {})
    next_id = tickets.get("next_id", 1001)
    
    new_ticket = {
        "ticket_id": f"TKT_{next_id}",
        "user_id": user_id,
        "subject": "Эскалация от ИИ-ассистента",
        "description": description,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "priority": "medium"
    }
    
    tickets["tickets"].append(new_ticket)
    tickets["next_id"] = next_id + 1
    
    return {
        "status": "escalated",
        "ticket_id": new_ticket["ticket_id"],
        "message": f"Ваш запрос передан оператору. Номер тикета: {new_ticket['ticket_id']}"
    }

# Улучшенный поиск в FAQ с морфологическим анализом
def search_faq(text: str) -> Optional[Dict[str, Any]]:
    """Улучшенный поиск в базе знаний FAQ с морфологическим анализом"""
    if not text or not kb_data:
        return None
    
    # Используем улучшенный морфологический анализ
    if MORPHOLOGY_AVAILABLE:
        try:
            result = enhance_classification_with_morphology(text, kb_data)
            confidence = result.get('confidence', 0)
            logger.info(f"🔍 Морфологический анализ: confidence={confidence:.2f}, intent={result.get('intent', 'unknown')}")
            
            # Понизили порог до минимума для стабильности
            if result.get('matched_item') and confidence > 0.05:  # Минимальный порог
                logger.info(f"✅ Морфологический поиск найден: {confidence:.2f}")
                return result['matched_item']
            elif result.get('matched_item'):
                logger.info(f"⚠️ Морфологический поиск найден, но низкая уверенность: {confidence:.2f}")
        except Exception as e:
            logger.error(f"❌ Ошибка морфологического анализа: {e}")
            import traceback
            traceback.print_exc()
    else:
        logger.warning("⚠️ Морфологический анализатор недоступен, используется простой поиск")
    
    # Fallback к простому поиску
    faq_items = kb_data.get("faq", [])
    text_lower = text.lower()
    
    # Предобработка сленговых выражений
    slang_replacements = {
        'че': 'что',
        'там': '',
        'по': '',
        'как работает': 'как',
        'работает': 'работа'
    }
    
    processed_text = text_lower
    for slang, replacement in slang_replacements.items():
        processed_text = processed_text.replace(slang, replacement)
    
    # Убираем лишние пробелы
    processed_text = ' '.join(processed_text.split())
    
    best_match = None
    best_score = 0
    
    for item in faq_items:
        score = 0
        
        # Поиск по ключевым словам (используем и оригинальный, и обработанный текст)
        keywords = item.get("keywords", [])
        keyword_score = sum(1 for keyword in keywords if keyword in text_lower or keyword in processed_text)
        
        # Поиск по вариациям вопросов
        variations = item.get("question_variations", [])
        variation_score = 0
        for variation in variations:
            variation_words = set(variation.lower().split())
            text_words = set(text_lower.split())
            processed_words = set(processed_text.split())
            common_words = len(variation_words.intersection(text_words)) + len(variation_words.intersection(processed_words))
            variation_score += common_words
        
        # Поиск по основному вопросу
        main_question = item.get("question", "").lower()
        main_score = sum(1 for word in main_question.split() if word in text_lower or word in processed_text)
        
        # Общий балл с весами
        score = (
            keyword_score * 2.0 +           # Ключевые слова важнее
            variation_score * 0.5 +         # Вариации вопросов
            main_score * 1.0                # Основной вопрос
        )
        
        if score > best_score:
            best_score = score
            best_match = item
    
    # Возвращаем результат только если балл достаточно высокий
    if best_score >= 1.0:
        logger.info(f"✅ Простой поиск найден: {best_score:.2f}")
        return best_match
    
    return None

# Основной эндпоинт
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Основной эндпоинт для чата с ИИ-ассистентом"""
    
    # Предобработка текста
    processed_text = preprocess_text(request.text)
    if not processed_text:
        raise HTTPException(status_code=400, detail="Пустое сообщение после обработки")
    
    # Определение языка
    detected_lang = detect_language(processed_text)
    final_locale = request.locale if request.locale in ['ru', 'kz', 'en'] else detected_lang
    
    # Классификация интента
    intent, confidence = classify_intent(processed_text)
    
    logger.info(f"User: {request.user_id}, Intent: {intent}, Confidence: {confidence}, Locale: {final_locale}")
    
    response_text = ""
    source = "llm"
    
    # Обработка по интенту
    if intent == "faq":
        faq_result = search_faq(processed_text)
        if faq_result:
            response_text = faq_result["answer"]
            source = "kb"
            confidence = 0.9
        else:
            # Если не найден в FAQ, используем LLM
            prompt = llm_client.create_taxi_context_prompt(processed_text, intent, final_locale)
            response_text = llm_client.generate_response(prompt)
    
    elif intent == "ride_status":
        ride_data = get_ride_status(request.user_id)
        if ride_data.get("status") == "no_rides":
            response_text = "У вас нет активных поездок"
        else:
            driver = ride_data.get("driver", {})
            response_text = f"Ваша поездка в процессе. Водитель: {driver.get('name', 'Неизвестно')}, машина: {driver.get('car', 'Неизвестно')}, номер: {driver.get('plate', 'Неизвестно')}. Ожидаемое время прибытия: {ride_data.get('estimated_arrival', 'Неизвестно')}"
        source = "kb"
        confidence = 0.95
    
    elif intent == "receipt":
        receipt_data = send_receipt(request.user_id)
        response_text = receipt_data["message"]
        source = "kb"
        confidence = 0.95
    
    elif intent == "cards":
        cards_data = list_cards(request.user_id)
        if cards_data["status"] == "success":
            cards = cards_data["cards"]
            primary_card = next((card for card in cards if card.get("is_primary")), None)
            response_text = f"Ваши карты: {', '.join([f'{card['type']} ****{card['last_four']}' for card in cards])}. Основная карта: {primary_card['type']} ****{primary_card['last_four'] if primary_card else 'Не выбрана'}"
        else:
            response_text = cards_data["message"]
        source = "kb"
        confidence = 0.95
    
    elif intent == "complaint":
        escalation_data = escalate_to_human(request.user_id, processed_text)
        response_text = escalation_data["message"]
        source = "kb"
        confidence = 0.95
    
    else:
        # Для неизвестных интентов используем LLM
        prompt = llm_client.create_taxi_context_prompt(processed_text, intent, final_locale)
        response_text = llm_client.generate_response(prompt)
    
    # Логирование
    logger.info(f"Response: {response_text[:100]}..., Source: {source}, Intent: {intent}, Confidence: {confidence}")
    
    return ChatResponse(
        response=response_text,
        intent=intent,
        confidence=confidence,
        source=source,
        timestamp=datetime.now().isoformat()
    )

# Дополнительные эндпоинты для моков
@app.get("/ride-status/{user_id}")
async def get_ride_status_endpoint(user_id: str):
    """Получить статус поездки"""
    return get_ride_status(user_id)

@app.post("/send-receipt/{user_id}")
async def send_receipt_endpoint(user_id: str):
    """Отправить чек"""
    return send_receipt(user_id)

@app.get("/cards/{user_id}")
async def list_cards_endpoint(user_id: str):
    """Получить список карт"""
    return list_cards(user_id)

@app.post("/escalate/{user_id}")
async def escalate_endpoint(user_id: str, description: str):
    """Эскалировать к оператору"""
    return escalate_to_human(user_id, description)

@app.get("/webapp")
async def webapp():
    """Отдача WebApp интерфейса"""
    return FileResponse("webapp.html")

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

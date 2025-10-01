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
    # Проверяем несколько возможных путей
    possible_paths = [
        filename,
        f"../{filename}",
        f"./{filename}"
    ]
    
    for path in possible_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Загружен файл: {path}")
                return data
        except FileNotFoundError:
            continue
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON в {path}: {e}")
            continue
    
    logger.error(f"Файл {filename} не найден ни в одном из путей: {possible_paths}")
    return {}

# Глобальные данные
fixtures = load_json_file("fixtures.json")
kb_data = load_json_file("kb.json")

# Убеждаемся что fixtures - это словарь
if isinstance(fixtures, list):
    # Если fixtures загружен как список, создаем правильную структуру
    fixtures = {
        "rides": fixtures,  # Используем список как есть
        "receipts": [], 
        "cards": [], 
        "tickets": {"next_id": 1001}
    }
    print("⚠️ fixtures.json загружен как список, преобразован в правильную структуру")
elif not isinstance(fixtures, dict):
    # Если fixtures не словарь и не список, создаем пустую структуру
    fixtures = {"rides": [], "receipts": [], "cards": [], "tickets": {"next_id": 1001}}
    print("⚠️ fixtures.json имеет неожиданный формат, создана пустая структура")

# Убеждаемся что kb_data - это словарь  
if isinstance(kb_data, list):
    kb_data = {"faq": []}
    print("⚠️ kb.json загружен как список, используется пустая структура")

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
    
    # Специальная логика для предварительного заказа - проверяем в первую очередь
    if any(phrase in text_lower for phrase in ['предварительный заказ', 'предзаказ', 'заранее', 'зарезервировать']):
        return 'faq', 0.9  # Сразу возвращаем FAQ с высокой уверенностью
    
    # Специальная логика для исключения конфликтующих слов
    # Если запрос содержит специфичные FAQ слова, приоритизируем FAQ
    specific_faq_words = ['наценка', 'доплата', 'расценка', 'доставка', 'моточасы', 'баланс', 'приложение']
    if any(word in text_lower for word in specific_faq_words):
        # Добавляем большой бонус для FAQ и обнуляем cards
        faq_bonus = 10
        cards_penalty = -10  # Штраф для cards
    else:
        faq_bonus = 0
        cards_penalty = 0
    
    # FAQ интенты (включаем все ключевые слова из базы знаний)
    faq_keywords = ['цена', 'стоимость', 'тариф', 'расчет', 'сколько стоит', 
                   'промокод', 'скидка', 'промо', 'код', 'ввести',
                   'отменить', 'отмена', 'отказ',
                   'связаться', 'позвонить', 'водитель', 'контакт',
                   'не приехал', 'опоздал', 'ждать', 'проблема',
                   'предварительный заказ', 'предзаказ', 'заранее', 'время',
                   'зарезервировать', 'вызов', 'назначить время',
                   # Добавляем все ключевые слова из FAQ
                   'наценка', 'коэффициент', 'доплата', 'надбавка', 'спрос', 'повышенный спрос', 'подорожание',
                   'комфорт', 'класс', 'машина', 'премиум', 'камри', 'дороже', 'удобство',
                   'расценка', 'таксометр', 'калькулятор', 'предварительно', 'оценка',
                   'доставка', 'заказ', 'курьер', 'посылка', 'откуда', 'куда', 'телефон', 'получатель',
                   'регистрация', 'заказы', 'лента заказов', 'баланс', 'id', 'клиент', 'пробный',
                   'пополнение', 'qiwi', 'cyberplat', 'касса24', 'единица', 'kaspi', 'visa', 'mastercard',
                   'моточасы', 'минуты', 'поездка', 'время', 'тариф', 'длительные заказы',
                   'ожидание', 'поехали', 'остановить', 'заказ выполнен', 'клиент', 'адрес',
                   'приложение', 'не работает', 'обновление', 'google play', 'app store', 'gps', 'вылетает', 'зависает',
                   'работает', 'груз', 'отправить', 'расстояние', 'товары', 'документы']
    
    # Статус поездки (только специфичные слова)
    ride_status_keywords = ['где водитель', 'статус поездки', 'активные поездки']
    
    # Чек (только специфичные слова)
    receipt_keywords = ['чек', 'квитанция', 'документ', 'справка', 'отправить чек']
    
    # Карты (только специфичные слова, исключаем "оплата" и "доплата")
    cards_keywords = ['карта', 'карты', 'основная карта', 'привязать карту', 'основная']
    
    # Жалобы
    complaint_keywords = ['списали дважды', 'двойное списание', 'жалоба', 'неправильно списали']
    
    # Подсчет совпадений
    faq_score = sum(1 for keyword in faq_keywords if keyword in text_lower) + faq_bonus
    ride_score = sum(1 for keyword in ride_status_keywords if keyword in text_lower)
    receipt_score = sum(1 for keyword in receipt_keywords if keyword in text_lower)
    cards_score = sum(1 for keyword in cards_keywords if keyword in text_lower) + cards_penalty
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
    rides = fixtures.get("rides", [])
    user_rides = [ride for ride in rides if ride.get("user_id") == user_id]
    
    if not user_rides:
        return {"status": "no_rides", "message": "У вас нет активных поездок"}
    
    # Возвращаем последнюю поездку
    return user_rides[-1]

def send_receipt(user_id: str) -> Dict[str, Any]:
    """Отправляет чек пользователю"""
    receipts = fixtures.get("receipts", [])
    user_receipts = [receipt for receipt in receipts if receipt.get("user_id") == user_id]
    
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
    cards = fixtures.get("cards", [])
    user_cards = [card for card in cards if card.get("user_id") == user_id]
    
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

# ТРЕХУРОВНЕВАЯ СИСТЕМА ПОИСКА
def search_with_three_filters(query: str, faq_items: List[Dict]) -> List[tuple]:
    """
    Трехуровневая система поиска с приоритетами:
    1. question_variations (приоритет 0.5)
    2. keywords (приоритет 0.3) 
    3. answer content (приоритет 0.2)
    """
    if not query or not faq_items:
        return []
    
    results = []
    query_lower = query.lower().strip()
    
    # Предобработка запроса
    query_words = re.sub(r'[^\w\s]', ' ', query_lower).split()
    query_words = [word for word in query_words if len(word) > 2]
    
    # Специальная логика для исключения конфликтующих FAQ
    # Если запрос содержит специфичные слова, исключаем конфликтующие FAQ
    if 'расценка' in query_lower:
        # Для "расценка" исключаем FAQ о наценке
        faq_items = [item for item in faq_items if 'наценк' not in item.get('question', '').lower()]
    elif 'наценка' in query_lower or 'доплата' in query_lower:
        # Для "наценка" и "доплата" исключаем FAQ о расценке
        faq_items = [item for item in faq_items if 'расценк' not in item.get('question', '').lower()]
    
    for item in faq_items:
        # Filter 1: Question Variations (приоритет 0.5)
        variations_score = search_question_variations(query_lower, item.get("question_variations", []))
        
        # Filter 2: Keywords (приоритет 0.3)
        keywords_score = search_keywords(query_words, item.get("keywords", []))
        
        # Filter 3: Answer Content (приоритет 0.2)
        answer_score = search_answer_content(query_words, item.get("answer", ""))
        
        # Общий балл с приоритетами
        total_score = (
            variations_score * 0.5 +    # 50% - максимальный приоритет
            keywords_score * 0.3 +      # 30% - средний приоритет
            answer_score * 0.2          # 20% - дополнительный поиск
        )
        
        # Минимальный порог для рассмотрения
        if total_score >= 0.3:  # 30% минимум
            results.append((item, total_score, {
                'variations': variations_score,
                'keywords': keywords_score, 
                'answer': answer_score
            }))
    
    # Сортируем по убыванию общего балла
    return sorted(results, key=lambda x: x[1], reverse=True)


def search_question_variations(query: str, variations: List[str]) -> float:
    """Filter 1: Поиск по вариантам вопросов (высокий приоритет)"""
    if not variations:
        return 0.0
    
    best_score = 0.0
    
    for variation in variations:
        variation_lower = variation.lower()
        
        # Точное совпадение
        if query == variation_lower:
            return 1.0
        
        # Очень близкое совпадение (90%+)
        similarity = calculate_text_similarity(query, variation_lower)
        if similarity > 0.9:
            best_score = max(best_score, similarity)
        
        # Хорошее совпадение (80%+)
        elif similarity > 0.8:
            best_score = max(best_score, similarity * 0.9)
        
        # Умеренное совпадение (70%+)
        elif similarity > 0.7:
            best_score = max(best_score, similarity * 0.7)
        
        # Проверяем частичное вхождение
        if query in variation_lower or variation_lower in query:
            partial_score = min(len(query), len(variation_lower)) / max(len(query), len(variation_lower))
            best_score = max(best_score, partial_score * 0.6)
    
    return best_score


def search_keywords(query_words: List[str], keywords: List[str]) -> float:
    """Filter 2: Улучшенный поиск по ключевым словам с приоритизацией"""
    if not query_words or not keywords:
        return 0.0
    
    # Специальные приоритеты для ключевых слов
    priority_keywords = {
        # Высокий приоритет - уникальные слова
        'наценка': 15, 'коэффициент': 15, 'доплата': 15, 'надбавка': 15, 'спрос': 15, 'повышенный спрос': 15, 'подорожание': 15,
        'комфорт': 15, 'камри': 15, 'премиум': 15, 'класс': 15, 'машина': 15, 'дороже': 15, 'удобство': 15,
        'моточасы': 15, 'минуты': 15, 'поездка': 15, 'время': 15, 'длительные заказы': 15,
        'баланс': 15, 'пополнение': 15, 'qiwi': 15, 'cyberplat': 15, 'касса24': 15, 'единица': 15, 'kaspi': 15, 'visa': 15, 'mastercard': 15,
        'приложение': 15, 'google play': 15, 'app store': 15, 'gps': 15, 'вылетает': 15, 'зависает': 15,
        'водитель': 15, 'регистрация': 15, 'лента заказов': 15, 'заказы': 15, 'id': 15, 'клиент': 15, 'пробный': 15,
        
        # Очень высокий приоритет - уникальные слова для расценки
        'расценка': 20, 'таксометр': 20, 'калькулятор': 20, 'предварительно': 20, 'оценка': 20,
        
        # Высокий приоритет - специфичные слова
        'доставка': 15, 'курьер': 15, 'посылка': 15, 'отправить': 15, 'заказ': 15, 'откуда': 15, 'куда': 15, 'телефон': 15, 'получатель': 15,
        'предварительный заказ': 15, 'предзаказ': 15, 'заранее': 15,
        'ожидание': 15, 'поехали': 15, 'остановить': 15, 'заказ выполнен': 15, 'клиент': 15, 'адрес': 15,
        'работает': 15, 'груз': 15, 'расстояние': 15, 'товары': 15, 'документы': 15,
        
        # Низкий приоритет - общие слова (могут конфликтовать)
        'цена': 3, 'стоимость': 3, 'тариф': 3
    }
    
    total_score = 0.0
    max_possible = len(keywords) * 20  # Максимум баллов за ключевые слова
    
    for keyword in keywords:
        keyword_lower = keyword.lower().strip()
        keyword_root = extract_word_root(keyword_lower)
        max_similarity = 0
        
        # Получаем приоритет ключевого слова
        keyword_priority = priority_keywords.get(keyword_lower, 5)  # По умолчанию 5
        
        for word in query_words:
            word_lower = word.lower().strip()
            
            # Точное совпадение ключевого слова
            if word_lower == keyword_lower:
                total_score += keyword_priority
                max_similarity = 1.0
                continue
            
            # Вычисляем схожесть с ключевым словом
            similarity = calculate_word_similarity(word_lower, keyword_lower)
            max_similarity = max(max_similarity, similarity)
            
            # Дополнительная проверка с корнем
            word_root = extract_word_root(word_lower)
            root_similarity = calculate_word_similarity(word_root, keyword_root)
            max_similarity = max(max_similarity, root_similarity)
        
        # Конвертируем схожесть в баллы с учетом приоритета
        if max_similarity >= 1.0:      # Точное совпадение
            total_score += keyword_priority
        elif max_similarity >= 0.9:    # Совпадение корней
            total_score += keyword_priority * 0.9
        elif max_similarity >= 0.8:    # Частичное совпадение корней
            total_score += keyword_priority * 0.8
        elif max_similarity >= 0.7:    # Хорошая схожесть
            total_score += keyword_priority * 0.7
        elif max_similarity >= 0.6:    # Умеренная схожесть
            total_score += keyword_priority * 0.5
        elif max_similarity >= 0.5:    # Слабая схожесть
            total_score += keyword_priority * 0.3
        elif max_similarity >= 0.4:    # Минимальная схожесть
            total_score += keyword_priority * 0.1
    
    return total_score / max_possible if max_possible > 0 else 0.0


def search_answer_content(query_words: List[str], answer: str) -> float:
    """Filter 3: Поиск по содержимому ответов"""
    if not query_words or not answer:
        return 0.0
    
    answer_lower = answer.lower()
    answer_words = re.sub(r'[^\w\s]', ' ', answer_lower).split()
    answer_words = [word for word in answer_words if len(word) > 2]
    
    if not answer_words:
        return 0.0
    
    # TF-IDF подсчет
    common_words = set(query_words).intersection(set(answer_words))
    if not common_words:
        return 0.0
    
    # Простой TF-IDF
    tf_score = len(common_words) / len(answer_words)
    idf_score = 1 + (len(common_words) / len(query_words))
    tfidf_score = tf_score * idf_score
    
    # Бонус за важные слова в начале ответа
    position_bonus = 0
    for i, word in enumerate(answer_words[:10]):  # Первые 10 слов
        if word in query_words:
            position_bonus += (10 - i) / 10 * 0.1
    
    # Бонус за фразовые совпадения
    phrase_bonus = 0
    for i in range(len(query_words) - 1):
        phrase = f"{query_words[i]} {query_words[i+1]}"
        if phrase in answer_lower:
            phrase_bonus += 0.2
    
    return min(1.0, tfidf_score + position_bonus + phrase_bonus)


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Вычисляет схожесть между двумя текстами"""
    if not text1 or not text2:
        return 0.0
    
    # Точное совпадение
    if text1 == text2:
        return 1.0
    
    # Левенштейн расстояние
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    distance = levenshtein_distance(text1, text2)
    max_len = max(len(text1), len(text2))
    similarity = 1 - (distance / max_len)
    
    return max(0.0, similarity)


def calculate_word_similarity(word1, word2):
    """Вычисляет семантическую схожесть между словами"""
    if not word1 or not word2:
        return 0
    
    # Нормализуем слова
    w1, w2 = word1.lower(), word2.lower()
    
    # Точное совпадение
    if w1 == w2:
        return 1.0
    
    # Извлекаем корни
    root1, root2 = extract_word_root(w1), extract_word_root(w2)
    if root1 == root2:
        return 0.9
    
    # Частичное совпадение корней
    if len(root1) >= 4 and len(root2) >= 4:
        common_len = 0
        min_len = min(len(root1), len(root2))
        for i in range(min_len):
            if root1[i] == root2[i]:
                common_len += 1
            else:
                break
        
        if common_len >= 4:
            return 0.7 + (common_len / min_len) * 0.2
    
    # Левенштейн расстояние для опечаток
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    # Проверяем опечатки
    if len(w1) >= 3 and len(w2) >= 3:
        distance = levenshtein_distance(w1, w2)
        max_len = max(len(w1), len(w2))
        similarity = 1 - (distance / max_len)
        
        if similarity > 0.6:  # 60% схожести
            return similarity * 0.5
    
    # Фонетическая схожесть
    phonetic_map = {
        'к': ['г', 'х', 'к'], 'п': ['б', 'п'], 'т': ['д', 'т'],
        'с': ['з', 'ц', 'с'], 'ф': ['в', 'ф'], 'ш': ['щ', 'ж', 'ш'],
        'ч': ['щ', 'ч'], 'р': ['р', 'л'], 'л': ['р', 'л']
    }
    
    if len(w1) >= 3 and len(w2) >= 3:
        phonetic_score = 0
        min_len = min(len(w1), len(w2))
        
        for i in range(min_len):
            if w1[i] == w2[i]:
                phonetic_score += 1
            elif w1[i] in phonetic_map.get(w2[i], []) or w2[i] in phonetic_map.get(w1[i], []):
                phonetic_score += 0.7
        
        phonetic_similarity = phonetic_score / min_len
        if phonetic_similarity > 0.7:
            return phonetic_similarity * 0.4
    
    return 0


def extract_word_root(word):
    """Извлекает корень слова, убирая окончания, суффиксы и приставки"""
    if len(word) < 4:
        return word
    
    root = word.lower()
    
    # Специальные случаи для конкретных слов
    special_cases = {
        'доставка': 'достав', 'доставки': 'достав', 'доставку': 'достав', 'доставке': 'достав',
        'доставщик': 'достав', 'доставщица': 'достав', 'доставлять': 'достав',
        'передоставка': 'достав', 'поддоставка': 'достав',
        'водитель': 'води', 'водители': 'води', 'водительница': 'води', 'водить': 'води',
        'водит': 'води', 'водила': 'води', 'водило': 'води', 'водили': 'води',
        'заказ': 'заказ', 'заказы': 'заказ', 'заказывать': 'заказ', 'заказчик': 'заказ',
        'заказчица': 'заказ', 'перезаказ': 'заказ', 'подзаказ': 'заказ',
        'ценообразование': 'цен', 'переоценка': 'цен', 'оценка': 'цен',
        'карточка': 'карт', 'картографический': 'карт', 'картограф': 'карт',
        'балансировка': 'баланс', 'балансировать': 'баланс',
        'тарификация': 'тариф', 'тарифицировать': 'тариф'
    }
    
    if root in special_cases:
        return special_cases[root]
    
    # Русские окончания (по длине от длинных к коротким)
    russian_endings = [
        'оваться', 'иваться', 'еваться', 'аться', 'иться', 'еться', 'уться',
        'ование', 'ирование', 'евание', 'ание', 'ение', 'ение',
        'ский', 'ская', 'ское', 'ские', 'ского', 'ской', 'скую', 'ским', 'ском', 'ских', 'скими',
        'ость', 'есть', 'ство', 'тель', 'тельница',
        'ый', 'ая', 'ое', 'ые', 'ого', 'ой', 'ую', 'ым', 'ом', 'их', 'ыми',
        'ия', 'ий', 'ие', 'ию', 'ием', 'ии', 'иями', 'иях',
        'ик', 'иц', 'ич', 'ищ', 'ник', 'ниц', 'щик', 'щиц',
        'а', 'о', 'у', 'ы', 'и', 'е', 'ю', 'ем', 'ом', 'ах', 'ями', 'ях',
        'ть', 'ти', 'л', 'ла', 'ло', 'ли', 'н', 'на', 'но', 'ны'
    ]
    
    # Приставки (по длине от длинных к коротким)
    prefixes = [
        'пере', 'пред', 'под', 'над', 'при', 'раз', 'рас', 'из', 'ис',
        'от', 'об', 'в', 'во', 'за', 'на', 'до', 'по', 'со', 'вы', 'у'
    ]
    
    # Убираем окончания (от длинных к коротким)
    for ending in sorted(russian_endings, key=len, reverse=True):
        if root.endswith(ending) and len(root) > len(ending) + 2:
            root = root[:-len(ending)]
            break
    
    # Убираем приставки (от длинных к коротким)
    for prefix in sorted(prefixes, key=len, reverse=True):
        if root.startswith(prefix) and len(root) > len(prefix) + 3:
            root = root[len(prefix):]
            break
    
    # Минимальная длина корня
    return root if len(root) >= 3 else word.lower()


def search_faq(text: str) -> Optional[Dict[str, Any]]:
    """Трехуровневый поиск в базе знаний FAQ с приоритетами"""
    if not text or not kb_data:
        return None
    
    faq_items = kb_data.get("faq", [])
    if not faq_items:
        return None
    
    logger.info(f"🔍 Трехуровневый поиск для: '{text}'")
    
    # Используем новую трехуровневую систему поиска
    results = search_with_three_filters(text, faq_items)
    
    if results:
        best_match, best_score, filter_scores = results[0]
        
        logger.info(f"🎯 Лучший результат: {best_score:.3f}")
        logger.info(f"   📋 Filter 1 (variations): {filter_scores['variations']:.3f}")
        logger.info(f"   🔑 Filter 2 (keywords): {filter_scores['keywords']:.3f}")
        logger.info(f"   📄 Filter 3 (answer): {filter_scores['answer']:.3f}")
        
        # Пороги для принятия решения
        if best_score >= 0.7:  # Отличное совпадение
            logger.info(f"✅ Отличное совпадение: {best_score:.3f}")
            return best_match
        elif best_score >= 0.5:  # Хорошее совпадение
            logger.info(f"✅ Хорошее совпадение: {best_score:.3f}")
            return best_match
        elif best_score >= 0.3:  # Удовлетворительное совпадение
            logger.info(f"⚠️ Удовлетворительное совпадение: {best_score:.3f}")
            return best_match
    
    # Fallback к морфологическому анализу если трехуровневый поиск не дал результатов
    if MORPHOLOGY_AVAILABLE:
        try:
            result = enhance_classification_with_morphology(text, kb_data)
            confidence = result.get('confidence', 0)
            logger.info(f"🔍 Fallback морфологический анализ: confidence={confidence:.2f}")
            
            if result.get('matched_item') and confidence > 0.1:
                logger.info(f"✅ Морфологический fallback найден: {confidence:.2f}")
                return result['matched_item']
        except Exception as e:
            logger.error(f"❌ Ошибка морфологического fallback: {e}")
    
    logger.info(f"❌ Трехуровневый поиск не нашел подходящих результатов")
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
    source = "kb"
    
    # Обработка по интентам
    if intent == "ride_status":
        result = get_ride_status(request.user_id)
        response_text = result.get("message", "Не удалось получить статус поездки")
        
    elif intent == "receipt":
        result = send_receipt(request.user_id)
        response_text = result.get("message", "Не удалось отправить чек")
        
    elif intent == "cards":
        result = list_cards(request.user_id)
        response_text = result.get("message", "Не удалось получить список карт")
        
    elif intent == "complaint":
        result = escalate_to_human(request.user_id, processed_text)
        response_text = result.get("message", "Не удалось создать тикет")
        
    else:  # FAQ
        # Поиск в базе знаний
        faq_result = search_faq(processed_text)
        
        if faq_result:
            response_text = faq_result.get("answer", "Не удалось найти ответ")
            source = "kb"
        else:
            # Fallback ответ для FAQ
            response_text = "Извините, я не смог найти подходящий ответ на ваш вопрос. Пожалуйста, попробуйте переформулировать вопрос или обратитесь к оператору."
            source = "fallback"
    
    logger.info(f"Response: {response_text[:100]}..., Source: {source}, Intent: {intent}, Confidence: {confidence}")
    
    return ChatResponse(
        response=response_text,
        intent=intent,
        confidence=confidence,
        source=source,
        timestamp=datetime.now().isoformat()
    )

# Дополнительные эндпоинты
@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/webapp")
async def webapp():
    """Возвращает веб-приложение"""
    possible_paths = [
        "../webapp.html",
        "./webapp.html",
        "webapp.html"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return FileResponse(path)
    
    # Fallback HTML если файл не найден
    fallback_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Taxi Support</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <h1>Taxi Support AI Assistant</h1>
        <p>Сервис работает. Веб-приложение будет доступно позже.</p>
    </body>
    </html>
    """
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=fallback_html)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
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
    
    # Расширенная предобработка текста
    slang_replacements = {
        'че': 'что',
        'там': '',
        'по': '',
        'как работает': 'как',
        'работает': 'работа',
        'как': 'как',
        'где': 'где',
        'что': 'что',
        'какие': 'какие',
        'можно': 'можно',
        'нужно': 'нужно',
        'есть': 'есть',
        'быть': 'быть',
        'время': 'время',
        'деньги': 'деньги',
        'цена': 'цена',
        'стоимость': 'стоимость'
    }
    
    # Убираем пунктуацию и лишние символы
    import re
    text_cleaned = re.sub(r'[^\w\s]', ' ', text_lower)
    text_cleaned = re.sub(r'\s+', ' ', text_cleaned).strip()
    
    processed_text = text_lower
    for slang, replacement in slang_replacements.items():
        processed_text = processed_text.replace(slang, replacement)
    
    # Убираем лишние пробелы
    processed_text = ' '.join(processed_text.split())
    
    # TF-IDF подсчет для точности
    def calculate_tfidf_score(query_words, doc_words):
        """Подсчитывает TF-IDF score между запросом и документом"""
        if not query_words or not doc_words:
            return 0
        
        # Подсчет общих слов
        common_words = set(query_words).intersection(set(doc_words))
        if not common_words:
            return 0
        
        # Простой TF-IDF: log(количество общих слов / общее количество слов)
        tf_score = len(common_words) / len(doc_words)
        idf_score = 1 + (len(common_words) / len(query_words))
        
        return tf_score * idf_score
    
    best_match = None
    best_score = 0
    
    for item in faq_items:
        score = 0
        
        # УЛЬТРА-ГИБКИЙ поиск по ключевым словам с умным stemming
        keywords = item.get("keywords", [])
        keyword_score = 0
        
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
            for ending in russian_endings:
                if root.endswith(ending) and len(root) > len(ending) + 2:
                    root = root[:-len(ending)]
                    break
            
            # Убираем приставки (от длинных к коротким)
            for prefix in prefixes:
                if root.startswith(prefix) and len(root) > len(prefix) + 3:
                    root = root[len(prefix):]
                    break
            
            # Минимальная длина корня
            return root if len(root) >= 3 else word.lower()
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_root = extract_word_root(keyword_lower)
            max_similarity = 0
            
            # УЛЬТРА-ПРОДВИНУТЫЙ поиск по всем словам запроса
            for word in text_cleaned.split():
                if len(word) < 3:  # Пропускаем короткие слова
                    continue
                
                # Вычисляем схожесть с ключевым словом
                similarity = calculate_word_similarity(word, keyword_lower)
                max_similarity = max(max_similarity, similarity)
                
                # Дополнительная проверка с корнем
                word_root = extract_word_root(word)
                root_similarity = calculate_word_similarity(word_root, keyword_root)
                max_similarity = max(max_similarity, root_similarity)
            
            # Конвертируем схожесть в баллы
            if max_similarity >= 1.0:      # Точное совпадение
                keyword_score += 8
            elif max_similarity >= 0.9:    # Совпадение корней
                keyword_score += 7
            elif max_similarity >= 0.8:    # Частичное совпадение корней
                keyword_score += 6
            elif max_similarity >= 0.7:    # Хорошая схожесть
                keyword_score += 5
            elif max_similarity >= 0.6:    # Умеренная схожесть
                keyword_score += 3
            elif max_similarity >= 0.5:    # Слабая схожесть
                keyword_score += 2
            elif max_similarity >= 0.4:    # Минимальная схожесть
                keyword_score += 1
            
            # Дополнительные бонусы за контекст
            if max_similarity > 0:
                # Бонус за множественные совпадения
                word_count = text_cleaned.count(keyword_lower)
                if word_count > 1:
                    keyword_score += word_count * 0.5
                
                # Бонус за позицию слова (начало важнее)
                words = text_cleaned.split()
                for i, word in enumerate(words):
                    if calculate_word_similarity(word, keyword_lower) > 0.7:
                        position_bonus = 1.0 - (i / len(words)) * 0.5
                        keyword_score += position_bonus * 0.5
                        break
            
            # 3. Поиск по всем формам слова (морфологические вариации)
            keyword_forms = [
                keyword_lower,
                keyword_lower + 'а', keyword_lower + 'о', keyword_lower + 'у', keyword_lower + 'ы', keyword_lower + 'и',
                keyword_lower + 'ам', keyword_lower + 'ами', keyword_lower + 'ах',
                keyword_lower + 'ой', keyword_lower + 'ую', keyword_lower + 'ым', keyword_lower + 'ом',
                keyword_lower + 'ый', keyword_lower + 'ая', keyword_lower + 'ое', keyword_lower + 'ые',
                keyword_lower + 'ого', keyword_lower + 'ой', keyword_lower + 'их', keyword_lower + 'ыми',
                keyword_lower[:-1] if keyword_lower.endswith('а') else keyword_lower,  # убираем 'а'
                keyword_lower[:-1] if keyword_lower.endswith('о') else keyword_lower,  # убираем 'о'
                keyword_lower[:-1] if keyword_lower.endswith('и') else keyword_lower,  # убираем 'и'
                keyword_lower[:-2] if keyword_lower.endswith('ый') else keyword_lower,  # убираем 'ый'
                keyword_lower[:-2] if keyword_lower.endswith('ая') else keyword_lower,  # убираем 'ая'
            ]
            
            for form in keyword_forms:
                if form in text_cleaned:
                    keyword_score += 3
                    found_by_root = True
                    break
            
            # Переходим к следующему ключевому слову
            
            # СЕМАНТИЧЕСКИЙ поиск по расширенным синонимам
            extended_synonyms = {
                'доставка': ['доставка', 'доставки', 'доставлять', 'доставщик', 'доставщица', 
                           'курьер', 'курьерская', 'посылка', 'перевозка', 'транспортировка',
                           'груз', 'грузоперевозка', 'логистика', 'отправка', 'получение'],
                'цена': ['цена', 'цены', 'стоимость', 'тариф', 'расценка', 'прайс', 'прейскурант',
                        'себестоимость', 'стоит', 'стоить', 'плата', 'оплата', 'деньги'],
                'карта': ['карта', 'карты', 'карточка', 'пластик', 'платеж', 'банковская',
                         'кредитка', 'дебетка', 'сбербанк', 'visa', 'mastercard'],
                'баланс': ['баланс', 'счет', 'счета', 'деньги', 'средства', 'капитал', 'финансы',
                          'наличка', 'наличные', 'копейки', 'рубли', 'тенге'],
                'водитель': ['водитель', 'водители', 'шофер', 'таксист', 'перевозчик', 'машинист',
                            'управляющий', 'кондуктор', 'пилот'],
                'заказ': ['заказ', 'заказы', 'заказывать', 'заказать', 'покупка', 'бронирование',
                         'резервирование', 'требование', 'просьба', 'заявка']
            }
            
            # Проверяем синонимы для ключевого слова
            if keyword_lower in extended_synonyms:
                for synonym in extended_synonyms[keyword_lower]:
                    for word in text_cleaned.split():
                        if len(word) >= 3:
                            synonym_similarity = calculate_word_similarity(word, synonym)
                            if synonym_similarity > 0.7:
                                keyword_score += synonym_similarity * 3
                                break
            
            # ДОПОЛНИТЕЛЬНЫЙ контекстный поиск
            # Проверяем связанные понятия
            related_concepts = {
                'доставка': ['адрес', 'получатель', 'отправитель', 'посылка', 'пакет', 'товар'],
                'цена': ['дешево', 'дорого', 'скидка', 'промокод', 'акция', 'распродажа'],
                'карта': ['привязать', 'привязка', 'оплата', 'списание', 'пополнение'],
                'баланс': ['пополнить', 'пополнение', 'списать', 'списание', 'история'],
                'водитель': ['машина', 'автомобиль', 'такси', 'поездка', 'маршрут'],
                'заказ': ['сделать', 'оформить', 'отменить', 'изменить', 'статус']
            }
            
            if keyword_lower in related_concepts:
                for concept in related_concepts[keyword_lower]:
                    for word in text_cleaned.split():
                        if len(word) >= 3:
                            concept_similarity = calculate_word_similarity(word, concept)
                            if concept_similarity > 0.8:
                                keyword_score += concept_similarity * 2
                                break
        
        # ГЛУБОКИЙ поиск по вариациям вопросов
        variations = item.get("question_variations", [])
        variation_score = 0
        query_words = text_cleaned.split()
        
        for variation in variations:
            variation_words = variation.lower().split()
            
            # 1. TF-IDF базовый подсчет
            tfidf_score = calculate_tfidf_score(query_words, variation_words)
            variation_score += tfidf_score
            
            # 2. Поиск по биграммам (два слова подряд)
            query_bigrams = set()
            for i in range(len(query_words) - 1):
                query_bigrams.add(f"{query_words[i]} {query_words[i+1]}")
            
            variation_bigrams = set()
            for i in range(len(variation_words) - 1):
                variation_bigrams.add(f"{variation_words[i]} {variation_words[i+1]}")
            
            bigram_matches = len(query_bigrams.intersection(variation_bigrams))
            variation_score += bigram_matches * 0.5
            
            # 3. Поиск по триграммам (три слова подряд)
            if len(query_words) >= 3 and len(variation_words) >= 3:
                query_trigrams = set()
                for i in range(len(query_words) - 2):
                    query_trigrams.add(f"{query_words[i]} {query_words[i+1]} {query_words[i+2]}")
                
                variation_trigrams = set()
                for i in range(len(variation_words) - 2):
                    variation_trigrams.add(f"{variation_words[i]} {variation_words[i+1]} {variation_words[i+2]}")
                
                trigram_matches = len(query_trigrams.intersection(variation_trigrams))
                variation_score += trigram_matches * 1.0
        
        # СЕМАНТИЧЕСКИЙ поиск по основному вопросу
        main_question = item.get("question", "").lower()
        main_question_words = main_question.split()
        
        # 1. TF-IDF базовый подсчет
        main_score = calculate_tfidf_score(query_words, main_question_words) * 2
        
        # 2. Поиск по ключевым фразам
        question_phrases = [
            "как", "что", "где", "когда", "почему", "зачем",
            "можно", "нужно", "есть", "работает", "делать"
        ]
        
        for phrase in question_phrases:
            if phrase in text_cleaned and phrase in main_question:
                main_score += 0.5
        
        # 3. Поиск по порядку слов (важность контекста)
        # Пересечение слов с учетом порядка
        ordered_matches = 0
        for i, word in enumerate(query_words):
            if word in main_question_words:
                # Ищем позицию в вопросе
                for j, q_word in enumerate(main_question_words):
                    if word == q_word:
                        # Близость позиций увеличивает балл
                        position_bonus = 1.0 - (abs(i - j) * 0.1)
                        ordered_matches += max(0.1, position_bonus)
                        break
        
        main_score += ordered_matches * 0.3
        
        # 4. Анализ важности слов
        important_words = ["доставка", "цена", "стоимость", "тариф", "карта", "баланс", "водитель", "заказ"]
        for word in important_words:
            if word in text_cleaned and word in main_question:
                main_score += 1.0  # Высокий бонус за важные слова
        
        # УЛЬТРА-ПРОДВИНУТАЯ нормализация баллов
        max_possible_keywords = len(keywords) * 8  # Максимум баллов за ключевые слова (новый алгоритм)
        normalized_keyword_score = keyword_score / max_possible_keywords if max_possible_keywords > 0 else 0
        
        # Общий балл с максимально улучшенными весами
        score = (
            normalized_keyword_score * 10.0 +   # Ключевые слова = максимальная важность
            variation_score * 2.0 +             # Вариации вопросов (увеличено)
            main_score * 4.0                    # Основной вопрос (увеличено)
        )
        
        # МНОЖЕСТВЕННЫЕ бонусы за комплексное совпадение
        bonus_multiplier = 1.0
        
        if keyword_score > 0 and variation_score > 0 and main_score > 0:
            bonus_multiplier *= 1.3  # 30% бонус за совпадение по всем трем критериям
        
        if keyword_score > len(keywords) * 5:  # Высокий балл за ключевые слова
            bonus_multiplier *= 1.2  # Дополнительный 20% бонус
        
        if variation_score > 2.0:  # Хорошие вариации
            bonus_multiplier *= 1.1  # Дополнительный 10% бонус
        
        score *= bonus_multiplier
        
        # ФИНАЛЬНЫЙ бонус за качество совпадения
        if score > 5.0:  # Очень высокий общий балл
            score += 1.0  # Абсолютный бонус
        
        if score > best_score:
            best_score = score
            best_match = item
    
    # Возвращаем результат только если балл достаточно высокий
    if best_score >= 0.5:  # Понизили порог для лучшего покрытия
        logger.info(f"✅ Fallback поиск найден: {best_score:.3f}")
        if best_match:
            logger.info(f"📋 Найденный вопрос: {best_match.get('question', '')[:50]}...")
        return best_match
    
    logger.info(f"❌ Fallback поиск не нашел совпадений (лучший балл: {best_score:.3f})")
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
            # LLM отключен
            response_text = "Извините, я не нашел подходящий ответ в базе знаний."
    
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
        # LLM отключен
        response_text = "Извините, я не нашел подходящий ответ в базе знаний."
    
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

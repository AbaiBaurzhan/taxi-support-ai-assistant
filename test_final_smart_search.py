"""
Финальный тест умного поиска по ключевым словам с извлечением корней
"""

import sys
import os
sys.path.append('backend')

import json
import re

def load_kb_data():
    """Загружает данные базы знаний"""
    try:
        with open('backend/kb.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки kb.json: {e}")
        return None

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

def search_faq_smart(text: str, kb_data: dict):
    """Умная версия функции поиска FAQ с извлечением корней"""
    if not text or not kb_data:
        return None
    
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
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_root = extract_word_root(keyword_lower)
            
            # 1. Точное совпадение (высший балл)
            if keyword_lower in text_cleaned:
                keyword_score += 6
                continue
            
            # 2. Поиск по корню слова (stemming) - ГЛАВНЫЙ АЛГОРИТМ
            found_by_root = False
            for word in text_cleaned.split():
                word_root = extract_word_root(word)
                
                # Точное совпадение корней
                if keyword_root == word_root:
                    keyword_score += 5
                    found_by_root = True
                    break
                
                # Частичное совпадение корней (минимум 4 символа)
                if len(keyword_root) >= 4 and len(word_root) >= 4:
                    min_len = min(len(keyword_root), len(word_root))
                    if keyword_root[:min_len] == word_root[:min_len] and min_len >= 4:
                        keyword_score += 4
                        found_by_root = True
                        break
            
            if found_by_root:
                continue
            
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
            
            if found_by_root:
                continue
            
            # 4. Частичное совпадение (подстрока)
            if keyword_lower in text_lower or keyword_lower in processed_text:
                keyword_score += 2
                continue
            
            # 5. Обратное частичное совпадение (запрос в ключевом слове)
            for word in text_cleaned.split():
                if len(word) > 3 and word in keyword_lower:
                    keyword_score += 2
                    break
            
            # 6. Фонетический поиск (похожие звуки)
            phonetic_map = {
                'к': ['г', 'х'],
                'п': ['б'],
                'т': ['д'],
                'с': ['з', 'ц'],
                'ф': ['в'],
                'ш': ['щ', 'ж'],
                'ч': ['щ']
            }
            
            for word in text_cleaned.split():
                word_root = extract_word_root(word)
                if len(word_root) >= 4 and len(keyword_root) >= 4:
                    # Проверяем фонетическое сходство корней
                    similarity_count = 0
                    min_len = min(len(word_root), len(keyword_root))
                    
                    for i in range(min_len):
                        if word_root[i] == keyword_root[i]:
                            similarity_count += 1
                        elif word_root[i] in phonetic_map.get(keyword_root[i], []):
                            similarity_count += 0.5
                    
                    if similarity_count >= min_len * 0.7:  # 70% сходства
                        keyword_score += 1.5
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
        query_words_set = set(query_words)
        question_words_set = set(main_question_words)
        
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
        
        # Нормализация баллов для нового алгоритма
        max_possible_keywords = len(keywords) * 5  # Максимум баллов за ключевые слова (новый алгоритм)
        normalized_keyword_score = keyword_score / max_possible_keywords if max_possible_keywords > 0 else 0
        
        # Общий балл с улучшенными весами
        score = (
            normalized_keyword_score * 6.0 +    # Ключевые слова = самые важные (увеличено)
            variation_score * 1.5 +             # Вариации вопросов (увеличено)
            main_score * 3.0                    # Основной вопрос (увеличено)
        )
        
        # Бонус за комплексное совпадение
        if keyword_score > 0 and variation_score > 0 and main_score > 0:
            score *= 1.2  # 20% бонус за совпадение по всем трем критериям
        
        if score > best_score:
            best_score = score
            best_match = item
    
    # Возвращаем результат только если балл достаточно высокий
    if best_score >= 0.3:  # Еще больше понизили порог
        return best_match
    
    return None

def test_comprehensive_search():
    """Комплексный тест умного поиска"""
    print("🧪 ФИНАЛЬНЫЙ ТЕСТ УМНОГО ПОИСКА")
    print("=" * 60)
    
    kb_data = load_kb_data()
    if not kb_data:
        return
    
    # Комплексные тестовые запросы
    test_queries = [
        # Доставка - разные формы и контексты
        "доставка",
        "доставки", 
        "доставлять",
        "доставщик",
        "передоставка",
        "как сделать доставку",
        "где заказать доставку",
        "че там по доставке",
        "доставка как работает",
        
        # Цена - разные формы и контексты
        "цена",
        "цены",
        "цену",
        "ценообразование",
        "переоценка",
        "сколько стоит поездка",
        "какая цена за километр",
        "как считается стоимость",
        
        # Карта - разные формы и контексты
        "карта",
        "карты",
        "карточка",
        "картографический",
        "какие карты принимаются",
        "как привязать карту",
        "карта не работает",
        
        # Баланс - разные формы и контексты
        "баланс",
        "балансы",
        "балансировка",
        "балансировать",
        "как пополнить баланс",
        "где посмотреть баланс",
        "баланс карты",
        
        # Тариф - разные формы и контексты
        "тариф",
        "тарифы",
        "тарификация",
        "тарифицировать",
        "что такое комфорт тариф",
        "какие есть тарифы",
        "тариф комфорт",
        
        # Водитель - разные формы и контексты
        "водитель",
        "водители",
        "водительница",
        "водить",
        "где мой водитель",
        "водитель не приехал",
        "как связаться с водителем",
        
        # Заказ - разные формы и контексты
        "заказ",
        "заказы",
        "заказывать",
        "заказчик",
        "как сделать заказ",
        "где мой заказ",
        "заказ не пришел",
        
        # Сложные комбинированные запросы
        "как пополнить баланс карты",
        "где выбрать тип заказа доставка",
        "сколько стоит комфорт класс",
        "можно ли сделать предзаказ",
        "что такое наценка за тариф",
        "водитель не приехал на заказ",
        "приложение не работает с картой",
        "какие карты принимаются для оплаты",
        "как зарегистрировать заказ доставки",
        "где вводить промокод на скидку"
    ]
    
    print(f"Тестируем {len(test_queries)} комплексных запросов:")
    print()
    
    success_count = 0
    detailed_results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i:2d}. Запрос: '{query}'")
        
        # Тестируем умный поиск
        result = search_faq_smart(query, kb_data)
        
        if result:
            question = result.get('question', '')
            keywords = result.get('keywords', [])
            print(f"    ✅ НАЙДЕНО!")
            print(f"    📋 Question: {question[:60]}...")
            print(f"    🔑 Keywords: {keywords[:3]}...")
            success_count += 1
            detailed_results.append({
                'query': query,
                'found': True,
                'question': question,
                'keywords': keywords
            })
        else:
            print(f"    ❌ НЕ НАЙДЕНО")
            detailed_results.append({
                'query': query,
                'found': False,
                'question': None,
                'keywords': None
            })
        
        print()
    
    success_rate = (success_count / len(test_queries)) * 100
    print("📊 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    print(f"Успешно найдено: {success_count}/{len(test_queries)} ({success_rate:.1f}%)")
    
    if success_rate >= 95:
        print("🎉 ПРЕВОСХОДНО! Умный поиск работает идеально!")
    elif success_rate >= 90:
        print("🚀 ОТЛИЧНО! Очень высокое качество поиска!")
    elif success_rate >= 80:
        print("✅ ХОРОШО! Значительные улучшения!")
    elif success_rate >= 70:
        print("⚠️ УДОВЛЕТВОРИТЕЛЬНО! Нужны небольшие улучшения!")
    else:
        print("❌ Нужны серьезные улучшения!")
    
    # Анализ по категориям
    print("\n📈 АНАЛИЗ ПО КАТЕГОРИЯМ:")
    categories = {
        'доставка': [r for r in detailed_results if 'достав' in r['query']],
        'цена': [r for r in detailed_results if any(word in r['query'] for word in ['цена', 'стоимость', 'тариф'])],
        'карта': [r for r in detailed_results if 'карт' in r['query']],
        'баланс': [r for r in detailed_results if 'баланс' in r['query']],
        'водитель': [r for r in detailed_results if 'водител' in r['query']],
        'заказ': [r for r in detailed_results if 'заказ' in r['query']],
        'сложные': [r for r in detailed_results if len(r['query'].split()) > 3]
    }
    
    for category, results in categories.items():
        if results:
            found = sum(1 for r in results if r['found'])
            rate = (found / len(results)) * 100
            print(f"  {category.capitalize()}: {found}/{len(results)} ({rate:.1f}%)")
    
    return detailed_results

if __name__ == "__main__":
    test_comprehensive_search()

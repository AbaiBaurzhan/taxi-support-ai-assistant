"""
Тест ультра-гибкого поиска по ключевым словам
"""

import sys
import os
sys.path.append('backend')

import json
import re

def search_faq_ultra_flexible(text: str, kb_data: dict):
    """Ультра-гибкая версия функции поиска FAQ"""
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
        
        # УЛЬТРА-ГИБКИЙ поиск по ключевым словам
        keywords = item.get("keywords", [])
        keyword_score = 0
        
        for keyword in keywords:
            # 1. Точное совпадение (высший балл)
            if keyword.lower() in text_cleaned:
                keyword_score += 5
                continue
            
            # 2. Поиск по корню слова (stemming)
            keyword_root = keyword.lower()
            for word in text_cleaned.split():
                if len(keyword_root) > 3 and len(word) > 3:
                    # Проверяем общий корень (первые 4-5 символов)
                    common_root = min(len(keyword_root), len(word))
                    if keyword_root[:common_root] == word[:common_root] and common_root >= 4:
                        keyword_score += 4
                        break
            
            # 3. Частичное совпадение (подстрока)
            if keyword.lower() in text_lower or keyword.lower() in processed_text:
                keyword_score += 3
                continue
            
            # 4. Обратное частичное совпадение (запрос в ключевом слове)
            for word in text_cleaned.split():
                if len(word) > 3 and word in keyword.lower():
                    keyword_score += 2
                    break
            
            # 5. Поиск по синонимам и вариациям
            keyword_variations = [
                keyword.lower(),
                keyword.lower().replace('и', ''),
                keyword.lower().replace('о', 'а'),
                keyword.lower().replace('е', 'ё'),
                keyword.lower() + 'ы',
                keyword.lower() + 'и',
                keyword.lower() + 'а',
                keyword.lower() + 'у'
            ]
            
            for variation in keyword_variations:
                if variation in text_cleaned:
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
                if len(word) >= 4 and len(keyword) >= 4:
                    # Проверяем фонетическое сходство
                    similarity_count = 0
                    min_len = min(len(word), len(keyword))
                    
                    for i in range(min_len):
                        if word[i] == keyword[i]:
                            similarity_count += 1
                        elif word[i] in phonetic_map.get(keyword[i], []):
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

def load_kb_data():
    """Загружает данные базы знаний"""
    try:
        with open('backend/kb.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки kb.json: {e}")
        return None

def test_ultra_flexible_search():
    """Тестирует ультра-гибкий поиск"""
    print("🚀 Тестирование УЛЬТРА-ГИБКОГО поиска")
    print("=" * 60)
    
    kb_data = load_kb_data()
    if not kb_data:
        return
    
    # Сложные тестовые запросы
    test_queries = [
        # Точные совпадения
        "доставка",
        "цена поездки",
        "баланс карты",
        
        # Сленговые запросы
        "че там по доставке",
        "как работает тариф",
        "сколько стоит такси",
        
        # Опечатки и вариации
        "доставк",  # без окончания
        "цены",  # множественное число
        "карты",  # множественное число
        "тарифы",  # множественное число
        
        # Фонетически похожие
        "доставгка",  # опечатка
        "цена",  # похоже на "цены"
        "карта",  # похоже на "карты"
        
        # Сложные фразы
        "как пополнить баланс карты",
        "где мой заказ доставки",
        "сколько стоит комфорт класс",
        "можно ли сделать предзаказ",
        "что такое наценка за тариф",
        "водитель не приехал на заказ",
        "приложение не работает с картой",
        "какие карты принимаются для оплаты"
    ]
    
    print(f"Тестируем {len(test_queries)} сложных запросов:")
    print()
    
    success_count = 0
    for i, query in enumerate(test_queries, 1):
        print(f"{i:2d}. Запрос: '{query}'")
        
        # Тестируем ультра-гибкий поиск
        result = search_faq_ultra_flexible(query, kb_data)
        
        if result:
            print(f"    ✅ НАЙДЕНО!")
            print(f"    📋 Question: {result.get('question', '')[:60]}...")
            success_count += 1
        else:
            print(f"    ❌ НЕ НАЙДЕНО")
        
        print()
    
    success_rate = (success_count / len(test_queries)) * 100
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"Успешно найдено: {success_count}/{len(test_queries)} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 ПРЕВОСХОДНО! Ультра-гибкий поиск работает идеально!")
    elif success_rate >= 80:
        print("🚀 ОТЛИЧНО! Очень высокое качество поиска!")
    elif success_rate >= 70:
        print("✅ ХОРОШО! Значительные улучшения!")
    else:
        print("❌ Нужны дополнительные улучшения")

if __name__ == "__main__":
    test_ultra_flexible_search()

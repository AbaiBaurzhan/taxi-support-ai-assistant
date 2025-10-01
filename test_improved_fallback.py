"""
Тест улучшенного fallback поиска
"""

import sys
import os
sys.path.append('backend')

# Импортируем только функцию поиска без FastAPI
import json
import re

def search_faq_standalone(text: str, kb_data: dict):
    """Стояночная версия функции поиска FAQ"""
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
        
        # Поиск по ключевым словам (улучшенный)
        keywords = item.get("keywords", [])
        keyword_score = 0
        for keyword in keywords:
            # Точное совпадение = высший балл
            if keyword in text_cleaned:
                keyword_score += 3
            elif keyword in text_lower or keyword in processed_text:
                keyword_score += 2
            # Частичное совпадение
            elif any(keyword in word or word in keyword for word in text_cleaned.split()):
                keyword_score += 1
        
        # Поиск по вариациям вопросов (TF-IDF)
        variations = item.get("question_variations", [])
        variation_score = 0
        query_words = text_cleaned.split()
        for variation in variations:
            variation_words = variation.lower().split()
            tfidf_score = calculate_tfidf_score(query_words, variation_words)
            variation_score += tfidf_score
        
        # Поиск по основному вопросу (TF-IDF)
        main_question = item.get("question", "").lower()
        main_question_words = main_question.split()
        main_score = calculate_tfidf_score(query_words, main_question_words) * 2  # Удваиваем важность
        
        # Нормализация баллов для лучшей точности
        max_possible_keywords = len(keywords) * 3  # Максимум баллов за ключевые слова
        normalized_keyword_score = keyword_score / max_possible_keywords if max_possible_keywords > 0 else 0
        
        # Общий балл с весами и нормализацией
        score = (
            normalized_keyword_score * 4.0 +    # Ключевые слова = самые важные (нормализованные)
            variation_score * 1.0 +             # Вариации вопросов (TF-IDF)
            main_score * 2.0                    # Основной вопрос (TF-IDF удвоенный)
        )
        
        if score > best_score:
            best_score = score
            best_match = item
    
    # Возвращаем результат только если балл достаточно высокий
    if best_score >= 0.5:  # Понизили порог для лучшего покрытия
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

def test_improved_fallback():
    """Тестирует улучшенный fallback поиск"""
    print("🧪 Тестирование улучшенного fallback поиска")
    print("=" * 60)
    
    kb_data = load_kb_data()
    if not kb_data:
        return
    
    # Тестовые запросы
    test_queries = [
        "доставка",
        "че там по доставке",
        "как работает доставка",
        "цена поездки",
        "сколько стоит такси",
        "какие карты принимаются",
        "баланс на карте",
        "как пополнить счет",
        "водитель не приехал",
        "где мой заказ",
        "комфорт класс",
        "предзаказ можно сделать",
        "наценка за что",
        "моточасы что это",
        "таксометр работает",
        "приложение глючит"
    ]
    
    print(f"Тестируем {len(test_queries)} запросов:")
    print()
    
    success_count = 0
    for i, query in enumerate(test_queries, 1):
        print(f"{i:2d}. Запрос: '{query}'")
        
        # Тестируем fallback поиск
        result = search_faq_standalone(query, kb_data)
        
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
    
    if success_rate >= 80:
        print("🎉 Отлично! Fallback работает очень хорошо!")
    elif success_rate >= 60:
        print("✅ Хорошо! Есть значительные улучшения!")
    else:
        print("❌ Нужны дополнительные улучшения")

if __name__ == "__main__":
    test_improved_fallback()

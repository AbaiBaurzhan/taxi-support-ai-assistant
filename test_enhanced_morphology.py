"""
Тест улучшенной морфологической системы для BZ.txt
"""

import sys
import os
sys.path.append('backend')

from enhanced_morphological_analyzer import enhance_classification_with_morphology, enhanced_analyzer
import json

def load_kb_data():
    """Загружает данные базы знаний"""
    try:
        with open('backend/kb.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки kb.json: {e}")
        return None

def test_morphological_analysis():
    """Тестирует морфологический анализ"""
    print("🧪 Тестирование улучшенной морфологической системы")
    print("=" * 60)
    
    # Загружаем базу знаний
    kb_data = load_kb_data()
    if not kb_data:
        return
    
    print(f"✅ Загружено {len(kb_data.get('faq', []))} FAQ элементов")
    print()
    
    # Тестовые запросы с различными вариантами вопросов
    test_queries = [
        # Наценка
        "что такое наценка?",
        "почему у меня появилась доплата?",
        "что значит повышающий коэффициент?",
        "откуда берется надбавка к цене?",
        "зачем делают наценку?",
        "почему стоимость стала выше?",
        "из-за чего цена выросла?",
        
        # Тариф Комфорт
        "что такое тариф комфорт?",
        "чем отличается комфорт от обычного?",
        "что входит в тариф комфорт?",
        "комфорт это какие машины?",
        "насколько дороже поездка в комфорте?",
        "комфорт это камри?",
        
        # Расценки
        "как узнать расценку?",
        "как посмотреть примерную стоимость?",
        "где можно увидеть расценки заранее?",
        "можно ли узнать цену до заказа?",
        "как рассчитать цену по таксометру?",
        
        # Предзаказ
        "как сделать предварительный заказ?",
        "можно ли вызвать такси заранее?",
        "как оформить предзаказ на время?",
        "можно ли заранее заказать машину?",
        
        # Доставка
        "как зарегистрировать заказ доставки?",
        "как оформить заказ на доставку?",
        "где выбрать тип заказа доставка?",
        "как вызвать курьера?",
        
        # Водитель
        "как мне принимать заказы?",
        "что нужно чтобы работать водителем?",
        "как зарегистрироваться как водитель?",
        "где найти ленту заказов?",
        
        # Баланс
        "как пополнить баланс?",
        "каким образом пополнить баланс?",
        "где можно пополнить счет?",
        "как привязать карту?",
        
        # Моточасы
        "что такое моточасы?",
        "что означают моточасы в тарифе?",
        "как считается оплата за время?",
        "зачем ввели оплату за минуты?",
        
        # Таксометр
        "как работать с таксометром?",
        "как правильно пользоваться таксометром?",
        "когда нажимать поехали и остановить?",
        "как завершить заказ в приложении?",
        
        # Приложение
        "приложение не работает что делать?",
        "приложение не запускается",
        "как обновить aparu?",
        "может ли помочь настройка gps?"
    ]
    
    # Тестируем каждый запрос
    results = []
    for i, query in enumerate(test_queries, 1):
        print(f"{i:2d}. Запрос: '{query}'")
        
        # Тестируем морфологический анализ
        result = enhance_classification_with_morphology(query, kb_data)
        
        if result.get('matched_item'):
            matched_item = result['matched_item']
            confidence = result.get('confidence', 0)
            language = result.get('language', 'ru')
            
            print(f"    ✅ Найдено совпадение!")
            print(f"    📊 Confidence: {confidence:.2f}")
            print(f"    🌐 Language: {language}")
            print(f"    ❓ Question: {matched_item.get('question', '')[:50]}...")
            print(f"    💬 Answer: {matched_item.get('answer', '')[:80]}...")
            
            results.append({
                'query': query,
                'found': True,
                'confidence': confidence,
                'language': language,
                'question': matched_item.get('question', ''),
                'answer_length': len(matched_item.get('answer', ''))
            })
        else:
            print(f"    ❌ Совпадение не найдено")
            results.append({
                'query': query,
                'found': False,
                'confidence': 0,
                'language': result.get('language', 'ru')
            })
        
        print()
    
    # Статистика
    print("📊 СТАТИСТИКА ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    total_queries = len(results)
    found_queries = sum(1 for r in results if r['found'])
    success_rate = (found_queries / total_queries) * 100
    
    print(f"Всего запросов: {total_queries}")
    print(f"Найдено совпадений: {found_queries}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    if found_queries > 0:
        avg_confidence = sum(r['confidence'] for r in results if r['found']) / found_queries
        print(f"Средняя уверенность: {avg_confidence:.2f}")
        
        # Языковая статистика
        ru_count = sum(1 for r in results if r.get('language') == 'ru')
        kz_count = sum(1 for r in results if r.get('language') == 'kz')
        print(f"Русский язык: {ru_count}")
        print(f"Казахский язык: {kz_count}")
    
    print()
    
    # Показываем примеры неудачных запросов
    failed_queries = [r for r in results if not r['found']]
    if failed_queries:
        print("❌ ЗАПРОСЫ БЕЗ СОВПАДЕНИЙ:")
        for r in failed_queries[:5]:  # Показываем первые 5
            print(f"  - '{r['query']}'")
        if len(failed_queries) > 5:
            print(f"  ... и еще {len(failed_queries) - 5}")

def test_morphological_features():
    """Тестирует отдельные функции морфологического анализа"""
    print("\n🔬 ТЕСТИРОВАНИЕ МОРФОЛОГИЧЕСКИХ ФУНКЦИЙ")
    print("=" * 60)
    
    # Тест нормализации
    test_texts = [
        "Что такое НАЦЕНКА???",
        "Как пополнить баланс!",
        "Приложение не работает...",
        "Моточасы - это что?"
    ]
    
    print("📝 Нормализация текста:")
    for text in test_texts:
        normalized = enhanced_analyzer.normalize_text(text)
        print(f"  '{text}' -> '{normalized}'")
    
    print()
    
    # Тест получения основы слова
    test_words = [
        "наценка", "наценки", "наценку",
        "комфорт", "комфорта", "комфортом",
        "доставка", "доставки", "доставку",
        "водитель", "водителя", "водителю"
    ]
    
    print("🔤 Получение основы слова:")
    for word in test_words:
        stem = enhanced_analyzer.get_word_stem(word)
        print(f"  '{word}' -> '{stem}'")
    
    print()
    
    # Тест расширения запроса
    test_queries = [
        "наценка",
        "тариф комфорт",
        "пополнить баланс"
    ]
    
    print("🔄 Расширение запроса:")
    for query in test_queries:
        expanded = enhanced_analyzer.expand_query(query)
        print(f"  '{query}' -> {expanded[:5]}...")  # Показываем первые 5 вариантов

if __name__ == "__main__":
    test_morphological_analysis()
    test_morphological_features()

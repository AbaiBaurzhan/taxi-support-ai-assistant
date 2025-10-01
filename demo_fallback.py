"""
Демонстрация работы Fallback системы
"""

def demo_fallback_processing():
    print("🔄 ДЕМОНСТРАЦИЯ FALLBACK СИСТЕМЫ")
    print("=" * 50)
    
    # Пример запроса
    original_query = "че там по доставке ?"
    print(f"📝 Оригинальный запрос: '{original_query}'")
    print()
    
    # Шаг 1: Предобработка сленга
    print("🔧 ШАГ 1: Предобработка сленга")
    slang_replacements = {
        'че': 'что',
        'там': '',
        'по': '',
        'как работает': 'как',
        'работает': 'работа'
    }
    
    text_lower = original_query.lower()
    processed_text = text_lower
    
    for slang, replacement in slang_replacements.items():
        processed_text = processed_text.replace(slang, replacement)
    
    # Убираем лишние пробелы
    processed_text = ' '.join(processed_text.split())
    
    print(f"   Оригинальный: '{text_lower}'")
    print(f"   Обработанный: '{processed_text}'")
    print()
    
    # Шаг 2: Поиск в базе знаний
    print("🔍 ШАГ 2: Поиск в базе знаний")
    
    # Имитация элемента базы знаний
    faq_item = {
        "question": "Как зарегистрировать заказ доставки?",
        "keywords": ["доставка", "заказ", "регистрация"],
        "question_variations": [
            "как сделать заказ доставки",
            "как оформить доставку",
            "доставка как работает"
        ]
    }
    
    print(f"   Ищем в: '{faq_item['question']}'")
    print(f"   Ключевые слова: {faq_item['keywords']}")
    print()
    
    # Шаг 3: Подсчет баллов
    print("📊 ШАГ 3: Подсчет баллов")
    
    # Поиск по ключевым словам
    keyword_score = 0
    for keyword in faq_item["keywords"]:
        if keyword in text_lower or keyword in processed_text:
            keyword_score += 1
            print(f"   ✅ Найдено ключевое слово: '{keyword}'")
    
    # Поиск по вариациям вопросов
    variation_score = 0
    for variation in faq_item["question_variations"]:
        variation_words = set(variation.lower().split())
        text_words = set(text_lower.split())
        processed_words = set(processed_text.split())
        common_words = len(variation_words.intersection(text_words)) + len(variation_words.intersection(processed_words))
        if common_words > 0:
            variation_score += common_words
            print(f"   ✅ Найдено совпадение в вариации: '{variation}' (баллов: {common_words})")
    
    # Поиск по основному вопросу
    main_question = faq_item["question"].lower()
    main_score = 0
    for word in main_question.split():
        if word in text_lower or word in processed_text:
            main_score += 1
            print(f"   ✅ Найдено слово в основном вопросе: '{word}'")
    
    print()
    
    # Шаг 4: Итоговый балл
    print("🎯 ШАГ 4: Итоговый балл")
    total_score = (
        keyword_score * 2.0 +     # Ключевые слова важнее
        variation_score * 0.5 +   # Вариации вопросов
        main_score * 1.0          # Основной вопрос
    )
    
    print(f"   Ключевые слова: {keyword_score} × 2.0 = {keyword_score * 2.0}")
    print(f"   Вариации: {variation_score} × 0.5 = {variation_score * 0.5}")
    print(f"   Основной вопрос: {main_score} × 1.0 = {main_score * 1.0}")
    print(f"   ИТОГО: {total_score}")
    print()
    
    # Шаг 5: Решение
    print("✅ ШАГ 5: Решение")
    if total_score >= 1.0:
        print(f"   🎉 НАЙДЕНО! Балл {total_score} >= 1.0")
        print(f"   📋 Ответ: {faq_item['question']}")
    else:
        print(f"   ❌ НЕ НАЙДЕНО. Балл {total_score} < 1.0")
        print("   🔄 Переход к следующему уровню fallback")

if __name__ == "__main__":
    demo_fallback_processing()

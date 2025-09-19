#!/usr/bin/env python3
"""
🎯 ТЕСТ СИСТЕМЫ ВЫБОРА ГОТОВЫХ ОТВЕТОВ
"""

from main import answer_selection_client
import time

print("🎯 ТЕСТИРОВАНИЕ СИСТЕМЫ ВЫБОРА ГОТОВЫХ ОТВЕТОВ:")
print("=" * 60)

# Тестовые вопросы из вариаций
test_questions = [
    "Что такое наценка?",
    "Почему у меня появилась доплата в заказе?",
    "Что такое Тариф Комфорт?",
    "Чем отличается Комфорт от обычного тарифа?",
    "Как узнать расценку?",
    "Как посмотреть примерную стоимость поездки?",
    "Как заказать доставку?",
    "Как зарегистрировать заказ доставки?",
    "Как сделать предварительный заказ?",
    "Как мне принимать заказы и что для этого нужно?"
]

results = []
for i, question in enumerate(test_questions, 1):
    print(f"{i:2d}. {question}")
    start_time = time.time()
    result = answer_selection_client.find_best_answer(question)
    processing_time = time.time() - start_time
    
    print(f"    ✅ Ответ: {result['answer'][:80]}...")
    print(f"    📊 Категория: {result['category']}")
    print(f"    🎯 Уверенность: {result['confidence']}")
    print(f"    🔧 Источник: {result['source']}")
    print(f"    ⏱️ Время: {processing_time:.2f}с")
    print("-" * 50)
    
    results.append({
        'question': question,
        'answer': result['answer'],
        'category': result['category'],
        'confidence': result['confidence'],
        'source': result['source'],
        'time': processing_time
    })

# Статистика
print("\n📊 СТАТИСТИКА:")
print("=" * 40)

llm_selection_count = sum(1 for r in results if r['source'] == 'llm_answer_selection')
keyword_search_count = sum(1 for r in results if r['source'] == 'keyword_search')
fallback_count = sum(1 for r in results if r['source'] == 'fallback')

print(f"🎯 LLM выбор ответов: {llm_selection_count}/{len(results)} ({llm_selection_count/len(results)*100:.1f}%)")
print(f"🔍 Поиск по ключевым словам: {keyword_search_count}/{len(results)} ({keyword_search_count/len(results)*100:.1f}%)")
print(f"❌ Fallback: {fallback_count}/{len(results)} ({fallback_count/len(results)*100:.1f}%)")

avg_time = sum(r['time'] for r in results) / len(results)
print(f"⏱️ Среднее время: {avg_time:.2f}с")

# Проверяем качество ответов
good_answers = sum(1 for r in results if r['confidence'] > 0.8)
print(f"✅ Качественных ответов: {good_answers}/{len(results)} ({good_answers/len(results)*100:.1f}%)")

# Проверяем правильность выбора ответов
correct_selections = 0
for i, result in enumerate(results):
    question = result['question'].lower()
    category = result['category'].lower()
    
    # Простая проверка правильности выбора
    if 'наценка' in question or 'доплата' in question:
        if 'ответ 1' in category or 'keyword_match' in category:
            correct_selections += 1
    elif 'комфорт' in question or 'тариф' in question:
        if 'ответ 2' in category or 'keyword_match' in category:
            correct_selections += 1
    elif 'расценка' in question or 'стоимость' in question:
        if 'ответ 3' in category or 'keyword_match' in category:
            correct_selections += 1
    elif 'доставка' in question or 'заказ' in question:
        if 'ответ 4' in category or 'keyword_match' in category:
            correct_selections += 1
    elif 'предварительный' in question:
        if 'ответ 5' in category or 'keyword_match' in category:
            correct_selections += 1
    elif 'принимать' in question or 'водитель' in question:
        if 'ответ 6' in category or 'keyword_match' in category:
            correct_selections += 1

print(f"🎯 Правильных выборов: {correct_selections}/{len(results)} ({correct_selections/len(results)*100:.1f}%)")

print("\n🎯 ТЕСТ ЗАВЕРШЕН!")

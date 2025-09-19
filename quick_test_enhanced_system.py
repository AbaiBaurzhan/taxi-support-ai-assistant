#!/usr/bin/env python3
"""
🔍 БЫСТРЫЙ ТЕСТ УЛУЧШЕННОЙ СИСТЕМЫ БЕЗ СЕРВЕРА
"""

from main import enhanced_search_client
import time

print("🔍 ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ СИСТЕМЫ:")
print("=" * 50)

test_questions = [
    "Что такое наценка?",
    "Как заказать доставку?", 
    "Как пополнить баланс?",
    "Приложение не работает",
    "Что такое тариф комфорт?",
    "Почему дорого?",
    "Курьер не приехал",
    "Не могу оплатить",
    "Ошибка в приложении",
    "Чем отличается комфорт?"
]

results = []
for i, question in enumerate(test_questions, 1):
    print(f"{i:2d}. {question}")
    start_time = time.time()
    result = enhanced_search_client.find_best_answer(question)
    processing_time = time.time() - start_time
    
    print(f"    ✅ Ответ: {result['answer'][:80]}...")
    print(f"    📊 Категория: {result['category']}")
    print(f"    🎯 Уверенность: {result['confidence']}")
    print(f"    🔧 Источник: {result['source']}")
    print(f"    ⏱️ Время: {processing_time:.2f}с")
    print("-" * 40)
    
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
print("=" * 30)

enhanced_search_count = sum(1 for r in results if r['source'] == 'enhanced_simple_search')
llm_search_count = sum(1 for r in results if r['source'] == 'optimized_llm_search')
fallback_count = sum(1 for r in results if r['source'] == 'fallback')

print(f"🔍 Улучшенный простой поиск: {enhanced_search_count}/{len(results)} ({enhanced_search_count/len(results)*100:.1f}%)")
print(f"🧠 LLM поиск: {llm_search_count}/{len(results)} ({llm_search_count/len(results)*100:.1f}%)")
print(f"❌ Fallback: {fallback_count}/{len(results)} ({fallback_count/len(results)*100:.1f}%)")

avg_time = sum(r['time'] for r in results) / len(results)
print(f"⏱️ Среднее время: {avg_time:.2f}с")

# Проверяем правильность ответов
correct_answers = 0
for i, result in enumerate(results):
    question = result['question'].lower()
    category = result['category'].lower()
    
    # Простая проверка правильности
    if 'наценка' in question and 'pricing' in category:
        correct_answers += 1
    elif 'доставка' in question and 'delivery' in category:
        correct_answers += 1
    elif 'баланс' in question and 'balance' in category:
        correct_answers += 1
    elif 'приложение' in question and 'app' in category:
        correct_answers += 1
    elif 'тариф' in question and 'tariffs' in category:
        correct_answers += 1
    elif 'дорого' in question and 'pricing' in category:
        correct_answers += 1
    elif 'курьер' in question and 'delivery' in category:
        correct_answers += 1
    elif 'оплатить' in question and 'balance' in category:
        correct_answers += 1
    elif 'ошибка' in question and 'app' in category:
        correct_answers += 1
    elif 'комфорт' in question and 'tariffs' in category:
        correct_answers += 1

print(f"✅ Правильных ответов: {correct_answers}/{len(results)} ({correct_answers/len(results)*100:.1f}%)")

print("\n🎯 ТЕСТ ЗАВЕРШЕН!")

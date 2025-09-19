#!/usr/bin/env python3
"""
🎯 ТЕСТ УЛЬТРА-ПРОСТОЙ LLM СИСТЕМЫ
"""

from main import ultra_simple_llm_client
import time

print("🎯 ТЕСТИРОВАНИЕ УЛЬТРА-ПРОСТОЙ LLM СИСТЕМЫ:")
print("=" * 50)

# Тестовые вопросы
test_questions = [
    "Что такое наценка?",
    "Что такое Тариф Комфорт?", 
    "Как узнать расценку?",
    "Как заказать доставку?",
    "Как сделать предварительный заказ?",
    "Как мне принимать заказы?",
    "Как пополнить баланс?",
    "Приложение не работает",
    "Как использовать промокод?",
    "Как отменить заказ?"
]

results = []
for i, question in enumerate(test_questions, 1):
    print(f"{i:2d}. {question}")
    start_time = time.time()
    result = ultra_simple_llm_client.find_best_answer(question)
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

llm_search_count = sum(1 for r in results if r['source'] == 'ultra_simple_llm')
keyword_search_count = sum(1 for r in results if r['source'] == 'keyword_search')
fallback_count = sum(1 for r in results if r['source'] == 'fallback')

print(f"🎯 Ультра-простая LLM: {llm_search_count}/{len(results)} ({llm_search_count/len(results)*100:.1f}%)")
print(f"🔍 Поиск по ключевым словам: {keyword_search_count}/{len(results)} ({keyword_search_count/len(results)*100:.1f}%)")
print(f"❌ Fallback: {fallback_count}/{len(results)} ({fallback_count/len(results)*100:.1f}%)")

avg_time = sum(r['time'] for r in results) / len(results)
print(f"⏱️ Среднее время: {avg_time:.2f}с")

# Проверяем качество ответов
good_answers = sum(1 for r in results if r['confidence'] > 0.8)
print(f"✅ Качественных ответов: {good_answers}/{len(results)} ({good_answers/len(results)*100:.1f}%)")

print("\n🎯 ТЕСТ ЗАВЕРШЕН!")

#!/usr/bin/env python3
"""
🧪 ТЕСТ УЛУЧШЕННОЙ СИСТЕМЫ С МОРФОЛОГИЕЙ
"""

from enhanced_main import simple_answer_client
import time

print("🧪 ТЕСТ УЛУЧШЕННОЙ СИСТЕМЫ С МОРФОЛОГИЕЙ:")
print("=" * 70)

# Тестовые вопросы с морфологическими вариациями
test_questions = [
    # Наценка - морфологические формы
    "наценки", "наценку", "наценкой", "наценке",
    "доплаты", "доплату", "доплатой", "доплате",
    "надбавки", "надбавку", "надбавкой", "надбавке",
    "коэффициенты", "коэффициента", "коэффициентом",
    
    # Комфорт - морфологические формы
    "комфорты", "комфорта", "комфортом", "комфорте",
    "тарифы", "тарифа", "тарифом", "тарифе",
    "классы", "класса", "классом", "классе",
    
    # Баланс - морфологические формы
    "балансы", "баланса", "балансом", "балансе",
    "пополняю", "пополняешь", "пополняет", "пополняем",
    "оплачиваю", "оплачиваешь", "оплачивает", "оплачиваем",
    
    # Приложение - морфологические формы
    "приложения", "приложения", "приложением", "приложении",
    "обновляю", "обновляешь", "обновляет", "обновляем",
    
    # Промокод - морфологические формы
    "промокоды", "промокода", "промокодом", "промокоде",
    "скидки", "скидку", "скидкой", "скидке",
    "бонусы", "бонуса", "бонусом", "бонусе",
    
    # Отмена - морфологические формы
    "отменяю", "отменяешь", "отменяет", "отменяем",
    "отмены", "отмену", "отменой", "отмене",
    
    # Сложные вопросы
    "Почему у меня наценки?", "Как пополнить балансы?", "Что такое комфорты?",
    "Как использовать промокоды?", "Можно ли отменить заказы?", "Приложения не работают"
]

results = []
for i, question in enumerate(test_questions, 1):
    print(f"{i:3d}. {question}")
    start_time = time.time()
    result = simple_answer_client.find_best_answer(question)
    processing_time = time.time() - start_time
    
    print(f"     ✅ Ответ: {result['answer'][:60]}...")
    print(f"     📊 Категория: {result['category']}")
    print(f"     🎯 Уверенность: {result['confidence']}")
    print(f"     🔧 Источник: {result['source']}")
    print(f"     ⏱️ Время: {processing_time:.2f}с")
    print("-" * 60)
    
    results.append({
        'question': question,
        'answer': result['answer'],
        'category': result['category'],
        'confidence': result['confidence'],
        'source': result['source'],
        'time': processing_time
    })

# Статистика
print("\n📊 СТАТИСТИКА УЛУЧШЕННОЙ СИСТЕМЫ:")
print("=" * 50)

llm_count = sum(1 for r in results if r['source'] == 'enhanced_llm')
morphological_count = sum(1 for r in results if r['source'] == 'morphological_search')
partial_count = sum(1 for r in results if r['source'] == 'partial_search')
fallback_count = sum(1 for r in results if r['source'] == 'fallback')

print(f"🎯 Улучшенная LLM: {llm_count}/{len(results)} ({llm_count/len(results)*100:.1f}%)")
print(f"🔤 Морфологический поиск: {morphological_count}/{len(results)} ({morphological_count/len(results)*100:.1f}%)")
print(f"🔍 Частичный поиск: {partial_count}/{len(results)} ({partial_count/len(results)*100:.1f}%)")
print(f"❌ Fallback: {fallback_count}/{len(results)} ({fallback_count/len(results)*100:.1f}%)")

avg_time = sum(r['time'] for r in results) / len(results)
print(f"⏱️ Среднее время: {avg_time:.2f}с")

# Проверяем качество ответов
good_answers = sum(1 for r in results if r['confidence'] > 0.8)
print(f"✅ Качественных ответов: {good_answers}/{len(results)} ({good_answers/len(results)*100:.1f}%)")

# Анализ по источникам
sources = {}
for result in results:
    source = result['source']
    if source not in sources:
        sources[source] = {'total': 0, 'good': 0}
    sources[source]['total'] += 1
    if result['confidence'] > 0.8:
        sources[source]['good'] += 1

print(f"\n📈 АНАЛИЗ ПО ИСТОЧНИКАМ:")
print("=" * 40)
for source, stats in sources.items():
    accuracy = stats['good'] / stats['total'] * 100 if stats['total'] > 0 else 0
    print(f"{source}: {stats['good']}/{stats['total']} ({accuracy:.1f}%)")

print(f"\n🎯 ТЕСТ УЛУЧШЕННОЙ СИСТЕМЫ ЗАВЕРШЕН!")
print(f"Всего протестировано: {len(test_questions)} вопросов")

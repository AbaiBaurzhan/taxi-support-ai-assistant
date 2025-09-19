#!/usr/bin/env python3
"""
🧪 УПРОЩЕННЫЙ ТЕСТ ПО ВСЕМ ВОПРОСАМ
Быстрый тест всех вопросов из базы знаний
"""

import json
import time
from datetime import datetime

def test_all_questions():
    """Тестирует все вопросы из базы знаний"""
    print("🧪 ТЕСТ ПО ВСЕМ ВОПРОСАМ ИЗ БАЗЫ ЗНАНИЙ")
    print("="*50)
    
    # Импортируем поисковую систему
    try:
        from enhanced_search_client import get_enhanced_answer
        print("✅ Используется enhanced_search_client")
    except ImportError:
        print("❌ enhanced_search_client не найден")
        return
    
    # Загружаем базу знаний
    try:
        with open('BZ.txt', 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
        print(f"✅ База знаний загружена: {len(knowledge_base)} записей")
    except Exception as e:
        print(f"❌ Ошибка загрузки базы: {e}")
        return
    
    # Собираем все вопросы
    all_questions = []
    categories = {}
    
    for idx, item in enumerate(knowledge_base):
        # Определяем категорию
        keywords = item.get('keywords', [])
        if any(kw in ['наценка', 'коэффициент', 'доплата'] for kw in keywords):
            category = 'НАЦЕНКА'
        elif any(kw in ['доставка', 'курьер', 'посылка'] for kw in keywords):
            category = 'ДОСТАВКА'
        elif any(kw in ['баланс', 'счет', 'пополнить'] for kw in keywords):
            category = 'БАЛАНС'
        elif any(kw in ['приложение', 'обновление', 'работать'] for kw in keywords):
            category = 'ПРИЛОЖЕНИЕ'
        elif any(kw in ['тариф', 'комфорт', 'класс'] for kw in keywords):
            category = 'ТАРИФ'
        elif any(kw in ['моточасы', 'время', 'минуты'] for kw in keywords):
            category = 'МОТОЧАСЫ'
        else:
            category = 'ОБЩИЕ'
        
        if category not in categories:
            categories[category] = {'total': 0, 'successful': 0}
        
        # Добавляем все вариации вопросов
        for variation in item.get('question_variations', []):
            all_questions.append({
                'question': variation,
                'category': category,
                'item_id': idx + 1
            })
            categories[category]['total'] += 1
        
        # Добавляем вопросы по ключевым словам
        for keyword in item.get('keywords', []):
            all_questions.append({
                'question': f"Что такое {keyword}?",
                'category': category,
                'item_id': idx + 1
            })
            categories[category]['total'] += 1
    
    print(f"📝 Всего вопросов для тестирования: {len(all_questions)}")
    print(f"📊 Категорий: {len(categories)}")
    
    # Запускаем тесты
    successful_tests = 0
    failed_tests = 0
    response_times = []
    
    print(f"\n🔍 Запуск тестов...")
    
    for i, test_case in enumerate(all_questions):
        question = test_case['question']
        category = test_case['category']
        
        # Показываем прогресс каждые 10 вопросов
        if (i + 1) % 10 == 0:
            print(f"   Прогресс: {i+1}/{len(all_questions)} ({((i+1)/len(all_questions)*100):.1f}%)")
        
        start_time = time.time()
        
        try:
            # Получаем ответ
            answer = get_enhanced_answer(question)
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            # Проверяем успешность
            if answer != "Нужна уточняющая информация":
                successful_tests += 1
                categories[category]['successful'] += 1
            else:
                failed_tests += 1
            
        except Exception as e:
            print(f"❌ Ошибка в тесте {i+1}: {e}")
            failed_tests += 1
    
    # Выводим результаты
    print(f"\n" + "="*50)
    print(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print(f"="*50)
    
    print(f"\n🎯 ОБЩИЕ МЕТРИКИ:")
    print(f"   Всего тестов: {len(all_questions)}")
    print(f"   Успешных: {successful_tests}")
    print(f"   Неудачных: {failed_tests}")
    print(f"   Успешность: {(successful_tests/len(all_questions)*100):.1f}%")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        print(f"\n⏱️ ПРОИЗВОДИТЕЛЬНОСТЬ:")
        print(f"   Среднее время ответа: {avg_time:.3f}s")
        print(f"   Минимальное время: {min_time:.3f}s")
        print(f"   Максимальное время: {max_time:.3f}s")
    
    print(f"\n📈 РЕЗУЛЬТАТЫ ПО КАТЕГОРИЯМ:")
    for category, metrics in categories.items():
        if metrics['total'] > 0:
            success_rate = (metrics['successful'] / metrics['total']) * 100
            status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
            print(f"   {status} {category}: {success_rate:.1f}% ({metrics['successful']}/{metrics['total']})")
    
    # Сохраняем результаты
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(all_questions),
        'successful_tests': successful_tests,
        'failed_tests': failed_tests,
        'success_rate': successful_tests / len(all_questions) if all_questions else 0,
        'categories': categories,
        'avg_response_time': sum(response_times) / len(response_times) if response_times else 0
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"all_questions_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: {filename}")
    print(f"\n🎉 ТЕСТ ЗАВЕРШЕН!")

if __name__ == "__main__":
    test_all_questions()

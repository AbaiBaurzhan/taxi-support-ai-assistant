#!/usr/bin/env python3
"""
🧪 КОМПЛЕКСНЫЙ ТЕСТ ИИ МОДЕЛИ APARU
Тестирование всех возможных вопросов и сценариев
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

# Тестовые вопросы
TEST_QUESTIONS = [
    # Основные вопросы
    {"question": "Что такое наценка?", "expected": "наценка", "category": "основной"},
    {"question": "Как заказать доставку?", "expected": "доставка", "category": "основной"},
    {"question": "Как пополнить баланс?", "expected": "баланс", "category": "основной"},
    {"question": "Приложение не работает", "expected": "приложение", "category": "основной"},
    
    # Синонимы и перефразы
    {"question": "Почему так дорого?", "expected": "наценка", "category": "синоним"},
    {"question": "Откуда доплата?", "expected": "наценка", "category": "синоним"},
    {"question": "Как отправить посылку?", "expected": "доставка", "category": "синоним"},
    {"question": "Нужен курьер", "expected": "доставка", "category": "синоним"},
    {"question": "Пополнить счет", "expected": "баланс", "category": "синоним"},
    {"question": "Платеж не проходит", "expected": "баланс", "category": "синоним"},
    {"question": "Программа глючит", "expected": "приложение", "category": "синоним"},
    {"question": "Софт не запускается", "expected": "приложение", "category": "синоним"},
    
    # Разговорные варианты
    {"question": "А что за наценка такая?", "expected": "наценка", "category": "разговорный"},
    {"question": "Можно ли заказать доставку?", "expected": "доставка", "category": "разговорный"},
    {"question": "Как бы пополнить баланс?", "expected": "баланс", "category": "разговорный"},
    {"question": "У меня приложение виснет", "expected": "приложение", "category": "разговорный"},
    
    # Опечатки
    {"question": "Что такое наценкa?", "expected": "наценка", "category": "опечатка"},
    {"question": "Как заказать доставкy?", "expected": "доставка", "category": "опечатка"},
    {"question": "Как пополнить балaнс?", "expected": "баланс", "category": "опечатка"},
    {"question": "Приложениe не работает", "expected": "приложение", "category": "опечатка"},
    
    # Смешанные вопросы
    {"question": "Наценка и доставка", "expected": "наценка", "category": "смешанный"},
    {"question": "Баланс и приложение", "expected": "баланс", "category": "смешанный"},
    
    # Неизвестные вопросы
    {"question": "Как вызвать такси?", "expected": "fallback", "category": "неизвестный"},
    {"question": "Сколько стоит поездка?", "expected": "fallback", "category": "неизвестный"},
    {"question": "Где мой водитель?", "expected": "fallback", "category": "неизвестный"},
]

def test_local_system():
    """Тестирует локальную систему"""
    print("🧪 ТЕСТИРОВАНИЕ ЛОКАЛЬНОЙ СИСТЕМЫ")
    print("=" * 50)
    
    from main import SIMPLE_ANSWERS
    
    results = []
    correct = 0
    total = len(TEST_QUESTIONS)
    
    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        question = test_case["question"]
        expected = test_case["expected"]
        category = test_case["category"]
        
        # Простой поиск (как в main.py)
        text = question.lower()
        found_answer = None
        found_keyword = None
        
        for keyword, answer in SIMPLE_ANSWERS.items():
            if keyword in text:
                found_answer = answer
                found_keyword = keyword
                break
        
        if found_keyword:
            result = "✅ CORRECT" if found_keyword == expected else "❌ WRONG"
            if found_keyword == expected:
                correct += 1
        else:
            result = "✅ CORRECT" if expected == "fallback" else "❌ WRONG"
            if expected == "fallback":
                correct += 1
            found_keyword = "fallback"
            found_answer = "Извините, не могу найти ответ. Обратитесь в службу поддержки."
        
        print(f"{i:2d}. {result} | {category:12s} | {question:30s} | {found_keyword:10s}")
        
        results.append({
            "question": question,
            "expected": expected,
            "actual": found_keyword,
            "category": category,
            "correct": found_keyword == expected,
            "answer": found_answer[:50] + "..." if len(found_answer) > 50 else found_answer
        })
    
    accuracy = (correct / total) * 100
    print("=" * 50)
    print(f"📊 РЕЗУЛЬТАТЫ ЛОКАЛЬНОГО ТЕСТИРОВАНИЯ:")
    print(f"   ✅ Правильных ответов: {correct}/{total}")
    print(f"   📈 Точность: {accuracy:.1f}%")
    
    return results, accuracy

def test_api_system(base_url="http://localhost:8000"):
    """Тестирует API систему"""
    print(f"\n🌐 ТЕСТИРОВАНИЕ API СИСТЕМЫ ({base_url})")
    print("=" * 50)
    
    results = []
    correct = 0
    total = len(TEST_QUESTIONS)
    
    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        question = test_case["question"]
        expected = test_case["expected"]
        category = test_case["category"]
        
        try:
            # Отправляем запрос к API
            response = requests.post(
                f"{base_url}/chat",
                json={
                    "text": question,
                    "user_id": "test_user",
                    "locale": "ru"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                actual_intent = data.get("intent", "unknown")
                actual_source = data.get("source", "unknown")
                actual_response = data.get("response", "")
                
                # Определяем найденный ключевое слово
                if actual_source == "simple":
                    found_keyword = actual_intent
                else:
                    found_keyword = "fallback"
                
                result = "✅ CORRECT" if found_keyword == expected else "❌ WRONG"
                if found_keyword == expected:
                    correct += 1
                
                print(f"{i:2d}. {result} | {category:12s} | {question:30s} | {found_keyword:10s}")
                
                results.append({
                    "question": question,
                    "expected": expected,
                    "actual": found_keyword,
                    "category": category,
                    "correct": found_keyword == expected,
                    "response": actual_response[:50] + "..." if len(actual_response) > 50 else actual_response,
                    "api_response": data
                })
            else:
                print(f"{i:2d}. ❌ ERROR | {category:12s} | {question:30s} | HTTP {response.status_code}")
                results.append({
                    "question": question,
                    "expected": expected,
                    "actual": "error",
                    "category": category,
                    "correct": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"{i:2d}. ❌ ERROR | {category:12s} | {question:30s} | {str(e)[:20]}")
            results.append({
                "question": question,
                "expected": expected,
                "actual": "error",
                "category": category,
                "correct": False,
                "error": str(e)
            })
    
    accuracy = (correct / total) * 100
    print("=" * 50)
    print(f"📊 РЕЗУЛЬТАТЫ API ТЕСТИРОВАНИЯ:")
    print(f"   ✅ Правильных ответов: {correct}/{total}")
    print(f"   📈 Точность: {accuracy:.1f}%")
    
    return results, accuracy

def analyze_results(local_results, api_results):
    """Анализирует результаты тестирования"""
    print("\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("=" * 50)
    
    # Статистика по категориям
    categories = {}
    for result in local_results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "correct": 0}
        categories[cat]["total"] += 1
        if result["correct"]:
            categories[cat]["correct"] += 1
    
    print("📈 ТОЧНОСТЬ ПО КАТЕГОРИЯМ:")
    for cat, stats in categories.items():
        accuracy = (stats["correct"] / stats["total"]) * 100
        print(f"   {cat:12s}: {stats['correct']:2d}/{stats['total']:2d} ({accuracy:5.1f}%)")
    
    # Проблемные вопросы
    print("\n❌ ПРОБЛЕМНЫЕ ВОПРОСЫ:")
    for result in local_results:
        if not result["correct"]:
            print(f"   ❌ {result['question']:30s} | Ожидалось: {result['expected']:10s} | Получено: {result['actual']:10s}")

def save_results(local_results, api_results, local_accuracy, api_accuracy):
    """Сохраняет результаты в файл"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    
    data = {
        "timestamp": timestamp,
        "local_results": {
            "accuracy": local_accuracy,
            "total_tests": len(local_results),
            "results": local_results
        },
        "api_results": {
            "accuracy": api_accuracy,
            "total_tests": len(api_results),
            "results": api_results
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в {filename}")

if __name__ == "__main__":
    print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ ИИ МОДЕЛИ APARU")
    print("=" * 60)
    
    # Тестируем локальную систему
    local_results, local_accuracy = test_local_system()
    
    # Тестируем API систему (если доступна)
    try:
        api_results, api_accuracy = test_api_system()
    except Exception as e:
        print(f"\n⚠️ API тестирование пропущено: {e}")
        api_results, api_accuracy = [], 0
    
    # Анализируем результаты
    analyze_results(local_results, api_results)
    
    # Сохраняем результаты
    save_results(local_results, api_results, local_accuracy, api_accuracy)
    
    print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")

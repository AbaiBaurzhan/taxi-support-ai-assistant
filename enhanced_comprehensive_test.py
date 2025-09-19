#!/usr/bin/env python3
"""
🧪 КОМПЛЕКСНЫЙ ТЕСТ УЛУЧШЕННОЙ ИИ МОДЕЛИ APARU
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
    {"question": "Как вызвать такси?", "expected": "unknown", "category": "неизвестный"},
    {"question": "Сколько стоит поездка?", "expected": "unknown", "category": "неизвестный"},
    {"question": "Где мой водитель?", "expected": "unknown", "category": "неизвестный"},
]

def test_enhanced_system():
    """Тестирует улучшенную систему"""
    print("🧪 ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ СИСТЕМЫ")
    print("=" * 50)
    
    from main import ai_model
    
    results = []
    correct = 0
    total = len(TEST_QUESTIONS)
    
    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        question = test_case["question"]
        expected = test_case["expected"]
        category = test_case["category"]
        
        # Используем улучшенную модель
        result = ai_model.find_best_match(question)
        actual_category = result["category"]
        confidence = result["confidence"]
        source = result["source"]
        
        # Определяем правильность ответа
        if expected == "unknown":
            is_correct = actual_category == "unknown"
        else:
            is_correct = actual_category == expected
        
        if is_correct:
            correct += 1
            status = "✅ CORRECT"
        else:
            status = "❌ WRONG"
        
        print(f"{i:2d}. {status} | {category:12s} | {question:30s} | {actual_category:10s} ({confidence:.2f}) [{source}]")
        
        results.append({
            "question": question,
            "expected": expected,
            "actual": actual_category,
            "category": category,
            "correct": is_correct,
            "confidence": confidence,
            "source": source,
            "answer": result["answer"][:50] + "..." if len(result["answer"]) > 50 else result["answer"]
        })
    
    accuracy = (correct / total) * 100
    print("=" * 50)
    print(f"📊 РЕЗУЛЬТАТЫ УЛУЧШЕННОГО ТЕСТИРОВАНИЯ:")
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
                actual_confidence = data.get("confidence", 0.0)
                actual_source = data.get("source", "unknown")
                actual_response = data.get("response", "")
                
                # Определяем правильность ответа
                if expected == "unknown":
                    is_correct = actual_intent == "unknown"
                else:
                    is_correct = actual_intent == expected
                
                if is_correct:
                    correct += 1
                    status = "✅ CORRECT"
                else:
                    status = "❌ WRONG"
                
                print(f"{i:2d}. {status} | {category:12s} | {question:30s} | {actual_intent:10s} ({actual_confidence:.2f}) [{actual_source}]")
                
                results.append({
                    "question": question,
                    "expected": expected,
                    "actual": actual_intent,
                    "category": category,
                    "correct": is_correct,
                    "confidence": actual_confidence,
                    "source": actual_source,
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
            categories[cat] = {"total": 0, "correct": 0, "avg_confidence": 0}
        categories[cat]["total"] += 1
        if result["correct"]:
            categories[cat]["correct"] += 1
        categories[cat]["avg_confidence"] += result["confidence"]
    
    print("📈 ТОЧНОСТЬ ПО КАТЕГОРИЯМ:")
    for cat, stats in categories.items():
        accuracy = (stats["correct"] / stats["total"]) * 100
        avg_conf = stats["avg_confidence"] / stats["total"]
        print(f"   {cat:12s}: {stats['correct']:2d}/{stats['total']:2d} ({accuracy:5.1f}%) | Средняя уверенность: {avg_conf:.2f}")
    
    # Статистика по источникам
    sources = {}
    for result in local_results:
        source = result["source"]
        if source not in sources:
            sources[source] = {"total": 0, "correct": 0}
        sources[source]["total"] += 1
        if result["correct"]:
            sources[source]["correct"] += 1
    
    print("\n🔍 ЭФФЕКТИВНОСТЬ ПО ИСТОЧНИКАМ:")
    for source, stats in sources.items():
        accuracy = (stats["correct"] / stats["total"]) * 100
        print(f"   {source:12s}: {stats['correct']:2d}/{stats['total']:2d} ({accuracy:5.1f}%)")
    
    # Проблемные вопросы
    print("\n❌ ПРОБЛЕМНЫЕ ВОПРОСЫ:")
    for result in local_results:
        if not result["correct"]:
            print(f"   ❌ {result['question']:30s} | Ожидалось: {result['expected']:10s} | Получено: {result['actual']:10s} | Уверенность: {result['confidence']:.2f}")

def save_results(local_results, api_results, local_accuracy, api_accuracy):
    """Сохраняет результаты в файл"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"enhanced_test_results_{timestamp}.json"
    
    data = {
        "timestamp": timestamp,
        "model_version": "3.0.0",
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
    print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ УЛУЧШЕННОЙ ИИ МОДЕЛИ APARU")
    print("=" * 70)
    
    # Тестируем улучшенную систему
    local_results, local_accuracy = test_enhanced_system()
    
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
    
    print("\n🎉 ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ МОДЕЛИ ЗАВЕРШЕНО!")

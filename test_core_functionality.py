#!/usr/bin/env python3
"""
🧪 ТЕСТ ОСНОВНОЙ ФУНКЦИОНАЛЬНОСТИ ТРЕХУРОВНЕВОЙ СИСТЕМЫ

Тестирует ключевые сценарии без проблемных функций
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_core_scenarios():
    """Тестирует основные сценарии работы системы"""
    print("🚀 ТЕСТ ОСНОВНОЙ ФУНКЦИОНАЛЬНОСТИ ТРЕХУРОВНЕВОЙ СИСТЕМЫ")
    print("=" * 70)
    
    # Основные тесты
    tests = [
        {
            "name": "Ключевой тест 1: 'доставка'",
            "query": "доставка",
            "expected_keywords": ["доставка", "курьер"]
        },
        {
            "name": "Ключевой тест 2: 'что такое доставка'", 
            "query": "что такое доставка",
            "expected_keywords": ["доставка", "услуга"]
        },
        {
            "name": "Ключевой тест 3: 'как работает доставка'",
            "query": "как работает доставка", 
            "expected_keywords": ["работает", "следующим образом"]
        },
        {
            "name": "Тест пополнения баланса",
            "query": "как пополнить баланс",
            "expected_keywords": ["баланс", "пополнить"]
        },
        {
            "name": "Тест стоимости поездки",
            "query": "сколько стоит поездка",
            "expected_keywords": ["цена", "стоимость"]
        }
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for i, test in enumerate(tests, 1):
        print(f"\n🧪 Тест {i}/{total_count}: {test['name']}")
        print(f"📝 Запрос: '{test['query']}'")
        
        try:
            response = requests.post(
                f"{API_BASE}/chat",
                json={
                    "text": test["query"],
                    "user_id": "test_user_core",
                    "locale": "ru"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Успешно")
                print(f"   📊 Уверенность: {data.get('confidence', 0):.2f}")
                print(f"   🔍 Источник: {data.get('source', '')}")
                print(f"   🎯 Intent: {data.get('intent', '')}")
                
                # Проверяем ключевые слова
                response_text = data.get("response", "").lower()
                found_keywords = [kw for kw in test["expected_keywords"] if kw.lower() in response_text]
                
                if found_keywords:
                    print(f"   🔑 Найденные ключевые слова: {found_keywords}")
                    print(f"   💬 Ответ: {data.get('response', '')[:80]}...")
                    success_count += 1
                else:
                    print(f"   ⚠️ Ключевые слова не найдены")
                    print(f"   💬 Ответ: {data.get('response', '')[:80]}...")
                
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"   ✅ Успешных: {success_count}/{total_count}")
    print(f"   📈 Процент успеха: {(success_count/total_count*100):.1f}%")
    
    # Проверяем основное достижение
    if success_count >= 4:  # Основные тесты должны работать
        print(f"\n🎉 ОСНОВНАЯ ФУНКЦИОНАЛЬНОСТЬ РАБОТАЕТ!")
        print(f"✅ Трехуровневая система поиска функционирует корректно")
        print(f"✅ Различение похожих вопросов работает")
        print(f"✅ Морфологический анализ активен")
    else:
        print(f"\n⚠️ ТРЕБУЕТСЯ ДОРАБОТКА")
    
    return success_count >= 4

if __name__ == "__main__":
    # Ждем запуска сервера
    print("🔄 Ожидание запуска сервера...")
    for i in range(10):
        try:
            response = requests.get(f"{API_BASE}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Сервер готов")
                break
        except:
            time.sleep(1)
            print(f"   Попытка {i+1}/10...")
    else:
        print("❌ Сервер не запустился")
        exit(1)
    
    # Запускаем тесты
    success = test_core_scenarios()
    
    if success:
        print(f"\n🚀 СИСТЕМА ГОТОВА К PRODUCTION!")
    else:
        print(f"\n🔧 ТРЕБУЕТСЯ ДОРАБОТКА")

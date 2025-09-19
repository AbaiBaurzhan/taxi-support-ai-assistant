#!/usr/bin/env python3
"""
⚡ БЫСТРЫЙ ТЕСТ LLM МОДЕЛИ APARU
Тестирует основные вопросы
"""

import requests
import json
import time

def test_llm_model():
    """Быстрый тест LLM модели"""
    print("⚡ БЫСТРЫЙ ТЕСТ LLM МОДЕЛИ")
    print("=" * 40)
    
    # Тестовые вопросы
    test_questions = [
        "Что такое наценка?",
        "Как заказать доставку?", 
        "Как пополнить баланс?",
        "Приложение не работает",
        "наценки"
    ]
    
    local_server_url = "http://172.20.10.5:8001"
    railway_url = "https://taxi-support-ai-assistant-production.up.railway.app"
    
    print(f"\n🏠 Тестирую локальный сервер: {local_server_url}")
    print(f"🌐 Тестирую Railway сервер: {railway_url}")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Вопрос {i}: {question}")
        
        # Тест локального сервера
        try:
            start_time = time.time()
            response = requests.post(
                f"{local_server_url}/chat",
                json={"text": question, "user_id": f"test_{i}", "locale": "ru"},
                timeout=60
            )
            local_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"🏠 Локальный: ✅ {data.get('source', 'unknown')} | {local_time:.1f}с")
                print(f"   Ответ: {data.get('response', '')[:50]}...")
            else:
                print(f"🏠 Локальный: ❌ Ошибка {response.status_code}")
                
        except Exception as e:
            print(f"🏠 Локальный: ❌ {str(e)[:50]}...")
        
        # Тест Railway сервера
        try:
            start_time = time.time()
            response = requests.post(
                f"{railway_url}/chat",
                json={"text": question, "user_id": f"test_{i}", "locale": "ru"},
                timeout=30
            )
            railway_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"🌐 Railway: ✅ {data.get('source', 'unknown')} | {railway_time:.1f}с")
                print(f"   Ответ: {data.get('response', '')[:50]}...")
            else:
                print(f"🌐 Railway: ❌ Ошибка {response.status_code}")
                
        except Exception as e:
            print(f"🌐 Railway: ❌ {str(e)[:50]}...")
    
    print(f"\n🎯 БЫСТРЫЙ ТЕСТ ЗАВЕРШЕН!")

if __name__ == "__main__":
    test_llm_model()

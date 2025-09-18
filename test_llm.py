#!/usr/bin/env python3
"""
🧪 APARU LLM Test Script
Быстрое тестирование LLM с ngrok
"""

import subprocess
import time
import requests
import json
import os

def test_llm():
    print("🧪 Тестирование LLM для APARU")
    print("=" * 50)
    
    # Проверяем Ollama
    print("🔍 Проверяю Ollama...")
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama установлен")
        else:
            print("❌ Ollama не найден")
            return
    except:
        print("❌ Ollama не установлен")
        return
    
    # Запускаем Ollama
    print("🚀 Запускаю Ollama...")
    ollama_process = subprocess.Popen(["ollama", "serve"])
    time.sleep(3)
    
    # Проверяем доступность
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama запущен")
        else:
            print("❌ Ollama не отвечает")
            return
    except:
        print("❌ Ollama недоступен")
        return
    
    # Запускаем ngrok
    print("🌐 Запускаю ngrok...")
    ngrok_process = subprocess.Popen(["ngrok", "http", "11434"])
    time.sleep(3)
    
    # Получаем URL туннеля
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get("tunnels", [])
            if tunnels:
                tunnel_url = tunnels[0]["public_url"]
                print(f"✅ Туннель создан: {tunnel_url}")
            else:
                print("❌ Туннель не создан")
                return
        else:
            print("❌ Не удалось получить URL туннеля")
            return
    except:
        print("❌ Ошибка получения URL туннеля")
        return
    
    # Тестируем LLM
    print("🧪 Тестирую LLM...")
    
    test_cases = [
        {
            "name": "Простой привет",
            "prompt": "Привет! Как дела?",
            "model": "llama2:7b"
        },
        {
            "name": "Вопрос о такси",
            "prompt": "Где мой водитель?",
            "model": "llama2:7b"
        },
        {
            "name": "Цена поездки",
            "prompt": "Как считается цена поездки?",
            "model": "llama2:7b"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Тест: {test_case['name']}")
        
        payload = {
            "model": test_case["model"],
            "prompt": test_case["prompt"],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 100
            }
        }
        
        try:
            response = requests.post(
                f"{tunnel_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "")
                print(f"✅ Ответ: {answer[:100]}...")
            else:
                print(f"❌ Ошибка: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    # Тестируем APARU API
    print("\n🎯 Тестирую APARU API...")
    
    aparu_tests = [
        {
            "text": "Где водитель?",
            "user_id": "test123",
            "locale": "RU"
        },
        {
            "text": "Пришлите чек",
            "user_id": "test123", 
            "locale": "RU"
        },
        {
            "text": "Как считается цена?",
            "user_id": "test123",
            "locale": "RU"
        }
    ]
    
    for test in aparu_tests:
        print(f"\n📝 APARU тест: {test['text']}")
        
        try:
            # Тестируем локально
            response = requests.post(
                "http://localhost:8000/chat",
                json=test,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Ответ: {result['response'][:100]}...")
                print(f"   Intent: {result['intent']}, Source: {result['source']}")
            else:
                print(f"❌ Ошибка: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    # Показываем конфигурацию для Railway
    print(f"\n⚙️ Конфигурация для Railway:")
    print(f"LLM_URL={tunnel_url}")
    print(f"LLM_MODEL=llama2:7b")
    print(f"LLM_ENABLED=true")
    
    print(f"\n🎉 Тестирование завершено!")
    print(f"🌐 Туннель: {tunnel_url}")
    print(f"⏹️ Нажмите Ctrl+C для остановки")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Останавливаю...")
        ollama_process.terminate()
        ngrok_process.terminate()
        print("✅ Остановлено")

if __name__ == "__main__":
    test_llm()

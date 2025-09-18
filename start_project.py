#!/usr/bin/env python3
"""
🚀 APARU Taxi Support AI Assistant - Project Launcher
Запускает весь проект: API сервер + Telegram Bot + WebApp
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🚗 APARU Taxi Support AI Assistant")
    print("=" * 60)
    print("📁 Проект: ИИ-ассистент службы поддержки такси")
    print("🌐 URL: https://taxi-support-ai-assistant-production.up.railway.app")
    print("📱 Bot: @Aparu_support_bot")
    print("=" * 60)

def check_requirements():
    """Проверяет установленные зависимости"""
    print("🔍 Проверяю зависимости...")
    
    try:
        import fastapi
        import uvicorn
        import aiogram
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("📦 Установите зависимости: pip install -r requirements.txt")
        return False

def start_api_server():
    """Запускает FastAPI сервер"""
    print("🚀 Запускаю API сервер...")
    
    try:
        # Запуск в фоновом режиме
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ API сервер запущен на http://localhost:8000")
        return process
    except Exception as e:
        print(f"❌ Ошибка запуска API: {e}")
        return None

def start_telegram_bot():
    """Запускает Telegram Bot"""
    print("🤖 Запускаю Telegram Bot...")
    
    # Проверяем токен
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("⚠️  BOT_TOKEN не настроен!")
        print("📝 Установите токен: export BOT_TOKEN='ваш_токен'")
        return None
    
    try:
        process = subprocess.Popen([
            sys.executable, "bot.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Telegram Bot запущен")
        return process
    except Exception as e:
        print(f"❌ Ошибка запуска Bot: {e}")
        return None

def open_webapp():
    """Открывает WebApp в браузере"""
    print("🌐 Открываю WebApp...")
    
    webapp_url = "http://localhost:8000/webapp"
    try:
        webbrowser.open(webapp_url)
        print(f"✅ WebApp открыт: {webapp_url}")
    except Exception as e:
        print(f"❌ Ошибка открытия WebApp: {e}")

def show_project_info():
    """Показывает информацию о проекте"""
    print("\n📋 Информация о проекте:")
    print("=" * 40)
    print("📁 Структура:")
    print("  ├── main.py          # FastAPI сервер")
    print("  ├── bot.py            # Telegram Bot")
    print("  ├── webapp.html       # WebApp интерфейс")
    print("  ├── llm_client.py     # LLM клиент")
    print("  ├── kb.json           # База знаний")
    print("  ├── fixtures.json     # Моковые данные")
    print("  └── requirements.txt  # Зависимости")
    
    print("\n🔗 Ссылки:")
    print("  🌐 WebApp: http://localhost:8000/webapp")
    print("  📡 API: http://localhost:8000/chat")
    print("  ❤️  Health: http://localhost:8000/health")
    print("  📱 Bot: @Aparu_support_bot")
    
    print("\n⚙️  Команды:")
    print("  🚀 Запуск API: python main.py")
    print("  🤖 Запуск Bot: python bot.py")
    print("  🧪 Тест API: python test_api.py")

def main():
    """Основная функция"""
    print_banner()
    
    # Проверяем зависимости
    if not check_requirements():
        return
    
    print("\n🎯 Выберите действие:")
    print("1. 🚀 Запустить весь проект (API + Bot)")
    print("2. 📡 Только API сервер")
    print("3. 🤖 Только Telegram Bot")
    print("4. 🌐 Открыть WebApp")
    print("5. 📋 Показать информацию")
    print("6. 🧪 Тестировать API")
    print("0. ❌ Выход")
    
    choice = input("\n👉 Введите номер (0-6): ").strip()
    
    processes = []
    
    if choice == "1":
        # Запуск всего проекта
        api_process = start_api_server()
        if api_process:
            processes.append(api_process)
            time.sleep(2)  # Ждем запуска API
        
        bot_process = start_telegram_bot()
        if bot_process:
            processes.append(bot_process)
        
        if processes:
            print("\n✅ Проект запущен!")
            print("🌐 WebApp: http://localhost:8000/webapp")
            print("📱 Bot: @Aparu_support_bot")
            print("\n⏹️  Нажмите Ctrl+C для остановки")
            
            try:
                # Ждем завершения процессов
                for process in processes:
                    process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Останавливаю процессы...")
                for process in processes:
                    process.terminate()
    
    elif choice == "2":
        # Только API
        api_process = start_api_server()
        if api_process:
            print("\n⏹️  Нажмите Ctrl+C для остановки")
            try:
                api_process.wait()
            except KeyboardInterrupt:
                api_process.terminate()
    
    elif choice == "3":
        # Только Bot
        bot_process = start_telegram_bot()
        if bot_process:
            print("\n⏹️  Нажмите Ctrl+C для остановки")
            try:
                bot_process.wait()
            except KeyboardInterrupt:
                bot_process.terminate()
    
    elif choice == "4":
        # Открыть WebApp
        open_webapp()
    
    elif choice == "5":
        # Показать информацию
        show_project_info()
    
    elif choice == "6":
        # Тестировать API
        print("🧪 Тестирую API...")
        try:
            import requests
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ API работает!")
                print(f"📊 Ответ: {response.json()}")
            else:
                print(f"❌ API не отвечает: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка тестирования: {e}")
    
    elif choice == "0":
        print("👋 До свидания!")
    
    else:
        print("❌ Неверный выбор!")

if __name__ == "__main__":
    main()

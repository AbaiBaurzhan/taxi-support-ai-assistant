#!/usr/bin/env python3
"""
🚗 APARU Taxi Support AI Assistant - Universal Launcher
Запускает ВСЕ компоненты проекта одной командой!
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading
import signal
from pathlib import Path

class APARULauncher:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def print_banner(self):
        print("=" * 70)
        print("🚗 APARU Taxi Support AI Assistant")
        print("=" * 70)
        print("📁 Проект: ИИ-ассистент службы поддержки такси")
        print("🌐 Production: https://taxi-support-ai-assistant-production.up.railway.app")
        print("📱 Bot: @Aparu_support_bot")
        print("=" * 70)
        
    def check_files(self):
        """Проверяет наличие всех файлов проекта"""
        required_files = [
            "main.py", "bot.py", "webapp.html", 
            "llm_client.py", "kb.json", "fixtures.json",
            "requirements.txt"
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
            return False
        
        print("✅ Все файлы проекта найдены")
        return True
        
    def install_dependencies(self):
        """Устанавливает зависимости"""
        print("📦 Проверяю зависимости...")
        
        try:
            import fastapi, uvicorn, aiogram, requests, langdetect
            print("✅ Все зависимости уже установлены")
            return True
        except ImportError:
            print("📦 Устанавливаю зависимости...")
        try:
            # Пробуем разные варианты pip
            pip_commands = [
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                ["pip3", "install", "-r", "requirements.txt"],
                ["pip", "install", "-r", "requirements.txt"]
            ]
            
            for cmd in pip_commands:
                try:
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    print("✅ Зависимости установлены")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            print("❌ Не удалось установить зависимости")
            return False
        except Exception as e:
            print(f"❌ Ошибка установки: {e}")
            return False
                
    def start_api_server(self):
        """Запускает FastAPI сервер"""
        print("🚀 Запускаю API сервер...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем запуска
            time.sleep(3)
            
            if process.poll() is None:
                print("✅ API сервер запущен на http://localhost:8000")
                self.processes.append(("API Server", process))
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ API сервер не запустился: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка запуска API: {e}")
            return False
            
    def start_telegram_bot(self):
        """Запускает Telegram Bot"""
        print("🤖 Запускаю Telegram Bot...")
        
        # Проверяем токен
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
            print("⚠️  BOT_TOKEN не настроен!")
            print("📝 Установите токен: export BOT_TOKEN='ваш_токен'")
            print("🔗 Получите токен: https://t.me/BotFather")
            return False
        
        try:
            process = subprocess.Popen(
                [sys.executable, "bot.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем запуска
            time.sleep(2)
            
            if process.poll() is None:
                print("✅ Telegram Bot запущен")
                self.processes.append(("Telegram Bot", process))
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Bot не запустился: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка запуска Bot: {e}")
            return False
            
    def open_webapp(self):
        """Открывает WebApp в браузере"""
        print("🌐 Открываю WebApp...")
        
        webapp_url = "http://localhost:8000/webapp"
        try:
            webbrowser.open(webapp_url)
            print(f"✅ WebApp открыт: {webapp_url}")
            return True
        except Exception as e:
            print(f"❌ Ошибка открытия WebApp: {e}")
            return False
            
    def test_api(self):
        """Тестирует API"""
        print("🧪 Тестирую API...")
        
        try:
            import requests
            time.sleep(2)  # Ждем запуска API
            
            # Тест health
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API Health Check: OK")
                
                # Тест chat
                test_data = {
                    "text": "Где водитель?",
                    "user_id": "test123",
                    "locale": "RU"
                }
                
                response = requests.post("http://localhost:8000/chat", 
                                       json=test_data, timeout=5)
                if response.status_code == 200:
                    print("✅ API Chat: OK")
                    return True
                else:
                    print(f"❌ API Chat: {response.status_code}")
                    return False
            else:
                print(f"❌ API Health: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка тестирования: {e}")
            return False
            
    def show_status(self):
        """Показывает статус всех компонентов"""
        print("\n📊 Статус компонентов:")
        print("=" * 40)
        
        for name, process in self.processes:
            if process.poll() is None:
                print(f"✅ {name}: Запущен")
            else:
                print(f"❌ {name}: Остановлен")
                
        print("\n🔗 Ссылки:")
        print("  🌐 WebApp: http://localhost:8000/webapp")
        print("  📡 API: http://localhost:8000/chat")
        print("  ❤️  Health: http://localhost:8000/health")
        print("  📱 Bot: @Aparu_support_bot")
        
    def cleanup(self):
        """Останавливает все процессы"""
        print("\n🛑 Останавливаю все процессы...")
        
        for name, process in self.processes:
            if process.poll() is None:
                print(f"⏹️  Останавливаю {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    
        print("✅ Все процессы остановлены")
        
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        print(f"\n🛑 Получен сигнал {signum}, завершаю работу...")
        self.running = False
        self.cleanup()
        sys.exit(0)
        
    def run(self):
        """Основная функция запуска"""
        # Регистрируем обработчики сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.print_banner()
        
        # Проверяем файлы
        if not self.check_files():
            return
            
        # Устанавливаем зависимости
        if not self.install_dependencies():
            return
            
        print("\n🎯 Выберите режим запуска:")
        print("1. 🚀 Полный запуск (API + Bot + WebApp)")
        print("2. 📡 Только API сервер")
        print("3. 🤖 Только Telegram Bot")
        print("4. 🌐 Только WebApp")
        print("5. 🧪 Тест API")
        print("6. 📋 Показать информацию")
        print("0. ❌ Выход")
        
        choice = input("\n👉 Введите номер (0-6): ").strip()
        
        if choice == "1":
            # Полный запуск
            print("\n🚀 Запускаю весь проект APARU...")
            
            # Запускаем API
            if not self.start_api_server():
                return
                
            # Тестируем API
            if not self.test_api():
                print("⚠️  API не отвечает, но продолжаю...")
                
            # Запускаем Bot
            self.start_telegram_bot()
            
            # Открываем WebApp
            self.open_webapp()
            
            # Показываем статус
            self.show_status()
            
            print("\n🎉 Проект APARU запущен!")
            print("⏹️  Нажмите Ctrl+C для остановки")
            
            # Ждем завершения
            try:
                while self.running:
                    time.sleep(1)
                    # Проверяем статус процессов
                    for name, process in self.processes:
                        if process.poll() is not None:
                            print(f"⚠️  {name} остановился неожиданно")
            except KeyboardInterrupt:
                pass
                
        elif choice == "2":
            # Только API
            if self.start_api_server():
                self.test_api()
                self.show_status()
                print("\n⏹️  Нажмите Ctrl+C для остановки")
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
                    
        elif choice == "3":
            # Только Bot
            if self.start_telegram_bot():
                self.show_status()
                print("\n⏹️  Нажмите Ctrl+C для остановки")
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
                    
        elif choice == "4":
            # Только WebApp
            self.open_webapp()
            
        elif choice == "5":
            # Тест API
            if self.start_api_server():
                self.test_api()
                
        elif choice == "6":
            # Информация
            self.show_project_info()
            
        elif choice == "0":
            print("👋 До свидания!")
            
        else:
            print("❌ Неверный выбор!")
            
        # Очистка
        self.cleanup()
        
    def show_project_info(self):
        """Показывает информацию о проекте"""
        print("\n📋 Информация о проекте APARU:")
        print("=" * 50)
        print("📁 Структура:")
        print("  ├── main.py              # FastAPI сервер")
        print("  ├── bot.py               # Telegram Bot")
        print("  ├── webapp.html          # WebApp интерфейс")
        print("  ├── llm_client.py        # LLM клиент")
        print("  ├── kb.json              # База знаний FAQ")
        print("  ├── fixtures.json        # Моковые данные")
        print("  ├── requirements.txt     # Зависимости")
        print("  └── start_aparu.py       # 🚀 Этот лаунчер")
        
        print("\n🔗 Ссылки:")
        print("  🌐 WebApp: http://localhost:8000/webapp")
        print("  📡 API: http://localhost:8000/chat")
        print("  ❤️  Health: http://localhost:8000/health")
        print("  📱 Bot: @Aparu_support_bot")
        print("  🌐 Production: https://taxi-support-ai-assistant-production.up.railway.app")
        
        print("\n⚙️  Команды:")
        print("  🚀 Полный запуск: python3 start_aparu.py")
        print("  📡 Только API: python3 main.py")
        print("  🤖 Только Bot: python3 bot.py")
        print("  🧪 Тест API: curl http://localhost:8000/health")
        
        print("\n📋 Функции:")
        print("  ✅ REST API с эндпоинтом /chat")
        print("  ✅ Определение языка (RU/KZ/EN)")
        print("  ✅ Классификация запросов")
        print("  ✅ База знаний FAQ")
        print("  ✅ Моки такси-сервиса")
        print("  ✅ Telegram Bot + WebApp")
        print("  ✅ Деплой на Railway")

def main():
    """Точка входа"""
    launcher = APARULauncher()
    launcher.run()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🚀 APARU Local LLM Server
Запускает локальный LLM сервер с туннелем для доступа из интернета
"""

import os
import sys
import subprocess
import time
import requests
import threading
from pathlib import Path

class LocalLLMServer:
    def __init__(self):
        self.llm_process = None
        self.tunnel_process = None
        self.tunnel_url = None
        
    def print_banner(self):
        print("=" * 70)
        print("🤖 APARU Local LLM Server")
        print("=" * 70)
        print("📡 Запускает локальный LLM с доступом из интернета")
        print("🌐 Для использования в Railway production")
        print("=" * 70)
        
    def check_ollama(self):
        """Проверяет наличие Ollama"""
        print("🔍 Проверяю Ollama...")
        
        try:
            # Проверяем установку
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Ollama установлен")
                return True
            else:
                print("❌ Ollama не найден")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Ollama не установлен")
            return False
            
    def install_ollama(self):
        """Устанавливает Ollama"""
        print("📦 Устанавливаю Ollama...")
        
        try:
            # Скачиваем и устанавливаем Ollama
            install_script = """
            curl -fsSL https://ollama.ai/install.sh | sh
            """
            
            result = subprocess.run(install_script, shell=True, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Ollama установлен")
                return True
            else:
                print(f"❌ Ошибка установки: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
            
    def download_model(self, model_name="llama2"):
        """Загружает модель"""
        print(f"📥 Загружаю модель {model_name}...")
        
        try:
            result = subprocess.run(["ollama", "pull", model_name], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Модель {model_name} загружена")
                return True
            else:
                print(f"❌ Ошибка загрузки: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
            
    def start_ollama_server(self):
        """Запускает Ollama сервер"""
        print("🚀 Запускаю Ollama сервер...")
        
        try:
            self.llm_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем запуска
            time.sleep(3)
            
            # Проверяем доступность
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    print("✅ Ollama сервер запущен на http://localhost:11434")
                    return True
                else:
                    print("❌ Ollama сервер не отвечает")
                    return False
            except requests.exceptions.RequestException:
                print("❌ Ollama сервер недоступен")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
            return False
            
    def install_ngrok(self):
        """Устанавливает ngrok"""
        print("📦 Проверяю ngrok...")
        
        try:
            result = subprocess.run(["ngrok", "version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ ngrok установлен")
                return True
            else:
                print("❌ ngrok не найден")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ ngrok не установлен")
            return False
            
    def start_tunnel(self):
        """Запускает туннель"""
        print("🌐 Запускаю туннель...")
        
        try:
            # Запускаем ngrok туннель
            self.tunnel_process = subprocess.Popen(
                ["ngrok", "http", "11434", "--log=stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем запуска
            time.sleep(3)
            
            # Получаем URL туннеля
            try:
                response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    tunnels = data.get("tunnels", [])
                    if tunnels:
                        self.tunnel_url = tunnels[0]["public_url"]
                        print(f"✅ Туннель запущен: {self.tunnel_url}")
                        return True
                    else:
                        print("❌ Туннель не создан")
                        return False
                else:
                    print("❌ Не удалось получить URL туннеля")
                    return False
            except requests.exceptions.RequestException:
                print("❌ Ошибка получения URL туннеля")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка запуска туннеля: {e}")
            return False
            
    def test_llm(self):
        """Тестирует LLM через туннель"""
        print("🧪 Тестирую LLM...")
        
        if not self.tunnel_url:
            print("❌ Туннель не запущен")
            return False
            
        try:
            test_payload = {
                "model": "llama2",
                "prompt": "Привет! Как дела?",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 50
                }
            }
            
            response = requests.post(
                f"{self.tunnel_url}/api/generate",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "")
                print(f"✅ LLM отвечает: {answer[:50]}...")
                return True
            else:
                print(f"❌ Ошибка LLM: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка тестирования: {e}")
            return False
            
    def update_railway_config(self):
        """Обновляет конфигурацию для Railway"""
        print("⚙️ Обновляю конфигурацию...")
        
        if not self.tunnel_url:
            print("❌ Туннель не запущен")
            return False
            
        # Создаем файл конфигурации
        config_content = f"""# APARU Local LLM Configuration
LLM_URL={self.tunnel_url}
LLM_MODEL=llama2
LLM_ENABLED=true
"""
        
        try:
            with open(".env.local", "w") as f:
                f.write(config_content)
            print("✅ Конфигурация сохранена в .env.local")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False
            
    def cleanup(self):
        """Останавливает все процессы"""
        print("\n🛑 Останавливаю процессы...")
        
        if self.tunnel_process:
            self.tunnel_process.terminate()
            print("⏹️ Туннель остановлен")
            
        if self.llm_process:
            self.llm_process.terminate()
            print("⏹️ Ollama остановлен")
            
    def run(self):
        """Основная функция"""
        self.print_banner()
        
        print("\n🎯 Выберите действие:")
        print("1. 🚀 Полная настройка (Ollama + туннель)")
        print("2. 🤖 Только Ollama")
        print("3. 🌐 Только туннель")
        print("4. 🧪 Тест LLM")
        print("5. ⚙️ Обновить конфигурацию")
        print("0. ❌ Выход")
        
        choice = input("\n👉 Введите номер (0-5): ").strip()
        
        if choice == "1":
            # Полная настройка
            if not self.check_ollama():
                if not self.install_ollama():
                    return
                    
            if not self.download_model():
                return
                
            if not self.start_ollama_server():
                return
                
            if not self.install_ngrok():
                print("📝 Установите ngrok: https://ngrok.com/download")
                return
                
            if not self.start_tunnel():
                return
                
            if not self.test_llm():
                return
                
            if not self.update_railway_config():
                return
                
            print("\n🎉 Локальный LLM сервер готов!")
            print(f"🌐 URL: {self.tunnel_url}")
            print("⏹️ Нажмите Ctrl+C для остановки")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
        elif choice == "2":
            # Только Ollama
            if not self.check_ollama():
                if not self.install_ollama():
                    return
                    
            if not self.download_model():
                return
                
            if not self.start_ollama_server():
                return
                
            print("\n✅ Ollama запущен локально")
            print("🌐 Доступен на http://localhost:11434")
            
        elif choice == "3":
            # Только туннель
            if not self.start_tunnel():
                return
                
            print(f"\n✅ Туннель запущен: {self.tunnel_url}")
            
        elif choice == "4":
            # Тест
            if not self.test_llm():
                return
                
        elif choice == "5":
            # Конфигурация
            if not self.update_railway_config():
                return
                
        elif choice == "0":
            print("👋 До свидания!")
            
        else:
            print("❌ Неверный выбор!")
            
        self.cleanup()

def main():
    server = LocalLLMServer()
    server.run()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🚀 APARU Complete Training Pipeline
Полный пайплайн обучения LLM на данных APARU
"""

import subprocess
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def run_command(command, description):
    """Выполняет команду и показывает результат"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            return True
        else:
            print(f"❌ {description} - ошибка: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ошибка: {e}")
        return False

def main():
    """Полный пайплайн обучения APARU LLM"""
    print("🚀 APARU Complete Training Pipeline")
    print("=" * 60)
    
    # Проверяем наличие файла BZ.txt
    bz_file = "database_Aparu/BZ.txt"
    if not Path(bz_file).exists():
        print(f"❌ Файл {bz_file} не найден!")
        print("📁 Убедитесь, что файл находится в правильной папке")
        return
    
    print(f"✅ Найден файл: {bz_file}")
    
    # Шаг 1: Парсинг данных
    print("\n📊 Шаг 1: Парсинг данных APARU")
    if not run_command("python3 parse_aparu_bz.py", "Парсинг BZ.txt"):
        return
    
    # Шаг 2: Обучение модели
    print("\n🧠 Шаг 2: Обучение LLM модели")
    if not run_command("python3 train_aparu_llm.py", "Обучение модели APARU"):
        return
    
    # Шаг 3: Тестирование
    print("\n🧪 Шаг 3: Тестирование обученной модели")
    if not run_command("python3 aparu_enhanced_client.py", "Тестирование модели"):
        return
    
    # Шаг 4: Проверка файлов
    print("\n📁 Шаг 4: Проверка созданных файлов")
    
    files_to_check = [
        "aparu_knowledge_base.json",
        "aparu_knowledge_base.csv", 
        "aparu_knowledge_index.pkl",
        "aparu_training_prompts.json",
        "aparu_test_results.json",
        "Modelfile"
    ]
    
    for file in files_to_check:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - не найден")
    
    # Шаг 5: Инструкции по использованию
    print("\n🎯 Шаг 5: Инструкции по использованию")
    print("=" * 60)
    
    print("📋 Для интеграции с APARU:")
    print("1. Замените в main.py:")
    print("   from llm_client import llm_client")
    print("   на:")
    print("   from aparu_enhanced_client import aparu_enhanced_client")
    print()
    print("2. Замените все вызовы:")
    print("   llm_client.generate_response()")
    print("   на:")
    print("   aparu_enhanced_client.generate_response()")
    print()
    print("3. Загрузите базу знаний при запуске:")
    print("   aparu_enhanced_client.load_aparu_knowledge_base()")
    
    print("\n🧪 Для тестирования модели:")
    print("ollama run aparu-support 'Что такое наценка?'")
    print("ollama run aparu-support 'Как пополнить баланс?'")
    print("ollama run aparu-support 'Что такое моточасы?'")
    
    print("\n🌐 Для использования с туннелем:")
    print("1. Запустите Ollama: ollama serve")
    print("2. Создайте туннель: ngrok http 11434")
    print("3. Установите переменную: LLM_URL=https://your-ngrok-url.ngrok.io")
    
    print("\n📊 Статистика обучения:")
    try:
        with open("aparu_test_results.json", 'r', encoding='utf-8') as f:
            import json
            results = json.load(f)
            success_count = sum(1 for r in results if r['status'] == 'success')
            print(f"✅ Успешных тестов: {success_count}/{len(results)}")
    except:
        print("❌ Не удалось загрузить результаты тестирования")
    
    print("\n🎉 Обучение завершено!")
    print("🤖 Модель APARU готова к использованию!")

if __name__ == "__main__":
    main()

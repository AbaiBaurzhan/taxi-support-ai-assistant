#!/bin/bash

# Скрипт для запуска проекта локально

echo "🚀 Запуск демо-проекта ИИ-ассистента такси..."

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.9+"
    exit 1
fi

# Проверка pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден. Установите pip"
    exit 1
fi

# Переход в директорию backend
cd backend

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt

# Проверка Ollama (опционально)
if command -v ollama &> /dev/null; then
    echo "✅ Ollama найден"
    echo "💡 Для загрузки модели выполните: ollama pull llama2"
else
    echo "⚠️  Ollama не найден. Будет использоваться transformers"
fi

# Создание .env файла если его нет
if [ ! -f .env ]; then
    echo "📝 Создание .env файла..."
    cp env.example .env
    echo "⚠️  Отредактируйте .env файл с вашими настройками"
fi

# Запуск сервера
echo "🌐 Запуск FastAPI сервера на http://localhost:8000"
echo "📱 WebApp доступен на http://localhost:8000/webapp"
echo "📚 API документация на http://localhost:8000/docs"
echo ""
echo "Для остановки нажмите Ctrl+C"

python3 main.py

#!/bin/bash
# 🚀 APARU Taxi Support AI Assistant - Quick Start

echo "🚗 APARU Taxi Support AI Assistant"
echo "=================================="

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден!"
    exit 1
fi

# Проверяем зависимости
echo "🔍 Проверяю зависимости..."
python3 -c "import fastapi, uvicorn, aiogram" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Устанавливаю зависимости..."
    pip3 install -r requirements.txt
fi

echo "✅ Зависимости готовы!"

# Меню выбора
echo ""
echo "🎯 Выберите действие:"
echo "1. 🚀 Запустить API сервер"
echo "2. 🤖 Запустить Telegram Bot"
echo "3. 🌐 Открыть WebApp"
echo "4. 📋 Показать информацию"
echo "0. ❌ Выход"

read -p "👉 Введите номер (0-4): " choice

case $choice in
    1)
        echo "🚀 Запускаю API сервер..."
        python3 main.py
        ;;
    2)
        echo "🤖 Запускаю Telegram Bot..."
        echo "⚠️  Убедитесь что BOT_TOKEN настроен!"
        python3 bot.py
        ;;
    3)
        echo "🌐 Открываю WebApp..."
        python3 -c "import webbrowser; webbrowser.open('http://localhost:8000/webapp')"
        echo "✅ WebApp должен открыться в браузере"
        ;;
    4)
        echo "📋 Информация о проекте:"
        echo "========================"
        echo "📁 Файлы:"
        echo "  ├── main.py          # FastAPI сервер"
        echo "  ├── bot.py            # Telegram Bot"
        echo "  ├── webapp.html       # WebApp интерфейс"
        echo "  ├── llm_client.py     # LLM клиент"
        echo "  ├── kb.json           # База знаний"
        echo "  └── fixtures.json     # Моковые данные"
        echo ""
        echo "🔗 Ссылки:"
        echo "  🌐 WebApp: http://localhost:8000/webapp"
        echo "  📡 API: http://localhost:8000/chat"
        echo "  ❤️  Health: http://localhost:8000/health"
        echo "  📱 Bot: @Aparu_support_bot"
        echo ""
        echo "🌐 Production: https://taxi-support-ai-assistant-production.up.railway.app"
        ;;
    0)
        echo "👋 До свидания!"
        ;;
    *)
        echo "❌ Неверный выбор!"
        ;;
esac
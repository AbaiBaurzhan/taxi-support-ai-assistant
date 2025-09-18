#!/bin/bash
# 🚗 APARU Taxi Support AI Assistant - Quick Launcher

echo "🚗 APARU Taxi Support AI Assistant"
echo "=================================="

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден!"
    exit 1
fi

# Проверяем файлы
echo "🔍 Проверяю файлы проекта..."
missing_files=()
for file in main.py bot.py webapp.html llm_client.py kb.json fixtures.json requirements.txt; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Отсутствуют файлы: ${missing_files[*]}"
    exit 1
fi

echo "✅ Все файлы найдены"

# Проверяем зависимости
echo "📦 Проверяю зависимости..."
python3 -c "import fastapi, uvicorn, aiogram" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Устанавливаю зависимости..."
    pip3 install -r requirements.txt
fi

echo "✅ Зависимости готовы!"

# Меню
echo ""
echo "🎯 Выберите действие:"
echo "1. 🚀 Запустить ВСЕ (API + Bot + WebApp)"
echo "2. 📡 Только API сервер"
echo "3. 🤖 Только Telegram Bot"
echo "4. 🌐 Открыть WebApp"
echo "5. 🧪 Тестировать API"
echo "6. 📋 Информация о проекте"
echo "0. ❌ Выход"

read -p "👉 Введите номер (0-6): " choice

case $choice in
    1)
        echo "🚀 Запускаю ВСЕ компоненты APARU..."
        
        # Запускаем API в фоне
        echo "📡 Запускаю API сервер..."
        python3 main.py &
        API_PID=$!
        sleep 3
        
        # Проверяем API
        echo "🧪 Тестирую API..."
        sleep 2
        if curl -s http://localhost:8000/health > /dev/null; then
            echo "✅ API работает!"
        else
            echo "⚠️  API не отвечает"
        fi
        
        # Запускаем Bot в фоне
        echo "🤖 Запускаю Telegram Bot..."
        if [ -n "$BOT_TOKEN" ] && [ "$BOT_TOKEN" != "YOUR_BOT_TOKEN_HERE" ]; then
            python3 bot.py &
            BOT_PID=$!
            echo "✅ Bot запущен!"
        else
            echo "⚠️  BOT_TOKEN не настроен!"
        fi
        
        # Открываем WebApp
        echo "🌐 Открываю WebApp..."
        python3 -c "import webbrowser; webbrowser.open('http://localhost:8000/webapp')"
        
        echo ""
        echo "🎉 Проект APARU запущен!"
        echo "🌐 WebApp: http://localhost:8000/webapp"
        echo "📱 Bot: @Aparu_support_bot"
        echo "⏹️  Нажмите Ctrl+C для остановки"
        
        # Ждем завершения
        trap 'echo "🛑 Останавливаю..."; kill $API_PID $BOT_PID 2>/dev/null; exit' INT
        wait
        ;;
    2)
        echo "📡 Запускаю API сервер..."
        python3 main.py
        ;;
    3)
        echo "🤖 Запускаю Telegram Bot..."
        if [ -n "$BOT_TOKEN" ] && [ "$BOT_TOKEN" != "YOUR_BOT_TOKEN_HERE" ]; then
            python3 bot.py
        else
            echo "⚠️  Установите BOT_TOKEN: export BOT_TOKEN='ваш_токен'"
        fi
        ;;
    4)
        echo "🌐 Открываю WebApp..."
        python3 -c "import webbrowser; webbrowser.open('http://localhost:8000/webapp')"
        echo "✅ WebApp должен открыться в браузере"
        ;;
    5)
        echo "🧪 Тестирую API..."
        if curl -s http://localhost:8000/health > /dev/null; then
            echo "✅ API работает!"
            echo "📊 Тестирую /chat..."
            curl -X POST http://localhost:8000/chat \
                -H "Content-Type: application/json" \
                -d '{"text": "Где водитель?", "user_id": "test123", "locale": "RU"}' \
                2>/dev/null | head -c 200
            echo ""
        else
            echo "❌ API не отвечает. Запустите сначала: python3 main.py"
        fi
        ;;
    6)
        echo "📋 Информация о проекте APARU:"
        echo "=============================="
        echo "📁 Файлы:"
        echo "  ├── main.py              # FastAPI сервер"
        echo "  ├── bot.py               # Telegram Bot"
        echo "  ├── webapp.html          # WebApp интерфейс"
        echo "  ├── llm_client.py        # LLM клиент"
        echo "  ├── kb.json              # База знаний"
        echo "  ├── fixtures.json        # Моковые данные"
        echo "  ├── start_aparu.py       # 🚀 Python лаунчер"
        echo "  └── start_aparu.sh       # 🚀 Bash лаунчер"
        echo ""
        echo "🔗 Ссылки:"
        echo "  🌐 WebApp: http://localhost:8000/webapp"
        echo "  📡 API: http://localhost:8000/chat"
        echo "  ❤️  Health: http://localhost:8000/health"
        echo "  📱 Bot: @Aparu_support_bot"
        echo "  🌐 Production: https://taxi-support-ai-assistant-production.up.railway.app"
        echo ""
        echo "⚙️  Команды:"
        echo "  🚀 Полный запуск: ./start_aparu.sh"
        echo "  🚀 Python лаунчер: python3 start_aparu.py"
        echo "  📡 Только API: python3 main.py"
        echo "  🤖 Только Bot: python3 bot.py"
        ;;
    0)
        echo "👋 До свидания!"
        ;;
    *)
        echo "❌ Неверный выбор!"
        ;;
esac

#!/bin/bash
# 🚀 APARU LLM - Быстрый деплой на Railway

echo "🚀 APARU LLM - Деплой на Railway"
echo "================================="

# Проверяем статус git
echo "📦 Проверяем статус git..."
git status

# Проверяем туннель
echo "🌐 Проверяем туннель ngrok..."
TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data['tunnels'] else 'No tunnels')" 2>/dev/null)

if [ "$TUNNEL_URL" != "No tunnels" ]; then
    echo "✅ Туннель активен: $TUNNEL_URL"
else
    echo "❌ Туннель не активен. Запускаем ngrok..."
    ngrok http 11434 &
    sleep 5
    TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data['tunnels'] else 'No tunnels')" 2>/dev/null)
    echo "✅ Новый туннель: $TUNNEL_URL"
fi

echo ""
echo "🎯 Следующие шаги:"
echo "1. Перейдите на: https://railway.app"
echo "2. Создайте новый проект из GitHub"
echo "3. Выберите репозиторий: AbaiBaurzhan/taxi-support-ai-assistant"
echo "4. Добавьте переменные окружения:"
echo ""
echo "   LLM_URL=$TUNNEL_URL"
echo "   LLM_MODEL=aparu-support"
echo "   LLM_ENABLED=true"
echo "   BOT_TOKEN=your_telegram_bot_token_here"
echo "   PYTHON_VERSION=3.11"
echo "   PORT=8000"
echo ""
echo "5. Нажмите Deploy!"
echo ""
echo "🧪 После деплоя протестируйте:"
echo "curl https://your-app.railway.app/health"
echo ""
echo "✅ APARU готов к деплою!"

#!/bin/bash

echo "🚀 ЗАПУСК ЛОКАЛЬНОЙ AI МОДЕЛИ ДЛЯ ГИБРИДНОЙ АРХИТЕКТУРЫ"
echo "====================================================="

# Проверяем наличие Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama не установлен!"
    echo "📥 Установите Ollama: https://ollama.ai"
    exit 1
fi

echo "✅ Ollama найден"

# Проверяем наличие модели
echo "🔍 Проверяем наличие модели aparu-senior-ai..."
if ollama list | grep -q "aparu-senior-ai"; then
    echo "✅ Модель aparu-senior-ai найдена"
else
    echo "📥 Создаем модель aparu-senior-ai..."
    
    # Создаем Modelfile
    cat > aparu-senior-ai.modelfile << 'EOF'
FROM llama2:7b

SYSTEM """Ты — Senior AI Engineer и FAQ-ассистент для техподдержки такси-агрегатора APARU. 

Твоя задача — отвечать пользователям строго по базе FAQ.

Правила работы:
- Всегда ищи соответствие в базе FAQ
- Понимай разные формулировки вопросов: синонимы, перефразы, разговорные варианты, опечатки
- Ответ должен быть только из базы, без генерации новых текстов
- Если уверенность ≥ 0.6 → выдай точный ответ из базы
- Если уверенность < 0.6 → верни сообщение: «Нужна уточняющая информация» и список ближайших вопросов
- Всегда возвращай top-3 наиболее похожих вопросов с коэффициентами близости
- Поддерживай категории (тарифы, баланс, доставка, приложение и т.д.) и ключевые слова

Главная цель: ассистент должен надёжно распознавать любые вариации вопросов и возвращать корректный ответ исключительно из базы FAQ, без «галлюцинаций»."""

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER stop "Human:"
PARAMETER stop "Assistant:"
EOF
    
    # Создаем модель
    ollama create aparu-senior-ai -f aparu-senior-ai.modelfile
    echo "✅ Модель aparu-senior-ai создана"
fi

# Запускаем Ollama сервер
echo "🚀 Запускаем Ollama сервер..."
ollama serve &

# Ждем запуска сервера
echo "⏳ Ждем запуска сервера..."
sleep 5

# Проверяем доступность сервера
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama сервер запущен на http://localhost:11434"
else
    echo "❌ Ошибка запуска Ollama сервера"
    exit 1
fi

# Запускаем туннель (ngrok)
echo "🌐 Настраиваем туннель для доступа из Railway..."

# Проверяем наличие ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok не установлен!"
    echo "📥 Установите ngrok: https://ngrok.com/download"
    echo "🔑 Получите токен: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

echo "✅ ngrok найден"

# Запускаем туннель
echo "🚀 Запускаем туннель на порту 11434..."
ngrok http 11434 --log=stdout &

# Ждем запуска туннеля
echo "⏳ Ждем запуска туннеля..."
sleep 10

# Получаем URL туннеля
TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
data = json.load(sys.stdin)
for tunnel in data['tunnels']:
    if tunnel['proto'] == 'https':
        print(tunnel['public_url'])
        break
")

if [ -n "$TUNNEL_URL" ]; then
    echo "✅ Туннель запущен: $TUNNEL_URL"
    echo ""
    echo "🔧 НАСТРОЙКА RAILWAY:"
    echo "1. Зайдите в Railway Dashboard"
    echo "2. Выберите проект 'taxi-support-ai-assistant'"
    echo "3. Добавьте переменную окружения:"
    echo "   LOCAL_MODEL_URL = $TUNNEL_URL"
    echo "4. Замените main.py на hybrid_main.py"
    echo "5. Замените requirements.txt на requirements_hybrid.txt"
    echo "6. Запустите деплой"
    echo ""
    echo "🧪 ТЕСТИРОВАНИЕ:"
    echo "curl -X POST $TUNNEL_URL/api/generate \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"model\": \"aparu-senior-ai\", \"prompt\": \"Что такое наценка?\"}'"
else
    echo "❌ Ошибка получения URL туннеля"
    exit 1
fi

echo ""
echo "🎉 ЛОКАЛЬНАЯ AI МОДЕЛЬ ГОТОВА К РАБОТЕ!"
echo "📱 Не закрывайте этот терминал - модель должна работать"
echo "🔄 Для остановки нажмите Ctrl+C"

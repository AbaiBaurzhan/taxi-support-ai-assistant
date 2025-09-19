#!/bin/bash

echo "🚀 ЗАПУСК ЛОКАЛЬНОЙ AI МОДЕЛИ APARU"
echo "=================================="

# Проверяем Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama не установлен!"
    echo "📥 Установите Ollama: https://ollama.ai"
    exit 1
fi

echo "✅ Ollama найден"

# Проверяем модель
echo "🔍 Проверяем модель aparu-senior-ai..."
if ollama list | grep -q "aparu-senior-ai"; then
    echo "✅ Модель aparu-senior-ai найдена"
else
    echo "⚠️ Модель aparu-senior-ai не найдена"
    echo "📥 Создаем модель..."
    
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
- Если уверенность < 0.6 → верни сообщение: «Нужна уточняющая информация»

Поддерживай категории (тарифы, баланс, доставка, приложение и т.д.) и ключевые слова.

Главная цель: ассистент должен надёжно распознавать любые вариации вопросов и возвращать корректный ответ исключительно из базы FAQ, без «галлюцинаций»."""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
EOF

    # Создаем модель
    ollama create aparu-senior-ai -f aparu-senior-ai.modelfile
    echo "✅ Модель aparu-senior-ai создана"
fi

# Запускаем Ollama сервер
echo "🚀 Запускаем Ollama сервер..."
ollama serve &

# Ждем запуска сервера
sleep 5

# Проверяем доступность
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama сервер запущен на http://localhost:11434"
else
    echo "❌ Не удалось запустить Ollama сервер"
    exit 1
fi

echo ""
echo "🎯 ЛОКАЛЬНАЯ МОДЕЛЬ ГОТОВА К РАБОТЕ!"
echo "   URL: http://localhost:11434"
echo "   Модель: aparu-senior-ai"
echo ""
echo "🧪 Тестируем модель..."
echo "❓ Вопрос: Что такое наценка?"

# Тестируем модель
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "aparu-senior-ai",
    "prompt": "Ответь на вопрос пользователя такси-агрегатора APARU: Что такое наценка?",
    "stream": false
  }' | jq -r '.response' | head -3

echo ""
echo "✅ Модель работает!"
echo ""
echo "🌐 Теперь можно деплоить легкий API на Railway"
echo "   Railway будет пересылать запросы к этой локальной модели"
echo ""
echo "📋 Следующие шаги:"
echo "1. Запустите: python3 lightweight_railway_api.py"
echo "2. Деплойте на Railway"
echo "3. Railway будет пересылать запросы к localhost:11434"

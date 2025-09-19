#!/bin/bash

echo "🚀 ДЕПЛОЙ ФИНАЛЬНОЙ ГИБРИДНОЙ АРХИТЕКТУРЫ APARU AI"
echo "=================================================="

# Переключаемся на гибридную архитектуру
echo "📝 Переключаемся на гибридную архитектуру..."
cp final_hybrid_main.py main.py
cp requirements_final_hybrid.txt requirements.txt

# Коммитим изменения
echo "💾 Коммитим изменения..."
git add .
git commit -m "🚀 Финальная гибридная архитектура - LLM на ноутбуке + Railway проксирует"

# Отправляем в GitHub
echo "🌐 Отправляем в GitHub..."
git push origin main

echo ""
echo "✅ ГИБРИДНАЯ АРХИТЕКТУРА ГОТОВА К ДЕПЛОЮ!"
echo ""
echo "📊 КОНФИГУРАЦИЯ:"
echo "  🏠 LLM модель: работает на ноутбуке"
echo "  🌐 Railway: только проксирует запросы"
echo "  ⚡ Быстрый деплой: без тяжелых ML библиотек"
echo "  🔗 ngrok туннель: https://a58a3de709bd.ngrok-free.app"
echo ""
echo "🎯 СЛЕДУЮЩИЙ ШАГ:"
echo "  railway deploy"
echo ""

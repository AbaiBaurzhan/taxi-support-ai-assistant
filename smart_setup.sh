#!/bin/bash

echo "🧠 АВТОМАТИЧЕСКИЙ ВЫБОР ЗАВИСИМОСТЕЙ APARU AI"
echo "=============================================="

# Проверяем переменные окружения
if [ "$FORCE_FULL_ML" = "true" ]; then
    echo "🔧 Принудительно включены полные ML зависимости"
    cp requirements_full_ml.txt requirements.txt
    echo "✅ Скопирован requirements_full_ml.txt"
    echo "🚀 Установка: pip install -r requirements.txt"
    echo "⏱️ Время: 5-10 минут"
    echo "📦 Размер: ~2-3 GB"
    echo "🎯 Точность: 80%"
    exit 0
fi

if [ "$FORCE_LIGHTWEIGHT" = "true" ]; then
    echo "🔧 Принудительно включена облегченная версия"
    cp requirements_lightweight.txt requirements.txt
    echo "✅ Скопирован requirements_lightweight.txt"
    echo "⚡ Установка: pip install -r requirements.txt"
    echo "⏱️ Время: 1-2 минуты"
    echo "📦 Размер: ~100 MB"
    echo "🎯 Точность: 70%"
    exit 0
fi

# Проверяем Railway
if [ "$RAILWAY_MODE" = "true" ]; then
    echo "☁️ Railway окружение - используем облегченную версию"
    cp requirements_lightweight.txt requirements.txt
    echo "✅ Скопирован requirements_lightweight.txt"
    echo "⚡ Установка: pip install -r requirements.txt"
    echo "⏱️ Время: 1-2 минуты"
    echo "📦 Размер: ~100 MB"
    echo "🎯 Точность: 70%"
    exit 0
fi

# Проверяем доступность ML библиотек
echo "🔍 Проверяем доступность ML библиотек..."

if python3 -c "import numpy, sentence_transformers, faiss, fuzzywuzzy, nltk, pandas, sklearn" 2>/dev/null; then
    echo "🚀 Полные ML зависимости доступны - используем максимальную точность"
    cp requirements_full_ml.txt requirements.txt
    echo "✅ Скопирован requirements_full_ml.txt"
    echo "🚀 Установка: pip install -r requirements.txt"
    echo "⏱️ Время: 5-10 минут"
    echo "📦 Размер: ~2-3 GB"
    echo "🎯 Точность: 80%"
else
    echo "⚠️ Полные ML зависимости недоступны - используем облегченную версию"
    cp requirements_lightweight.txt requirements.txt
    echo "✅ Скопирован requirements_lightweight.txt"
    echo "⚡ Установка: pip install -r requirements.txt"
    echo "⏱️ Время: 1-2 минуты"
    echo "📦 Размер: ~100 MB"
    echo "🎯 Точность: 70%"
fi

echo ""
echo "🎯 Система готова к работе!"
echo ""
echo "📋 Доступные режимы:"
echo "   FORCE_FULL_ML=true     - Принудительно полные ML зависимости"
echo "   FORCE_LIGHTWEIGHT=true - Принудительно облегченная версия"
echo "   RAILWAY_MODE=true      - Режим Railway (облегченная версия)"

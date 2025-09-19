#!/bin/bash

echo "🚀 ДЕПЛОЙ ГИБРИДНОЙ АРХИТЕКТУРЫ APARU AI"
echo "========================================"

echo ""
echo "🎯 ГИБРИДНАЯ АРХИТЕКТУРА:"
echo "   ✅ AI модель работает на вашем ноутбуке"
echo "   ✅ Railway только проксирует запросы"
echo "   ✅ Быстрый деплой (нет тяжелых ML библиотек)"
echo "   ✅ Полный контроль над AI моделью"
echo ""

# Останавливаем локальный сервер
pkill -f "python3.*main.py" 2>/dev/null || true

# Заменяем main.py на hybrid_main.py
echo "🔄 Переключаемся на гибридную архитектуру..."
cp hybrid_main.py main.py
echo "✅ main.py заменен на hybrid_main.py"

# Заменяем requirements.txt на requirements_hybrid.txt
echo "🔄 Переключаемся на легкие зависимости..."
cp requirements_hybrid.txt requirements.txt
echo "✅ requirements.txt заменен на requirements_hybrid.txt"

# Коммитим изменения
echo "📝 Коммитим гибридную архитектуру..."
git add .
git commit -m "🚀 Переключение на гибридную архитектуру - AI модель локально, Railway проксирует"

# Пушим в GitHub
echo "🌐 Отправляем в GitHub..."
git push origin main

echo ""
echo "✅ КОД ОТПРАВЛЕН В GITHUB!"
echo ""
echo "🔧 СЛЕДУЮЩИЕ ШАГИ:"
echo ""
echo "1️⃣ ЗАПУСТИТЕ ЛОКАЛЬНУЮ AI МОДЕЛЬ:"
echo "   chmod +x start_hybrid_model.sh"
echo "   ./start_hybrid_model.sh"
echo ""
echo "2️⃣ НАСТРОЙТЕ RAILWAY:"
echo "   - Зайдите в Railway Dashboard"
echo "   - Выберите проект 'taxi-support-ai-assistant'"
echo "   - Добавьте переменную окружения:"
echo "     LOCAL_MODEL_URL = [URL_ТУННЕЛЯ_ИЗ_ШАГА_1]"
echo "   - Нажмите 'Deploy'"
echo ""
echo "3️⃣ ПРОВЕРЬТЕ РАБОТУ:"
echo "   - Railway деплой займет ~30 секунд (легкие зависимости)"
echo "   - AI модель работает на вашем ноутбуке"
echo "   - Railway только пересылает запросы"
echo ""
echo "📊 ПРЕИМУЩЕСТВА ГИБРИДНОЙ АРХИТЕКТУРЫ:"
echo "   ⚡ Быстрый деплой Railway (~30 сек вместо 3 мин)"
echo "   🧠 Полный контроль над AI моделью"
echo "   💰 Экономия ресурсов Railway"
echo "   🔧 Легкое обновление модели"
echo "   📱 Работа с локальными данными"
echo ""
echo "⚠️ ВАЖНО:"
echo "   - Не закрывайте терминал с локальной моделью"
echo "   - Ноутбук должен быть подключен к интернету"
echo "   - Туннель должен быть активен"
echo ""
echo "🎉 ГИБРИДНАЯ АРХИТЕКТУРА ГОТОВА К ДЕПЛОЮ!"

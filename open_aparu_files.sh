#!/bin/bash
# 🚀 APARU - Auto Open Files in Cursor
# Автоматически открывает все нужные файлы проекта в Cursor

echo "🚗 APARU - Открываю все файлы в Cursor..."

# Основные файлы проекта
FILES=(
    "main.py"
    "bot.py" 
    "webapp.html"
    "llm_client.py"
    "kb.json"
    "fixtures.json"
    "requirements.txt"
    "README.md"
    "start_aparu.py"
    "start_aparu.sh"
)

# Проверяем наличие Cursor
if ! command -v cursor &> /dev/null; then
    echo "❌ Cursor не найден в PATH"
    echo "📝 Установите Cursor или добавьте в PATH"
    exit 1
fi

# Проверяем наличие файлов
echo "🔍 Проверяю файлы..."
MISSING_FILES=()
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    echo "❌ Отсутствуют файлы: ${MISSING_FILES[*]}"
    exit 1
fi

echo "✅ Все файлы найдены"

# Открываем все файлы в Cursor
echo "📂 Открываю файлы в Cursor..."
cursor "${FILES[@]}"

echo "🎉 Все файлы APARU открыты в Cursor!"
echo ""
echo "📋 Открытые файлы:"
for file in "${FILES[@]}"; do
    echo "  ✅ $file"
done

echo ""
echo "🚀 Для запуска проекта используйте:"
echo "  📡 API: source venv/bin/activate && python main.py"
echo "  🤖 Bot: export BOT_TOKEN='ваш_токен' && python3 bot.py"
echo "  🌐 WebApp: http://localhost:8000/webapp"

# 🚗 APARU Taxi Support AI Assistant

## 🚀 Быстрый запуск

### ⭐ Вариант 1: APARU лаунчер (рекомендуется)
```bash
# Python версия (полнофункциональная)
python3 start_aparu.py

# Bash версия (быстрая)
./start_aparu.sh
```

### Вариант 2: Старые лаунчеры
```bash
# Python скрипт
python3 start_project.py

# Bash скрипт
./start.sh
```

### Вариант 3: Ручной запуск
```bash
# API сервер
python3 main.py

# Telegram Bot (в другом терминале)
python3 bot.py
```

## 📁 Структура проекта

```
├── main.py              # FastAPI сервер
├── bot.py               # Telegram Bot
├── webapp.html          # WebApp интерфейс
├── llm_client.py        # LLM клиент
├── kb.json              # База знаний FAQ
├── fixtures.json        # Моковые данные
├── requirements.txt     # Зависимости
├── start_aparu.py       # 🚀 APARU лаунчер (Python)
├── start_aparu.sh       # 🚀 APARU лаунчер (Bash)
├── start_project.py     # 🚀 Старый лаунчер
├── start.sh             # 🚀 Старый лаунчер
└── README.md            # Документация
```

## 🔗 Ссылки

- **🌐 WebApp:** http://localhost:8000/webapp
- **📡 API:** http://localhost:8000/chat
- **❤️ Health:** http://localhost:8000/health
- **📱 Bot:** @Aparu_support_bot
- **🌐 Production:** https://taxi-support-ai-assistant-production.up.railway.app

## ⚙️ Настройка

### Telegram Bot Token
```bash
export BOT_TOKEN="ваш_токен_от_BotFather"
```

### Установка зависимостей
```bash
pip3 install -r requirements.txt
```

## 🧪 Тестирование

```bash
# Тест API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Где водитель?", "user_id": "test123", "locale": "RU"}'

# Тест Health
curl http://localhost:8000/health
```

## 📋 Функции

- ✅ REST API с эндпоинтом `/chat`
- ✅ Определение языка (RU/KZ/EN)
- ✅ Классификация запросов
- ✅ База знаний FAQ
- ✅ Моки такси-сервиса
- ✅ Telegram Bot + WebApp
- ✅ Деплой на Railway

## ❌ Ограничения

- LLaMA модель не работает из-за ограничений Railway (4GB лимит)
- Используется fallback система с готовыми ответами
- Для LLaMA нужен отдельный сервер
# 📋 Контекст проекта APARU

## 🎯 Обзор проекта
**APARU** - это демо-проект ИИ-ассистента службы поддержки такси в виде Telegram Mini App (WebApp), развернутый через Railway и хранящийся в GitHub.

## 📁 Структура файлов и их назначение

### 🚀 Основные файлы запуска
- **`start_aparu.py`** - Универсальный лаунчер проекта (Python)
- **`start_aparu.sh`** - Универсальный лаунчер проекта (Bash)
- **`start_project.py`** - Старый лаунчер проекта
- **`start.sh`** - Старый лаунчер проекта

### 🏗️ Backend компоненты
- **`main.py`** - Основной FastAPI сервер с REST API
- **`backend/main.py`** - Дублирующий файл сервера (идентичен main.py)
- **`llm_client.py`** - Клиент для работы с LLM (Ollama/fallback)
- **`bot.py`** - Telegram Bot на aiogram

### 🌐 Frontend
- **`webapp.html`** - Telegram WebApp интерфейс с чатом

### 📊 Данные
- **`fixtures.json`** - Моковые данные (поездки, чеки, карты, тикеты)
- **`kb.json`** - База знаний FAQ с ответами

### ⚙️ Конфигурация
- **`requirements.txt`** - Python зависимости
- **`backend/requirements.txt`** - Дублирующий файл зависимостей
- **`railway.toml`** - Конфигурация Railway
- **`Procfile`** - Конфигурация процесса для Railway
- **`docker-compose.yml`** - Docker конфигурация
- **`env.example`** - Пример переменных окружения

### 🧪 Тестирование
- **`test_api.sh`** - Скрипт тестирования API

### 📚 Документация
- **`README.md`** - Основная документация проекта

## 🔧 Технический стек

### Backend
- **FastAPI** - REST API сервер
- **aiogram** - Telegram Bot framework
- **langdetect** - Определение языка
- **ollama** - Локальная LLM (с fallback)
- **uvicorn** - ASGI сервер

### Frontend
- **HTML/JS** - WebApp интерфейс
- **Telegram WebApp SDK** - Интеграция с Telegram

### Хостинг
- **Railway** - Облачный хостинг
- **GitHub** - Хранилище кода

## 🎯 Функциональность

### ИИ-ассистент обрабатывает:
1. **Статус поездки** - "Где водитель?" → возвращает статус
2. **Чеки** - "Пришлите чек" → отправляет чек
3. **Карты** - "Какие карты?" → показывает карты
4. **Жалобы** - "Списали дважды" → эскалация к оператору
5. **FAQ** - "Как считается цена?" → ответы из базы знаний

### Технические возможности:
- ✅ Определение языка (RU/KZ/EN)
- ✅ Классификация интентов
- ✅ Предобработка текста (удаление эмодзи)
- ✅ Поиск в FAQ
- ✅ Моки такси-сервиса
- ✅ Логирование intent, confidence, source

## 🌐 Эндпоинты API

### Основные
- **`POST /chat`** - Основной чат с ИИ
- **`GET /webapp`** - WebApp интерфейс
- **`GET /health`** - Проверка здоровья

### Моки
- **`GET /ride-status/{user_id}`** - Статус поездки
- **`POST /send-receipt/{user_id}`** - Отправка чека
- **`GET /cards/{user_id}`** - Список карт
- **`POST /escalate/{user_id}`** - Эскалация к оператору

## 📱 Telegram Bot команды
- **`/start`** - Начать работу с ботом
- **`/help`** - Справка по командам
- **`/support`** - Открыть чат поддержки

## 🚀 Способы запуска

### 1. APARU лаунчер (рекомендуется)
```bash
python3 start_aparu.py
# или
./start_aparu.sh
```

### 2. Ручной запуск
```bash
# API сервер
python3 main.py

# Telegram Bot (в другом терминале)
python3 bot.py
```

## 🔗 Ссылки
- **🌐 WebApp:** http://localhost:8000/webapp
- **📡 API:** http://localhost:8000/chat
- **❤️ Health:** http://localhost:8000/health
- **📱 Bot:** @Aparu_support_bot
- **🌐 Production:** https://taxi-support-ai-assistant-production.up.railway.app

## ⚠️ Ограничения
- LLaMA модель не работает на Railway (4GB лимит)
- Используется fallback система с готовыми ответами
- Для LLaMA нужен отдельный сервер

## 🧪 Тестирование
```bash
# Тест API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Где водитель?", "user_id": "test123", "locale": "RU"}'

# Тест Health
curl http://localhost:8000/health
```

## 📋 Структура данных

### ChatRequest
```json
{
  "text": "string",
  "user_id": "string", 
  "locale": "string"
}
```

### ChatResponse
```json
{
  "response": "string",
  "intent": "string",
  "confidence": "float",
  "source": "string",
  "timestamp": "string"
}
```

## 🔄 Workflow
1. Пользователь отправляет сообщение
2. Текст предобрабатывается (удаление эмодзи)
3. Определяется язык
4. Классифицируется интент
5. Если FAQ - поиск в базе знаний
6. Если не FAQ - обращение к LLM
7. Возврат ответа с метаданными

## 🎨 UI/UX
- Современный дизайн с градиентами
- Быстрые кнопки для частых запросов
- Индикатор печати
- Адаптивная верстка
- Интеграция с Telegram WebApp SDK

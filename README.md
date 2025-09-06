# Taxi Support AI Assistant

Демо-проект ИИ-ассистента службы поддержки такси на FastAPI с локальной моделью LLaMA.

## Описание

REST API сервер с эндпоинтом `/chat`, который:
- Принимает текст, user_id и locale
- Выполняет предобработку текста (убирает эмодзи и спецсимволы)
- Определяет язык (RU/KZ/EN)
- Классифицирует запрос (FAQ, статус поездки, чек, жалоба)
- Отвечает из базы знаний kb.json для FAQ
- Обращается к локальной LLaMA для других запросов
- Логирует intent, confidence и источник ответа

## Структура проекта

```
backend/
├── main.py              # FastAPI сервер с эндпоинтом /chat
├── llm_client.py        # Клиент для работы с LLaMA (Ollama/transformers)
├── kb.json              # База знаний FAQ
├── fixtures.json        # Моковые данные такси
├── requirements.txt     # Зависимости Python
└── README.md           # Этот файл
```

## Установка и запуск

### 1. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Настройка LLaMA модели

#### Вариант A: Ollama (рекомендуется)

1. Установите Ollama: https://ollama.ai/
2. Загрузите модель:
```bash
ollama pull llama2
# или
ollama pull llama2:7b
```

#### Вариант B: Transformers

Модель будет загружена автоматически при первом запуске.

### 3. Запуск сервера

```bash
python main.py
```

Сервер запустится на `http://localhost:8000`

## API Эндпоинты

### POST /chat

Основной эндпоинт для чата.

**Запрос:**
```json
{
  "text": "Жду такси, где водитель?",
  "user_id": "user_123",
  "locale": "ru"
}
```

**Ответ:**
```json
{
  "response": "Ваша поездка в процессе. Водитель: Айдар, машина: Toyota Camry, номер: 123ABC01. Ожидаемое время прибытия: 5 минут",
  "intent": "ride_status",
  "confidence": 0.95,
  "source": "kb",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Дополнительные эндпоинты

- `GET /ride-status/{user_id}` - статус поездки
- `POST /send-receipt/{user_id}` - отправить чек
- `GET /cards/{user_id}` - список карт
- `POST /escalate/{user_id}` - эскалация к оператору
- `GET /health` - проверка здоровья

## Поддерживаемые интенты

1. **FAQ** - вопросы из базы знаний (цена, промокоды, отмена)
2. **ride_status** - статус поездки ("где водитель")
3. **receipt** - запрос чека ("пришлите чек")
4. **cards** - работа с картами ("какие карты", "сделать основной")
5. **complaint** - жалобы ("списали дважды")

## Тестирование

### Автоматическое тестирование

```bash
# Запуск тестов API
./test_api.sh
```

### Ручное тестирование

```bash
# Статус поездки
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"text": "Жду такси, где водитель?", "user_id": "user_123", "locale": "ru"}'

# FAQ
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"text": "Как считается цена поездки?", "user_id": "user_123", "locale": "ru"}'

# WebApp
open http://localhost:8000/webapp
```

## Конфигурация

### Переключение между Ollama и Transformers

В `llm_client.py` измените параметр `use_ollama`:

```python
# Для Ollama (по умолчанию)
llm_client = LLMClient(use_ollama=True)

# Для Transformers
llm_client = LLMClient(use_ollama=False, model_name="microsoft/DialoGPT-medium")
```

### Настройка модели Ollama

В `llm_client.py` измените `model_name`:

```python
self.model_name = "llama2"  # или "llama2:7b", "codellama", etc.
```

## Логирование

Сервер логирует:
- Входящие запросы (user_id, intent, confidence, locale)
- Ответы (первые 100 символов, источник, интент, уверенность)
- Ошибки работы с LLM

## Моковые данные

Данные хранятся в `fixtures.json`:
- **rides** - активные и завершенные поездки
- **receipts** - чеки пользователей
- **cards** - привязанные карты
- **tickets** - тикеты поддержки

## База знаний

FAQ хранится в `kb.json` с ключевыми словами для поиска.

## Быстрый старт

### Локальный запуск

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd backend

# Запустите скрипт установки
./start.sh
```

### Ручная установка

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## Развертывание

### Railway (рекомендуется)

1. Создайте репозиторий на GitHub
2. Подключите к Railway: https://railway.app
3. Настройте переменные окружения:
   - `BOT_TOKEN` - токен Telegram бота
   - `API_URL` - URL вашего Railway приложения
4. Railway автоматически развернет проект

### Docker

```bash
# Локальный запуск с Docker Compose
docker-compose up -d

# Или только API
docker build -t taxi-support .
docker run -p 8000:8000 taxi-support
```

### Telegram Bot

1. Создайте бота через @BotFather
2. Получите токен
3. Установите переменную `BOT_TOKEN`
4. Запустите бота: `python bot.py`

## Требования

- Python 3.9+
- Ollama (для локальной LLaMA) или Transformers
- 4GB+ RAM (для работы с моделями)

## Лицензия

MIT License

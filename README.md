# Taxi Support AI Assistant

Демо-проект ИИ-ассистента службы поддержки такси на FastAPI с локальной моделью LLaMA.

## 🚀 Описание

REST API сервер с эндпоинтом `/chat`, который:
- Принимает текст, user_id и locale
- Выполняет предобработку текста (убирает эмодзи и спецсимволы)
- Определяет язык (RU/KZ/EN)
- Классифицирует запрос (FAQ, статус поездки, чек, жалоба)
- Отвечает из базы знаний kb.json для FAQ
- Обращается к локальной LLaMA для других запросов
- Логирует intent, confidence и источник ответа

## 📁 Структура проекта

```
├── backend/
│   ├── main.py              # FastAPI сервер с эндпоинтом /chat
│   ├── llm_client.py        # Клиент для работы с LLaMA (Ollama/transformers)
│   ├── bot.py               # Telegram Bot
│   ├── webapp.html          # WebApp интерфейс
│   ├── kb.json              # База знаний FAQ
│   ├── fixtures.json        # Моковые данные такси
│   ├── requirements.txt     # Зависимости Python
│   ├── Dockerfile           # Docker конфигурация
│   ├── docker-compose.yml   # Docker Compose
│   ├── railway.toml         # Railway конфигурация
│   ├── start.sh            # Скрипт запуска
│   ├── test_api.sh         # Скрипт тестирования
│   └── README.md           # Документация
└── README.md               # Этот файл
```

## 🚀 Быстрый старт

### Локальный запуск

```bash
# Клонируйте репозиторий
git clone https://github.com/YOUR_USERNAME/taxi-support-ai-assistant.git
cd taxi-support-ai-assistant/backend

# Запустите скрипт установки
./start.sh
```

### Ручная установка

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 🌐 API Эндпоинты

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

- `GET /webapp` - WebApp интерфейс
- `GET /health` - проверка здоровья
- `GET /docs` - API документация
- `GET /ride-status/{user_id}` - статус поездки
- `POST /send-receipt/{user_id}` - отправить чек
- `GET /cards/{user_id}` - список карт
- `POST /escalate/{user_id}` - эскалация к оператору

## 🤖 Поддерживаемые интенты

1. **FAQ** - вопросы из базы знаний (цена, промокоды, отмена)
2. **ride_status** - статус поездки ("где водитель")
3. **receipt** - запрос чека ("пришлите чек")
4. **cards** - работа с картами ("какие карты", "сделать основной")
5. **complaint** - жалобы ("списали дважды")

## 🧪 Тестирование

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

## 🚀 Развертывание

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

## ⚙️ Конфигурация

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

## 📊 Логирование

Сервер логирует:
- Входящие запросы (user_id, intent, confidence, locale)
- Ответы (первые 100 символов, источник, интент, уверенность)
- Ошибки работы с LLM

## 🗃️ Моковые данные

Данные хранятся в `fixtures.json`:
- **rides** - активные и завершенные поездки
- **receipts** - чеки пользователей
- **cards** - привязанные карты
- **tickets** - тикеты поддержки

## 📚 База знаний

FAQ хранится в `kb.json` с ключевыми словами для поиска.

## 🔧 Требования

- Python 3.9+
- Ollama (для локальной LLaMA) или Transformers
- 4GB+ RAM (для работы с моделями)

## 📄 Лицензия

MIT License

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📞 Поддержка

Если у вас есть вопросы или проблемы, создайте Issue в репозитории.

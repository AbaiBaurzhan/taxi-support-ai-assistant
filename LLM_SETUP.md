# 🤖 Настройка локального LLM для APARU

## 🎯 Цель
Запустить LLM на вашем компьютере и подключить его к Railway production для обработки запросов.

## 🚀 Быстрый старт

### 1. Установка Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Скачайте с https://ollama.ai/download
```

### 2. Загрузка модели
```bash
# Загружаем LLaMA 2 (7B параметров)
ollama pull llama2

# Или более легкую модель
ollama pull llama2:7b
```

### 3. Запуск локального сервера
```bash
# Запускаем Ollama сервер
ollama serve

# В другом терминале проверяем
curl http://localhost:11434/api/tags
```

### 4. Установка туннеля (ngrok)
```bash
# macOS
brew install ngrok

# Или скачайте с https://ngrok.com/download
```

### 5. Создание туннеля
```bash
# Создаем туннель к Ollama
ngrok http 11434

# Получите URL вида: https://abc123.ngrok.io
```

## 🔧 Настройка Railway

### 1. Добавьте переменные окружения в Railway:
```bash
LLM_URL=https://your-ngrok-url.ngrok.io
LLM_MODEL=llama2
LLM_ENABLED=true
```

### 2. Или используйте автоматический скрипт:
```bash
python3 local_llm_server.py
```

## 🧪 Тестирование

### 1. Локальный тест
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "prompt": "Привет! Как дела?",
    "stream": false
  }'
```

### 2. Тест через туннель
```bash
curl -X POST https://your-ngrok-url.ngrok.io/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2", 
    "prompt": "Привет! Как дела?",
    "stream": false
  }'
```

### 3. Тест APARU API
```bash
curl -X POST https://taxi-support-ai-assistant-production.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Расскажи про цены на такси",
    "user_id": "test123",
    "locale": "RU"
  }'
```

## 🔄 Альтернативные решения

### 1. **Cloudflare Tunnel** (бесплатно)
```bash
# Установка
npm install -g cloudflared

# Создание туннеля
cloudflared tunnel --url http://localhost:11434
```

### 2. **Serveo** (бесплатно)
```bash
# Простой SSH туннель
ssh -R 80:localhost:11434 serveo.net
```

### 3. **LocalTunnel** (бесплатно)
```bash
# Установка
npm install -g localtunnel

# Создание туннеля
lt --port 11434
```

## ⚙️ Конфигурация

### Переменные окружения:
- `LLM_URL` - URL вашего LLM сервера
- `LLM_MODEL` - Название модели (llama2)
- `LLM_ENABLED` - Включить/выключить LLM (true/false)

### Пример .env файла:
```bash
LLM_URL=https://abc123.ngrok.io
LLM_MODEL=llama2
LLM_ENABLED=true
```

## 🚨 Важные моменты

### 1. **Безопасность**
- ngrok URL меняется при перезапуске
- Используйте ngrok с аккаунтом для стабильного URL
- Ограничьте доступ по IP если возможно

### 2. **Производительность**
- LLaMA 2 требует ~4GB RAM
- Первый запрос может быть медленным
- Используйте более легкие модели для тестов

### 3. **Стабильность**
- Туннель может разрываться
- Настройте автопереподключение
- Имейте fallback на готовые ответы

## 🔧 Автоматизация

### Скрипт автозапуска (macOS):
```bash
# Создайте файл ~/start_llm.sh
#!/bin/bash
cd /path/to/your/project
ollama serve &
sleep 5
ngrok http 11434 &
```

### Добавьте в crontab:
```bash
# Автозапуск при загрузке
@reboot /path/to/start_llm.sh
```

## 📊 Мониторинг

### 1. Проверка статуса Ollama:
```bash
curl http://localhost:11434/api/tags
```

### 2. Проверка туннеля:
```bash
curl http://localhost:4040/api/tunnels
```

### 3. Логи Railway:
```bash
railway logs
```

## 🎉 Результат

После настройки:
- ✅ LLM работает на вашем компьютере
- ✅ Railway получает ответы от вашего LLM
- ✅ Пользователи получают умные ответы
- ✅ Fallback система как резерв

## 🆘 Решение проблем

### Ollama не запускается:
```bash
# Проверьте порт
lsof -i :11434

# Перезапустите
pkill ollama
ollama serve
```

### Туннель не работает:
```bash
# Проверьте ngrok
ngrok version

# Перезапустите
pkill ngrok
ngrok http 11434
```

### Railway не подключается:
- Проверьте переменные окружения
- Убедитесь что туннель активен
- Проверьте логи Railway

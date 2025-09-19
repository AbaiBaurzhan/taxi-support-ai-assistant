# 🚀 ГИБРИДНАЯ АРХИТЕКТУРА APARU AI

## 📋 НАСТРОЙКА RAILWAY

### 1. Переменные окружения:
```
LOCAL_MODEL_URL = https://32f43b95cbea.ngrok-free.app
```

### 2. Структура проекта:
- `main.py` - гибридный FastAPI сервер
- `requirements.txt` - легкие зависимости (без ML библиотек)
- `hybrid_main.py` - резервная копия

### 3. Архитектура:
```
Пользователь → Railway (прокси) → ngrok туннель → LLM модель на ноутбуке
```

## 🔧 ЛОКАЛЬНЫЕ КОМПОНЕНТЫ

### Ollama (порт 11434):
```bash
ollama serve
```

### ngrok туннель:
```bash
ngrok http 11434
```

### LLM модель:
```bash
ollama run aparu-senior-ai
```

## 🧪 ТЕСТИРОВАНИЕ

### Проверка локальной модели:
```bash
curl -X POST http://localhost:11434/api/generate \
  -H 'Content-Type: application/json' \
  -d '{"model": "aparu-senior-ai", "prompt": "Что такое наценка?", "stream": false}'
```

### Проверка через ngrok:
```bash
curl -X POST https://32f43b95cbea.ngrok-free.app/api/generate \
  -H 'Content-Type: application/json' \
  -H 'ngrok-skip-browser-warning: true' \
  -d '{"model": "aparu-senior-ai", "prompt": "Что такое наценка?", "stream": false}'
```

## ⚠️ ВАЖНО

1. **Не закрывайте терминал** - Ollama и ngrok должны работать
2. **Откройте ngrok URL** в браузере для активации
3. **Первая загрузка** модели занимает время (5-10 минут)
4. **ngrok URL может измениться** - обновите переменную в Railway

## 🎯 ПРЕИМУЩЕСТВА

- ✅ LLM модель на ноутбуке - полный контроль
- ✅ Быстрый деплой Railway - без тяжелых ML библиотек
- ✅ Гибридная система - LLM + fallback к простому поиску
- ✅ Масштабируемость - можно добавить больше моделей
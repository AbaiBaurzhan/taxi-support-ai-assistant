# 🚀 ОБНОВЛЕННЫЕ ИНСТРУКЦИИ ДЛЯ RAILWAY DASHBOARD

## 📋 ОБНОВИТЕ ПЕРЕМЕННУЮ ОКРУЖЕНИЯ:

### 1. Откройте Railway Dashboard:
```
https://railway.app/dashboard
```

### 2. Найдите проект:
- Ищите `taxi-support-ai-assistant`
- Нажмите на него

### 3. Перейдите в Settings:
- Нажмите на вкладку **"Settings"** (слева)
- Найдите раздел **"Environment Variables"**

### 4. Обновите переменную:
- **Ключ:** `LOCAL_LLM_URL`
- **Значение:** `https://527f457e3d28.ngrok-free.app`
- Нажмите **"Save"**

### 5. Перезапустите сервис:
- Railway автоматически перезапустит сервис
- Подождите 2-3 минуты

## 🔧 ТЕКУЩИЙ СТАТУС:

| Компонент | Статус | Адрес |
|-----------|--------|-------|
| **Ollama** | ✅ Работает | `localhost:11434` |
| **Локальный сервер** | ✅ Работает | `172.20.10.5:8001` |
| **Ngrok туннель** | ✅ Работает | `https://527f457e3d28.ngrok-free.app` |
| **Railway** | 🔄 Обновляется | `https://taxi-support-ai-assistant-production.up.railway.app` |

## 🧪 ПОСЛЕ ОБНОВЛЕНИЯ:

Railway сможет подключиться к локальной LLM модели через ngrok туннель!

### Тестирование:
```bash
curl -X POST https://taxi-support-ai-assistant-production.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Что такое наценка?", "user_id": "test", "locale": "ru"}'
```

## ⚠️ ВАЖНО:

- **Не закрывайте терминал** - локальный сервер и ngrok должны работать
- **Не выключайте ноутбук** - Railway нужен доступ к серверу
- **Проверьте интернет** - стабильное соединение необходимо

## 🎯 РЕЗУЛЬТАТ:

После обновления Railway переменной:
- ✅ **Railway подключится** к локальной LLM модели через ngrok
- ✅ **LLM модель будет работать** через Railway
- ✅ **Пользователи получат ответы** от LLM модели

**�� ОБНОВИТЕ ПЕРЕМЕННУЮ `LOCAL_LLM_URL` НА `https://527f457e3d28.ngrok-free.app` В RAILWAY DASHBOARD!**

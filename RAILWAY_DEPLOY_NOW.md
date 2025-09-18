# 🚀 APARU LLM - Деплой на Railway

## 📋 **Пошаговая инструкция:**

### **1. 🌐 Переходим на Railway:**
- Откройте: https://railway.app
- Нажмите "Login" → "GitHub"
- Авторизуйтесь через GitHub

### **2. 🆕 Создаем новый проект:**
- Нажмите "New Project"
- Выберите "Deploy from GitHub repo"
- Найдите репозиторий: `AbaiBaurzhan/taxi-support-ai-assistant`
- Нажмите "Deploy Now"

### **3. ⚙️ Настраиваем переменные окружения:**
В разделе "Variables" добавьте:

```bash
# LLM настройки (ваш туннель)
LLM_URL=https://45fe8195b3e7.ngrok-free.app
LLM_MODEL=aparu-support
LLM_ENABLED=true

# Telegram Bot (замените на ваш токен)
BOT_TOKEN=your_telegram_bot_token_here

# Дополнительные настройки
PYTHON_VERSION=3.11
PORT=8000
```

### **4. 🔧 Настраиваем Railway конфигурацию:**

Railway автоматически определит Python проект и установит зависимости из `requirements.txt`.

### **5. 🚀 Запускаем деплой:**
- Railway автоматически начнет сборку
- Процесс займет 2-3 минуты
- После успешного деплоя получите URL: `https://your-app.railway.app`

### **6. 🧪 Тестируем деплой:**

#### **Проверка API:**
```bash
curl https://your-app.railway.app/health
```

#### **Проверка чата:**
```bash
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Что такое наценка?",
    "user_id": "test123",
    "locale": "ru"
  }'
```

#### **Проверка WebApp:**
- Откройте: `https://your-app.railway.app/webapp`

### **7. 🤖 Настраиваем Telegram Bot:**

#### **В BotFather:**
1. Создайте бота: `/newbot`
2. Получите токен
3. Добавьте токен в Railway Variables

#### **Настройка WebApp:**
```bash
# В BotFather выполните:
/setmenubutton
# Выберите вашего бота
# Отправьте: https://your-app.railway.app/webapp
```

### **8. 🔄 Мониторинг:**

#### **Логи Railway:**
- Перейдите в раздел "Deployments"
- Нажмите на последний деплой
- Смотрите логи в реальном времени

#### **Проверка туннеля:**
```bash
# На вашем компьютере
curl http://localhost:4040/api/tunnels
```

## 🎯 **Архитектура после деплоя:**

```
Пользователь → Telegram Bot → Railway → ngrok → Ваш компьютер → Ollama → Ответ
     ↓              ↓              ↓
  WebApp        FastAPI        APARU LLM
     ↓              ↓              ↓
  Chat UI      API Server    Smart Search
```

## ✅ **Что получим:**

### **🌐 Публичный доступ:**
- ✅ API доступен по HTTPS
- ✅ WebApp работает в Telegram
- ✅ Bot отвечает пользователям

### **🧠 Умная поддержка:**
- ✅ Обученная модель APARU
- ✅ Понимание контекста вопросов
- ✅ База знаний из BZ.txt
- ✅ Fallback система
- ✅ Многоязычность (RU/KZ/EN)

### **📊 Мониторинг:**
- ✅ Логи Railway
- ✅ Статистика запросов
- ✅ Ошибки и отладка

## 🚨 **Важные моменты:**

### **1. Туннель ngrok:**
- ✅ Сейчас работает: `https://45fe8195b3e7.ngrok-free.app`
- ⚠️ URL меняется при перезапуске ngrok
- 💡 Решение: ngrok Pro ($8/месяц) для стабильного URL

### **2. Альтернативы туннелю:**
```bash
# Cloudflare Tunnel (бесплатно)
cloudflared tunnel --url http://localhost:11434

# Serveo (бесплатно)
ssh -R 80:localhost:11434 serveo.net

# LocalTunnel (бесплатно)
lt --port 11434
```

### **3. Автоматизация:**
```bash
#!/bin/bash
# Скрипт для автопереподключения
while true; do
    # Проверяем туннель
    if ! curl -s http://localhost:4040/api/tunnels > /dev/null; then
        echo "Перезапускаем туннель..."
        pkill ngrok
        ngrok http 11434 &
        sleep 5
        
        # Обновляем Railway
        NEW_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
        # Обновите LLM_URL в Railway Variables
    fi
    sleep 300
done
```

## 🎉 **Результат:**

После деплоя у вас будет:
- ✅ Полноценный AI-ассистент поддержки такси
- ✅ Обученная модель на ваших данных
- ✅ Понимание контекста и смысла вопросов
- ✅ Telegram Bot + WebApp
- ✅ Публичный API
- ✅ Надежная система с fallback

**APARU готов к работе!** 🚀

## 🔗 **Ссылки для деплоя:**

- **Railway:** https://railway.app
- **Репозиторий:** https://github.com/AbaiBaurzhan/taxi-support-ai-assistant
- **Туннель:** https://45fe8195b3e7.ngrok-free.app
- **BotFather:** https://t.me/BotFather

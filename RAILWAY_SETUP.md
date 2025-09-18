# Railway Configuration для APARU LLM

## 🚀 Настройка Railway

### 1. **Переменные окружения:**
```bash
# В Railway Dashboard → Variables
LLM_URL=https://your-ngrok-url.ngrok.io
LLM_MODEL=aparu-support
LLM_ENABLED=true
BOT_TOKEN=your_telegram_bot_token
```

### 2. **Procfile:**
```
web: python main.py
```

### 3. **railway.toml:**
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python main.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

## 🔧 Локальная настройка

### 1. **Запуск Ollama:**
```bash
# На вашем компьютере
ollama serve
```

### 2. **Создание туннеля:**
```bash
# Установка ngrok
brew install ngrok

# Создание туннеля
ngrok http 11434

# Получаем URL: https://abc123.ngrok.io
```

### 3. **Обновление Railway:**
```bash
# Установка Railway CLI
npm install -g @railway/cli

# Логин
railway login

# Установка переменных
railway variables set LLM_URL=https://abc123.ngrok.io
railway variables set LLM_MODEL=aparu-support
railway variables set LLM_ENABLED=true
```

## 📊 Архитектура

```
Пользователь → Railway → ngrok → Ваш компьютер → Ollama → Ответ
     ↓              ↓
  Telegram Bot   FastAPI Server
     ↓              ↓
  WebApp        APARU Enhanced Client
                     ↓
              База знаний APARU
```

## 🎯 Преимущества

### ✅ **Для Railway:**
- Легкий сервер (только API)
- Быстрый запуск
- Низкое потребление ресурсов
- Стабильная работа

### ✅ **Для LLM:**
- Полная мощность вашего компьютера
- GPU ускорение (если есть)
- Быстрая генерация
- Стабильная работа

### ✅ **Для пользователей:**
- Быстрые ответы
- Точные данные APARU
- Надежная работа

## 🔄 Альтернативные решения

### 1. **Cloudflare Tunnel (бесплатно):**
```bash
# Установка
npm install -g cloudflared

# Создание туннеля
cloudflared tunnel --url http://localhost:11434
```

### 2. **Serveo (бесплатно):**
```bash
# SSH туннель
ssh -R 80:localhost:11434 serveo.net
```

### 3. **LocalTunnel (бесплатно):**
```bash
# Установка
npm install -g localtunnel

# Создание туннеля
lt --port 11434
```

## 🚨 Важные моменты

### **1. Стабильность туннеля:**
- ngrok бесплатно - URL меняется при перезапуске
- Решение: ngrok Pro ($8/месяц) для стабильного URL
- Или используйте Cloudflare Tunnel (бесплатно)

### **2. Мониторинг:**
```bash
# Проверка статуса Ollama
curl http://localhost:11434/api/tags

# Проверка туннеля
curl http://localhost:4040/api/tunnels

# Проверка Railway
railway logs
```

### **3. Автоматизация:**
```bash
#!/bin/bash
# Скрипт автопереподключения
while true; do
    # Проверяем Ollama
    if ! curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "Ollama не работает, перезапускаю..."
        ollama serve &
        sleep 10
    fi
    
    # Проверяем туннель
    if ! curl -s http://localhost:4040/api/tunnels > /dev/null; then
        echo "Туннель не работает, перезапускаю..."
        pkill ngrok
        ngrok http 11434 &
        sleep 5
        
        # Обновляем Railway
        NEW_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
        railway variables set LLM_URL="$NEW_URL"
    fi
    
    sleep 300  # Проверяем каждые 5 минут
done
```

## 🎉 Результат

**С туннелем:**
- ✅ Railway работает стабильно
- ✅ LLM работает на вашем компьютере
- ✅ Пользователи получают быстрые ответы
- ✅ Система надежна и масштабируема

**Без туннеля (только fallback):**
- ✅ Railway работает
- ❌ Только готовые ответы из базы знаний
- ❌ Нет генерации новых ответов
- ✅ Система все равно полезна

# 🌐 Схема работы туннеля

## 📊 Архитектура системы

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Пользователь   │    │     Railway     │    │   ngrok.com     │
│                 │    │   (Production)  │    │   (Туннель)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. Запрос             │                       │
         ├──────────────────────►│                       │
         │                       │ 2. Запрос к LLM       │
         │                       ├──────────────────────►│
         │                       │                       │
         │                       │                       │ 3. Передача на
         │                       │                       ├─────────────────┐
         │                       │                       │                 │
         │                       │                       │                 ▼
         │                       │                       │    ┌─────────────────┐
         │                       │                       │    │  Ваш компьютер   │
         │                       │                       │    │   localhost:11434│
         │                       │                       │    │     (Ollama)     │
         │                       │                       │    └─────────────────┘
         │                       │                       │                 │
         │                       │                       │ 4. Ответ         │
         │                       │                       ◄─────────────────┘
         │                       │                       │
         │                       │ 5. Ответ от LLM       │
         │                       ◄──────────────────────┤
         │                       │                       │
         │ 6. Финальный ответ    │                       │
         ◄──────────────────────┤                       │
```

## 🔄 Пошаговый процесс

### 1. **Пользователь отправляет запрос**
```json
POST /chat
{
  "text": "Где водитель?",
  "user_id": "123",
  "locale": "RU"
}
```

### 2. **Railway обрабатывает запрос**
- Определяет язык: RU
- Классифицирует интент: ride_status
- Не находит в FAQ
- Решает использовать LLM

### 3. **Railway отправляет запрос в LLM**
```json
POST https://abc123.ngrok.io/api/generate
{
  "model": "llama2",
  "prompt": "Ты - ИИ-ассистент службы поддержки такси...",
  "stream": false
}
```

### 4. **ngrok получает запрос**
- Принимает запрос на https://abc123.ngrok.io
- Перенаправляет на localhost:11434
- Передает запрос вашему компьютеру

### 5. **Ollama обрабатывает запрос**
- Получает запрос на localhost:11434
- Загружает модель llama2
- Генерирует ответ
- Возвращает результат

### 6. **Ответ идет обратно**
```
Ollama → ngrok → Railway → Пользователь
```

## 🛠️ Технические детали

### **ngrok как прокси:**
```bash
# ngrok создает два соединения:
# 1. Слушает на ngrok.com (публичный URL)
# 2. Подключается к localhost:11434 (ваш компьютер)

ngrok http 11434
# Результат:
# Forwarding: https://abc123.ngrok.io -> http://localhost:11434
```

### **HTTP заголовки:**
```http
# Запрос от Railway к ngrok:
POST /api/generate HTTP/1.1
Host: abc123.ngrok.io
Content-Type: application/json
Content-Length: 123

# ngrok добавляет заголовки:
X-Forwarded-For: railway-ip
X-Forwarded-Proto: https
X-Forwarded-Host: abc123.ngrok.io
```

### **Безопасность:**
- ngrok шифрует соединение (HTTPS)
- Только ngrok знает ваш внутренний IP
- Railway видит только публичный URL

## 🔧 Альтернативные туннели

### **1. Cloudflare Tunnel**
```bash
cloudflared tunnel --url http://localhost:11434
# Создает: https://random-name.trycloudflare.com
```

### **2. Serveo (SSH)**
```bash
ssh -R 80:localhost:11434 serveo.net
# Создает: https://random-name.serveo.net
```

### **3. LocalTunnel**
```bash
lt --port 11434
# Создает: https://random-name.loca.lt
```

## ⚡ Производительность

### **Латентность:**
```
Railway → ngrok: ~50-100ms
ngrok → Ваш компьютер: ~10-50ms
Ваш компьютер → Ollama: ~1-5ms
Ollama обработка: ~500-2000ms
```

### **Пропускная способность:**
- ngrok: ~1MB/s (бесплатно)
- Cloudflare: ~10MB/s (бесплатно)
- Serveo: ~5MB/s (бесплатно)

## 🚨 Ограничения

### **1. Стабильность URL:**
```bash
# ngrok бесплатно - URL меняется при перезапуске
# Решение: ngrok Pro ($5/месяц) для стабильного URL
```

### **2. Время жизни:**
```bash
# Бесплатные туннели могут закрываться через 8 часов
# Решение: автопереподключение
```

### **3. Безопасность:**
```bash
# Публичный URL доступен всем
# Решение: ограничение по IP или аутентификация
```

## 🔄 Автоматизация

### **Скрипт автопереподключения:**
```bash
#!/bin/bash
while true; do
    ngrok http 11434 &
    sleep 3600  # 1 час
    pkill ngrok
    sleep 5
done
```

### **Мониторинг:**
```bash
# Проверка статуса туннеля
curl http://localhost:4040/api/tunnels

# Проверка Ollama
curl http://localhost:11434/api/tags
```

## 🎯 Практический пример

### **Запуск системы:**
```bash
# Терминал 1: Ollama
ollama serve

# Терминал 2: Туннель
ngrok http 11434

# Терминал 3: Мониторинг
watch -n 5 'curl -s http://localhost:4040/api/tunnels | jq'
```

### **Тестирование:**
```bash
# Получаем URL туннеля
TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

# Тестируем LLM
curl -X POST "$TUNNEL_URL/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama2", "prompt": "Привет!", "stream": false}'

# Обновляем Railway
railway variables set LLM_URL="$TUNNEL_URL"
```

## 🎉 Результат

После настройки туннеля:
- ✅ Railway может достучаться до вашего LLM
- ✅ Пользователи получают умные ответы
- ✅ Ваш компьютер остается локальным
- ✅ Система работает стабильно

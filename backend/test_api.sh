#!/bin/bash

# Скрипт для тестирования API

API_URL="http://localhost:8000"

echo "🧪 Тестирование API эндпоинтов..."

# Проверка здоровья
echo "1. Проверка здоровья сервиса..."
curl -s "$API_URL/health" | jq '.' || echo "❌ Сервис недоступен"

echo -e "\n2. Тестирование чата..."

# Тест FAQ
echo "📝 Тест FAQ (цена поездки):"
curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"text": "Как считается цена поездки?", "user_id": "user_123", "locale": "ru"}' \
  | jq '.'

echo -e "\n📝 Тест статуса поездки:"
curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"text": "Где мой водитель?", "user_id": "user_123", "locale": "ru"}' \
  | jq '.'

echo -e "\n📝 Тест запроса чека:"
curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"text": "Пришлите чек", "user_id": "user_123", "locale": "ru"}' \
  | jq '.'

echo -e "\n📝 Тест жалобы:"
curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"text": "С меня списали дважды", "user_id": "user_456", "locale": "ru"}' \
  | jq '.'

echo -e "\n✅ Тестирование завершено!"

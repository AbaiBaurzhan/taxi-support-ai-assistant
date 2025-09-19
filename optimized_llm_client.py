#!/usr/bin/env python3
"""
🚀 ОПТИМИЗИРОВАННАЯ LLM МОДЕЛЬ APARU
Быстрая генерация ответов с оптимизированными параметрами
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedLLMClient:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_name = "aparu-senior-ai"
        self.ollama_available = False
        self._check_ollama()
        
        # Оптимизированные параметры для быстрой генерации
        self.optimized_params = {
            "temperature": 0.3,  # Низкая температура для стабильности
            "num_predict": 200,  # Короткие ответы (быстрее)
            "num_ctx": 512,      # Меньший контекст
            "repeat_penalty": 1.1,
            "top_k": 20,         # Ограниченный выбор
            "top_p": 0.9,        # Ограниченная вероятность
            "stop": ["\n\n", "Вопрос:", "Ответ:"]  # Стоп-слова
        }
        
        # Системный промпт для быстрых ответов
        self.system_prompt = """Ты — AI-ассистент службы поддержки такси APARU. 
Отвечай КРАТКО и ТОЧНО на вопросы о:
- Наценках и тарифах
- Доставке и курьерских услугах  
- Балансе и платежах
- Проблемах с приложением

Правила:
1. Отвечай только по существу
2. Максимум 2-3 предложения
3. Используй простые слова
4. Если не знаешь - скажи "Обратитесь в поддержку"

Примеры хороших ответов:
- "Наценка - дополнительная плата за высокий спрос"
- "Для доставки: приложение → Доставка → адреса → заказ"
- "Пополнить баланс: Профиль → Пополнить → способ оплаты"
- "Приложение не работает? Перезапустите и обновите" """

    def _check_ollama(self):
        """Проверяет доступность Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if any(m["name"].startswith(self.model_name) for m in models):
                    self.ollama_available = True
                    logger.info(f"✅ Ollama и модель '{self.model_name}' доступны")
                else:
                    logger.warning(f"⚠️ Модель '{self.model_name}' не найдена")
            else:
                logger.warning(f"⚠️ Ollama недоступен: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к Ollama: {e}")

    def get_fast_llm_response(self, question: str) -> Optional[Dict[str, Any]]:
        """Получает быстрый ответ от LLM модели"""
        if not self.ollama_available:
            logger.error("❌ Ollama недоступен")
            return None

        try:
            # Формируем оптимизированный промпт
            prompt = f"{self.system_prompt}\n\nВопрос: {question}\nОтвет:"
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": self.optimized_params
            }
            
            logger.info(f"🧠 Запрашиваем быстрый ответ от LLM...")
            start_time = datetime.now()
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=45  # Уменьшаем таймаут до 45 секунд
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '').strip()
                
                if answer:
                    logger.info(f"✅ LLM ответ получен за {processing_time:.2f}с")
                    return {
                        "answer": answer,
                        "category": "llm_generated",
                        "confidence": 0.9,
                        "source": "optimized_llm",
                        "processing_time": processing_time
                    }
            
            logger.warning(f"⚠️ LLM вернул неожиданный ответ: {response.status_code}")
            return None
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ LLM таймаут (>45с)")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка LLM: {e}")
            return None

    def get_hybrid_response(self, question: str) -> Dict[str, Any]:
        """Гибридный ответ: LLM + fallback"""
        # Сначала пытаемся получить LLM ответ
        llm_result = self.get_fast_llm_response(question)
        
        if llm_result:
            return llm_result
        
        # Fallback к простому поиску
        logger.info("🔄 Fallback к простому поиску...")
        return self._simple_search(question)
    
    def _simple_search(self, question: str) -> Dict[str, Any]:
        """Простой поиск по ключевым словам (fallback)"""
        question_lower = question.lower()
        
        # Простая база знаний
        simple_kb = {
            "наценка": "Наценка - дополнительная плата за высокий спрос. Помогает привлечь больше водителей.",
            "доставка": "Для доставки: приложение → Доставка → укажите адреса → подтвердите заказ.",
            "баланс": "Пополнить баланс: Профиль → Пополнить → выберите способ оплаты.",
            "приложение": "Приложение не работает? Перезапустите, проверьте интернет, обновите версию."
        }
        
        # Поиск по ключевым словам
        for keyword, answer in simple_kb.items():
            if keyword in question_lower:
                return {
                    "answer": answer,
                    "category": keyword,
                    "confidence": 0.8,
                    "source": "simple_search",
                    "processing_time": 0.1
                }
        
        # Fallback
        return {
            "answer": "Извините, не могу найти ответ. Обратитесь в службу поддержки.",
            "category": "unknown",
            "confidence": 0.0,
            "source": "fallback",
            "processing_time": 0.1
        }

# Глобальный экземпляр
optimized_llm_client = OptimizedLLMClient()

def test_optimized_llm():
    """Тестирует оптимизированную LLM модель"""
    print("🧪 ТЕСТИРУЮ ОПТИМИЗИРОВАННУЮ LLM МОДЕЛЬ")
    print("=" * 50)
    
    test_questions = [
        "Что такое наценка?",
        "Как заказать доставку?",
        "Как пополнить баланс?",
        "Приложение не работает"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Вопрос {i}: {question}")
        
        result = optimized_llm_client.get_hybrid_response(question)
        
        print(f"✅ Ответ: {result['answer']}")
        print(f"📊 Источник: {result['source']}")
        print(f"⏱️ Время: {result['processing_time']:.2f}с")
        print(f"🎯 Уверенность: {result['confidence']:.2f}")

if __name__ == "__main__":
    test_optimized_llm()

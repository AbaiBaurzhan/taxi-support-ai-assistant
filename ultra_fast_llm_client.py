#!/usr/bin/env python3
"""
⚡ СУПЕР-БЫСТРАЯ LLM МОДЕЛЬ APARU
Максимально быстрая генерация ответов
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltraFastLLMClient:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_name = "aparu-senior-ai"
        self.ollama_available = False
        self._check_ollama()
        
        # УЛЬТРА-БЫСТРЫЕ параметры для максимальной скорости
        self.ultra_fast_params = {
            "temperature": 0.05,  # Минимальная температура
            "num_predict": 50,    # Очень короткие ответы
            "num_ctx": 128,       # Минимальный контекст
            "repeat_penalty": 1.0,
            "top_k": 5,           # Минимальный выбор
            "top_p": 0.7,         # Минимальная вероятность
            "stop": ["\n", ".", "!", "?", "Ответ:"]  # Ранние стоп-слова
        }
        
        # Минимальный системный промпт
        self.minimal_prompt = """APARU такси. Отвечай КРАТКО:
- Наценка = доплата за спрос
- Доставка = приложение → Доставка → адрес
- Баланс = Профиль → Пополнить
- Приложение = перезапуск + обновление

Максимум 1 предложение. Если не знаешь = "Обратитесь в поддержку" """

    def _check_ollama(self):
        """Проверяет доступность Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
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

    def get_ultra_fast_llm_response(self, question: str) -> Optional[Dict[str, Any]]:
        """Получает ультра-быстрый ответ от LLM модели"""
        if not self.ollama_available:
            logger.error("❌ Ollama недоступен")
            return None

        try:
            # Минимальный промпт для максимальной скорости
            prompt = f"{self.minimal_prompt}\n\n{question}:"
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": self.ultra_fast_params
            }
            
            logger.info(f"⚡ Запрашиваем ультра-быстрый ответ от LLM...")
            start_time = datetime.now()
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=15  # Максимально короткий таймаут
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '').strip()
                
                if answer:
                    logger.info(f"⚡ LLM ответ получен за {processing_time:.2f}с")
                    return {
                        "answer": answer,
                        "category": "llm_generated",
                        "confidence": 0.95,
                        "source": "ultra_fast_llm",
                        "processing_time": processing_time
                    }
            
            logger.warning(f"⚠️ LLM вернул неожиданный ответ: {response.status_code}")
            return None
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ LLM таймаут (>15с)")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка LLM: {e}")
            return None

    def get_hybrid_response(self, question: str) -> Dict[str, Any]:
        """Гибридный ответ: Ультра-быстрый LLM + fallback"""
        # Сначала пытаемся получить ультра-быстрый LLM ответ
        llm_result = self.get_ultra_fast_llm_response(question)
        
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
ultra_fast_llm_client = UltraFastLLMClient()

def test_ultra_fast_llm():
    """Тестирует ультра-быструю LLM модель"""
    print("⚡ ТЕСТИРУЮ УЛЬТРА-БЫСТРУЮ LLM МОДЕЛЬ")
    print("=" * 60)
    
    test_questions = [
        "Что такое наценка?",
        "Как заказать доставку?",
        "Как пополнить баланс?",
        "Приложение не работает"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Вопрос {i}: {question}")
        
        result = ultra_fast_llm_client.get_hybrid_response(question)
        
        print(f"✅ Ответ: {result['answer']}")
        print(f"📊 Источник: {result['source']}")
        print(f"⏱️ Время: {result['processing_time']:.2f}с")
        print(f"🎯 Уверенность: {result['confidence']:.2f}")

if __name__ == "__main__":
    test_ultra_fast_llm()

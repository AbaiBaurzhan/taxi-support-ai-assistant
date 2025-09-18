import json
import logging
import requests
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, model_name: str = "llama2", use_ollama: bool = True):
        self.use_ollama = use_ollama
        self.model_name = model_name
        
        if use_ollama:
            # Проверяем переменные окружения для внешнего LLM
            self.llm_url = os.getenv("LLM_URL", "http://localhost:11434")
            self.ollama_url = f"{self.llm_url}/api/generate"
            self.llm_enabled = os.getenv("LLM_ENABLED", "true").lower() == "true"
            
            if not self.llm_enabled:
                logger.warning("LLM отключен через переменную окружения")
                self.use_ollama = False
        else:
            # Fallback to simple responses without heavy ML libraries
            logger.warning("Heavy ML libraries not available, using fallback responses")

    def generate_response(self, prompt: str, max_length: int = 200) -> str:
        """Генерирует ответ от LLM модели"""
        try:
            if self.use_ollama:
                return self._generate_with_ollama(prompt, max_length)
            else:
                return self._generate_fallback(prompt)
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return "Извините, произошла ошибка при генерации ответа."

    def _generate_with_ollama(self, prompt: str, max_length: int) -> str:
        """Генерация через Ollama API"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": max_length
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "Не удалось получить ответ от модели.")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Ollama: {e}")
            return self._generate_fallback(prompt)

    def _generate_fallback(self, prompt: str) -> str:
        """Простой fallback без ML библиотек"""
        prompt_lower = prompt.lower()
        
        if "цена" in prompt_lower or "стоимость" in prompt_lower:
            return "Цена поездки рассчитывается на основе расстояния и времени. Базовый тариф 200 тенге + 50 тенге за км."
        elif "промокод" in prompt_lower:
            return "Промокод можно ввести при оформлении заказа в поле 'Промокод'."
        elif "отменить" in prompt_lower:
            return "Поездку можно отменить в течение 2 минут после заказа без штрафа."
        elif "водитель" in prompt_lower:
            return "Вы можете связаться с водителем через приложение или позвонить по номеру в деталях поездки."
        else:
            return "Спасибо за обращение! Если у вас есть конкретный вопрос, я помогу найти ответ."

    def create_taxi_context_prompt(self, user_message: str, intent: str, locale: str) -> str:
        """Создает контекстный промпт для такси-сервиса"""
        
        system_prompt = f"""Ты - ИИ-ассистент службы поддержки такси-сервиса. 
Отвечай на языке: {locale}
Тип запроса: {intent}

Правила:
- Отвечай кратко и по делу
- Будь вежливым и профессиональным
- Если не знаешь ответа, предложи связаться с оператором
- Для жалоб всегда предлагай эскалацию к человеку
- Используй только русский, казахский или английский язык в зависимости от locale

Запрос пользователя: {user_message}

Ответ:"""

        return system_prompt

# Глобальный экземпляр клиента
llm_client = LLMClient()

import json
import logging
import requests
from typing import Dict, Any, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", use_ollama: bool = True):
        self.use_ollama = use_ollama
        self.model_name = model_name
        
        if use_ollama:
            self.ollama_url = "http://localhost:11434/api/generate"
            self.model_name = "llama2"  # или другая модель в Ollama
        else:
            # Используем transformers для локальной модели
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.model.to(self.device)
            
            # Добавляем pad_token если его нет
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_response(self, prompt: str, max_length: int = 200) -> str:
        """Генерирует ответ от LLM модели"""
        try:
            if self.use_ollama:
                return self._generate_with_ollama(prompt, max_length)
            else:
                return self._generate_with_transformers(prompt, max_length)
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
            return "Сервис временно недоступен. Попробуйте позже."

    def _generate_with_transformers(self, prompt: str, max_length: int) -> str:
        """Генерация через transformers"""
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Убираем исходный промпт из ответа
            response = response[len(prompt):].strip()
            
            return response if response else "Не удалось сгенерировать ответ."
            
        except Exception as e:
            logger.error(f"Ошибка генерации через transformers: {e}")
            return "Ошибка при работе с моделью."

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

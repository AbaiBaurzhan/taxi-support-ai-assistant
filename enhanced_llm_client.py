#!/usr/bin/env python3
"""
🧠 APARU Enhanced LLM Client
Интегрирует обученную базу знаний с LLM
"""

import json
import logging
import requests
import os
import pickle
from typing import Dict, Any, Optional, List
from knowledge_base_trainer import TaxiKnowledgeBase

logger = logging.getLogger(__name__)

class EnhancedLLMClient:
    def __init__(self, model_name: str = "llama2", use_ollama: bool = True):
        self.use_ollama = use_ollama
        self.model_name = model_name
        self.knowledge_base = None
        
        if use_ollama:
            # Проверяем переменные окружения для внешнего LLM
            self.llm_url = os.getenv("LLM_URL", "http://localhost:11434")
            self.ollama_url = f"{self.llm_url}/api/generate"
            self.llm_enabled = os.getenv("LLM_ENABLED", "true").lower() == "true"
            
            if not self.llm_enabled:
                logger.warning("LLM отключен через переменную окружения")
                self.use_ollama = False
        else:
            logger.warning("Heavy ML libraries not available, using fallback responses")
    
    def load_knowledge_base(self, index_path: str = "taxi_knowledge_index.pkl"):
        """Загружает обученную базу знаний"""
        try:
            self.knowledge_base = TaxiKnowledgeBase()
            self.knowledge_base.load_index(index_path)
            logger.info(f"База знаний загружена: {len(self.knowledge_base.knowledge_base)} записей")
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки базы знаний: {e}")
            return False
    
    def generate_response(self, prompt: str, max_length: int = 200) -> str:
        """Генерирует ответ от LLM модели с использованием базы знаний"""
        try:
            if self.use_ollama:
                return self._generate_with_knowledge_base(prompt, max_length)
            else:
                return self._generate_fallback(prompt)
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return "Извините, произошла ошибка при генерации ответа."
    
    def _generate_with_knowledge_base(self, prompt: str, max_length: int) -> str:
        """Генерация с использованием базы знаний"""
        try:
            # Если есть база знаний, ищем релевантную информацию
            if self.knowledge_base:
                # Извлекаем вопрос из промпта
                user_question = self._extract_question_from_prompt(prompt)
                
                # Ищем похожие записи в базе знаний
                similar_items = self.knowledge_base.search_similar(user_question, top_k=3)
                
                if similar_items and similar_items[0]['similarity_score'] > 0.7:
                    # Используем информацию из базы знаний
                    context = self._build_context_from_knowledge(similar_items)
                    enhanced_prompt = self._enhance_prompt_with_context(prompt, context)
                else:
                    enhanced_prompt = prompt
            else:
                enhanced_prompt = prompt
            
            # Отправляем запрос к LLM
            payload = {
                "model": self.model_name,
                "prompt": enhanced_prompt,
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
    
    def _extract_question_from_prompt(self, prompt: str) -> str:
        """Извлекает вопрос пользователя из промпта"""
        # Ищем строку "Запрос пользователя:"
        if "Запрос пользователя:" in prompt:
            return prompt.split("Запрос пользователя:")[-1].strip()
        return prompt
    
    def _build_context_from_knowledge(self, similar_items: List[Dict]) -> str:
        """Строит контекст из найденных записей базы знаний"""
        context_parts = []
        
        for item in similar_items:
            context_parts.append(f"Вопрос: {item['question']}")
            context_parts.append(f"Ответ: {item['answer']}")
            if item['keywords']:
                context_parts.append(f"Ключевые слова: {', '.join(item['keywords'])}")
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def _enhance_prompt_with_context(self, original_prompt: str, context: str) -> str:
        """Улучшает промпт с контекстом из базы знаний"""
        enhanced_prompt = f"""Ты - ИИ-ассистент службы поддержки такси-сервиса.

Используй следующую информацию из базы знаний для ответа:

{context}

Правила:
- Отвечай кратко и по делу
- Будь вежливым и профессиональным
- Используй информацию из базы знаний выше
- Если не знаешь ответа, предложи связаться с оператором
- Отвечай только на русском языке

{original_prompt}

Ответ:"""
        
        return enhanced_prompt
    
    def _generate_fallback(self, prompt: str) -> str:
        """Простой fallback без ML библиотек"""
        prompt_lower = prompt.lower()
        
        # Если есть база знаний, используем её для fallback
        if self.knowledge_base:
            user_question = self._extract_question_from_prompt(prompt)
            similar_items = self.knowledge_base.search_similar(user_question, top_k=1)
            
            if similar_items and similar_items[0]['similarity_score'] > 0.8:
                return similar_items[0]['answer']
        
        # Стандартные fallback ответы
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
        """Создает контекстный промпт для такси-сервиса с базой знаний"""
        
        # Если есть база знаний, ищем релевантную информацию
        context_info = ""
        if self.knowledge_base:
            similar_items = self.knowledge_base.search_similar(user_message, top_k=2)
            if similar_items and similar_items[0]['similarity_score'] > 0.6:
                context_info = f"\n\nРелевантная информация из базы знаний:\n"
                for item in similar_items:
                    context_info += f"Вопрос: {item['question']}\n"
                    context_info += f"Ответ: {item['answer']}\n\n"
        
        system_prompt = f"""Ты - ИИ-ассистент службы поддержки такси-сервиса. 
Отвечай на языке: {locale}
Тип запроса: {intent}
{context_info}
Правила:
- Отвечай кратко и по делу
- Будь вежливым и профессиональным
- Используй информацию из базы знаний выше
- Если не знаешь ответа, предложи связаться с оператором
- Для жалоб всегда предлагай эскалацию к человеку
- Используй только русский, казахский или английский язык в зависимости от locale

Запрос пользователя: {user_message}

Ответ:"""

        return system_prompt
    
    def get_knowledge_stats(self) -> Dict:
        """Возвращает статистику базы знаний"""
        if self.knowledge_base:
            return self.knowledge_base.get_statistics()
        return {"error": "База знаний не загружена"}

# Глобальный экземпляр клиента
enhanced_llm_client = EnhancedLLMClient()

def main():
    """Тестирование enhanced LLM client"""
    logging.basicConfig(level=logging.INFO)
    
    # Загружаем базу знаний
    if enhanced_llm_client.load_knowledge_base():
        print("✅ База знаний загружена")
        
        # Тестируем поиск
        test_questions = [
            "Где мой водитель?",
            "Как считается цена поездки?",
            "Можно ли отменить поездку?",
            "Как ввести промокод?"
        ]
        
        for question in test_questions:
            print(f"\n📝 Тест: {question}")
            
            # Создаем промпт
            prompt = enhanced_llm_client.create_taxi_context_prompt(question, "faq", "RU")
            
            # Генерируем ответ
            response = enhanced_llm_client.generate_response(prompt)
            print(f"✅ Ответ: {response[:100]}...")
            
            # Показываем статистику
            stats = enhanced_llm_client.get_knowledge_stats()
            print(f"📊 Статистика: {stats}")
    else:
        print("❌ Не удалось загрузить базу знаний")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🚀 ОПТИМИЗИРОВАННАЯ ПОИСКОВАЯ LLM СИСТЕМА APARU AI
Короткий промпт для быстрого поиска ответов
"""

import json
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedSearchLLMClient:
    def __init__(self):
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.model_name = "aparu-senior-ai"
        self.ollama_available = False
        
        # Загружаем базу знаний для поиска
        self.knowledge_base = self._load_knowledge_base()
        
        # Проверяем доступность Ollama
        self._check_ollama_model()
    
    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Загружает базу знаний для поиска ответов"""
        try:
            with open("senior_ai_knowledge_base.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"✅ Загружена база знаний: senior_ai_knowledge_base.json")
                return data
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            return []
    
    def _check_ollama_model(self):
        """Проверяет доступность Ollama и модели"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if any(m["name"].startswith(self.model_name) for m in models):
                    self.ollama_available = True
                    logger.info(f"✅ Ollama и модель '{self.model_name}' доступны")
                else:
                    logger.warning(f"⚠️ Модель '{self.model_name}' не найдена в Ollama")
            else:
                logger.warning(f"⚠️ Ollama недоступен: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к Ollama: {e}")
    
    def find_best_answer(self, question: str) -> Dict[str, Any]:
        """Находит лучший ответ из базы знаний"""
        start_time = datetime.now()
        
        # Используем LLM для поиска, а не генерации
        if self.ollama_available:
            try:
                logger.info("🔍 Используем LLM для поиска ответа...")
                result = self._llm_search_answer(question)
                if result:
                    processing_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ LLM поиск завершен за {processing_time:.2f}с")
                    return result
            except Exception as e:
                logger.error(f"❌ Ошибка LLM поиска: {e}")
        
        # Fallback к простому поиску
        logger.info("🔄 Fallback к простому поиску...")
        return self._simple_search(question)
    
    def _llm_search_answer(self, question: str) -> Dict[str, Any]:
        """Использует LLM для поиска ответа в базе знаний"""
        try:
            # КОРОТКИЙ ПРОМПТ для быстрого поиска
            search_prompt = f"""Найди ответ на вопрос: "{question}"

База FAQ:
1. Наценка - доплата за спрос
2. Доставка - курьерские услуги  
3. Баланс - пополнение счета
4. Приложение - технические проблемы
5. Тарифы - виды поездок

Ответь только номером (1-5):"""

            payload = {
                "model": self.model_name,
                "prompt": search_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.01,  # Минимальная температура
                    "num_predict": 3,      # Только номер
                    "num_ctx": 256,        # Короткий контекст
                    "repeat_penalty": 1.0,
                    "top_k": 1,            # Только лучший вариант
                    "top_p": 0.1,          # Минимальная вероятность
                    "stop": ["\n", ".", "!", "?", "Ответ:", "Категория:"]  # Ранние стоп-слова
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=8  # Короткий таймаут
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '').strip()
                
                # Парсим номер категории
                category_num = self._parse_category_number(answer)
                if category_num:
                    # Получаем ответ из базы знаний
                    if 1 <= category_num <= len(self.knowledge_base):
                        kb_item = self.knowledge_base[category_num - 1]
                        return {
                            "answer": kb_item.get("answer", "Ответ не найден"),
                            "category": kb_item.get("question", f"Категория {category_num}"),
                            "confidence": 0.95,
                            "source": "optimized_llm_search"
                        }
                
                logger.warning(f"⚠️ LLM вернул неожиданный ответ: {answer}")
                return None
            
            logger.warning(f"⚠️ LLM вернул ошибку: {response.status_code}")
            return None
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ LLM поиск таймаут (>8с)")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка LLM поиска: {e}")
            return None
    
    def _parse_category_number(self, answer: str) -> Optional[int]:
        """Парсим номер категории из ответа LLM"""
        try:
            # Ищем число в ответе
            import re
            numbers = re.findall(r'\d+', answer)
            if numbers:
                num = int(numbers[0])
                if 1 <= num <= len(self.knowledge_base):
                    return num
            return None
        except:
            return None
    
    def _simple_search(self, question: str) -> Dict[str, Any]:
        """Простой поиск по ключевым словам (fallback)"""
        question_lower = question.lower()
        
        # Поиск по ключевым словам
        for item in self.knowledge_base:
            keywords = item.get("keywords", [])
            variations = item.get("variations", [])
            answer = item.get("answer", "Ответ не найден")
            question_text = item.get("question", "")
            
            # Проверяем каждое ключевое слово
            for keyword in keywords:
                if keyword.lower() in question_lower:
                    return {
                        "answer": answer,
                        "category": question_text,
                        "confidence": 0.8,
                        "source": "simple_search"
                    }
            
            # Проверяем вариации
            for variation in variations:
                if variation.lower() in question_lower:
                    return {
                        "answer": answer,
                        "category": question_text,
                        "confidence": 0.8,
                        "source": "simple_search"
                    }
        
        # Fallback
        return {
            "answer": "Извините, не могу найти ответ на ваш вопрос. Обратитесь в службу поддержки.",
            "category": "unknown",
            "confidence": 0.0,
            "source": "fallback"
        }

# Тестирование
if __name__ == "__main__":
    client = OptimizedSearchLLMClient()
    
    test_questions = [
        "Что такое наценка?",
        "Как заказать доставку?",
        "Как пополнить баланс?",
        "Что такое тариф комфорта?"
    ]
    
    print("🚀 ТЕСТИРОВАНИЕ ОПТИМИЗИРОВАННОЙ ПОИСКОВОЙ LLM СИСТЕМЫ:")
    print("=" * 60)
    
    for question in test_questions:
        print(f"\n❓ Вопрос: {question}")
        result = client.find_best_answer(question)
        print(f"✅ Ответ: {result['answer'][:100]}...")
        print(f"📊 Категория: {result['category']}")
        print(f"🎯 Уверенность: {result['confidence']}")
        print(f"🔧 Источник: {result['source']}")
        print("-" * 40)

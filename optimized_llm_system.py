#!/usr/bin/env python3
"""
🚀 УЛУЧШЕННАЯ ПОИСКОВАЯ LLM СИСТЕМА APARU AI
Реализует все рекомендации для улучшения LLM поиска
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
                logger.info("🔍 Используем улучшенный LLM для поиска ответа...")
                result = self._optimized_llm_search_answer(question)
                if result:
                    processing_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ LLM поиск завершен за {processing_time:.2f}с")
                    return result
            except Exception as e:
                logger.error(f"❌ Ошибка LLM поиска: {e}")
        
        # Fallback к улучшенному простому поиску
        logger.info("🔄 Fallback к улучшенному простому поиску...")
        return self._enhanced_simple_search(question)
    
    def _optimized_llm_search_answer(self, question: str) -> Dict[str, Any]:
        """Использует улучшенный LLM для поиска ответа в базе знаний"""
        try:
            # УЛУЧШЕННЫЙ ПРОМПТ С ПРИМЕРАМИ
            search_prompt = f"""Найди категорию для вопроса: "{question}"

Категории APARU:
1. НАЦЕНКА - доплата, дорого, повышение цены
2. ДОСТАВКА - курьер, посылка, отправка
3. БАЛАНС - пополнение, оплата, платеж
4. ПРИЛОЖЕНИЕ - ошибка, не работает, глючит
5. ТАРИФЫ - комфорт, эконом, виды поездок

Примеры:
Вопрос: "Что такое наценка?" → Ответ: 1
Вопрос: "Как заказать доставку?" → Ответ: 2
Вопрос: "Пополнить баланс" → Ответ: 3
Вопрос: "Приложение не работает" → Ответ: 4
Вопрос: "Тариф комфорт" → Ответ: 5

Твой ответ (только номер 1-5):"""

            payload = {
                "model": self.model_name,
                "prompt": search_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.01,  # Минимальная температура для точности
                    "num_predict": 3,      # Только номер
                    "num_ctx": 512,        # Достаточный контекст
                    "repeat_penalty": 1.0,
                    "top_k": 1,            # Только лучший вариант
                    "top_p": 0.1,          # Минимальная вероятность
                    "stop": ["\n", ".", "!", "?", "Ответ:", "Категория:", "Объяснение:", "Потому что"]  # Ранние стоп-слова
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=12  # Оптимизированный таймаут
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
            logger.error(f"❌ LLM поиск таймаут (>12с)")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка LLM поиска: {e}")
            return None
    
    def _parse_category_number(self, answer: str) -> Optional[int]:
        """Парсит номер категории из ответа LLM"""
        try:
            # Ищем число в ответе
            import re
            numbers = re.findall(r'\d+', answer)
            if numbers:
                num = int(numbers[0])
                if 1 <= num <= 5:
                    return num
            return None
        except:
            return None
    
    def _enhanced_simple_search(self, question: str) -> Dict[str, Any]:
        """Улучшенный простой поиск по ключевым словам и синонимам"""
        question_lower = question.lower()
        
        # РАСШИРЕННАЯ БАЗА ЗНАНИЙ С СИНОНИМАМИ
        enhanced_kb = {
            "pricing": {
                "keywords": [
                    "наценка", "дорого", "подорожание", "повышение", "доплата", 
                    "цена", "стоимость", "тариф", "расценка", "коэффициент",
                    "спрос", "погода", "надбавка", "дополнительно", "больше"
                ],
                "variations": [
                    "что такое наценка", "почему дорого", "откуда доплата",
                    "повышающий коэффициент", "надбавка к цене", "зачем наценка",
                    "почему стоимость выше", "дополнительная оплата", "коэффициент спроса"
                ]
            },
            "delivery": {
                "keywords": [
                    "доставка", "курьер", "посылка", "отправить", "заказать", 
                    "заказ", "курьерская", "привезти", "принести", "отправить",
                    "получить", "доставить", "передать", "приехать"
                ],
                "variations": [
                    "как заказать доставку", "курьер не приехал", "посылка не пришла",
                    "отправить документы", "заказать курьера", "доставить товар"
                ]
            },
            "balance": {
                "keywords": [
                    "баланс", "счет", "кошелек", "пополнить", "платеж", 
                    "деньги", "оплата", "пополнение", "зачислить", "списать",
                    "деньги", "рубли", "тенге", "валюта", "финансы"
                ],
                "variations": [
                    "как пополнить баланс", "не могу оплатить", "пополнить счет",
                    "зачислить деньги", "списать средства", "пополнение кошелька"
                ]
            },
            "app": {
                "keywords": [
                    "приложение", "программа", "софт", "апп", "работать", 
                    "не работает", "ошибка", "глючит", "зависает", "тормозит",
                    "сбой", "проблема", "техническая", "баг", "крэш"
                ],
                "variations": [
                    "приложение не работает", "ошибка в приложении", "приложение глючит",
                    "программа зависает", "техническая проблема", "сбой в системе"
                ]
            },
            "tariffs": {
                "keywords": [
                    "тариф", "комфорт", "эконом", "бизнес", "поездка", 
                    "вид", "тип", "класс", "уровень", "категория",
                    "отличается", "разница", "сравнение", "выбор"
                ],
                "variations": [
                    "что такое тариф комфорт", "чем отличается комфорт", "что входит в тариф",
                    "какой тариф выбрать", "разница между тарифами", "сравнение тарифов"
                ]
            }
        }
        
        # УЛУЧШЕННЫЙ ПОИСК ПО КЛЮЧЕВЫМ СЛОВАМ И СИНОНИМАМ
        for category, data in enhanced_kb.items():
            keywords = data["keywords"]
            variations = data["variations"]
            
            # Проверяем каждое ключевое слово
            for keyword in keywords:
                if keyword.lower() in question_lower:
                    # Находим соответствующий ответ в базе знаний
                    answer = self._get_answer_by_category(category)
                    return {
                        "answer": answer,
                        "category": category,
                        "confidence": 0.9,
                        "source": "enhanced_simple_search"
                    }
            
            # Проверяем вариации
            for variation in variations:
                if variation.lower() in question_lower:
                    answer = self._get_answer_by_category(category)
                    return {
                        "answer": answer,
                        "category": category,
                        "confidence": 0.9,
                        "source": "enhanced_simple_search"
                    }
        
        # Fallback
        return {
            "answer": "Извините, не могу найти ответ на ваш вопрос. Обратитесь в службу поддержки.",
            "category": "unknown",
            "confidence": 0.0,
            "source": "fallback"
        }
    
    def _get_answer_by_category(self, category: str) -> str:
        """Получает ответ по категории из базы знаний"""
        category_mapping = {
            "pricing": 0,      # Наценка
            "delivery": 1,     # Доставка
            "balance": 2,      # Баланс
            "app": 3,          # Приложение
            "tariffs": 4       # Тарифы
        }
        
        index = category_mapping.get(category, 0)
        if 0 <= index < len(self.knowledge_base):
            return self.knowledge_base[index].get("answer", "Ответ не найден")
        
        return "Ответ не найден"

# Тестирование
if __name__ == "__main__":
    client = OptimizedSearchLLMClient()
    
    test_questions = [
        "Что такое наценка?",
        "Как заказать доставку?",
        "Как пополнить баланс?",
        "Приложение не работает",
        "Что такое тариф комфорт?",
        "Почему дорого?",
        "Курьер не приехал",
        "Не могу оплатить",
        "Ошибка в приложении",
        "Чем отличается комфорт?"
    ]
    
    print("🚀 ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ LLM СИСТЕМЫ:")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"{i:2d}. {question}")
        result = client.find_best_answer(question)
        print(f"    ✅ Ответ: {result['answer'][:100]}...")
        print(f"    📊 Категория: {result['category']}")
        print(f"    🎯 Уверенность: {result['confidence']}")
        print(f"    🔧 Источник: {result['source']}")
        print("-" * 40)

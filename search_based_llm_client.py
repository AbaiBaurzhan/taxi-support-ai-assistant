#!/usr/bin/env python3
"""
🔍 ПОИСКОВАЯ LLM СИСТЕМА APARU AI
LLM работает как поисковая система - находит готовые ответы из базы
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

class SearchBasedLLMClient:
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
            # Пытаемся загрузить из разных файлов
            knowledge_files = [
                "senior_ai_knowledge_base.json",
                "enhanced_aparu_knowledge_base.json", 
                "aparu_knowledge_base.json",
                "kb.json"
            ]
            
            for file_path in knowledge_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        logger.info(f"✅ Загружена база знаний: {file_path}")
                        
                        # Если это список, возвращаем как есть
                        if isinstance(data, list):
                            return data
                        # Если это словарь, конвертируем в список
                        elif isinstance(data, dict):
                            return list(data.values())
                        else:
                            logger.warning(f"⚠️ Неожиданный формат базы знаний: {type(data)}")
                            continue
                            
                except FileNotFoundError:
                    continue
            
            # Fallback - простая база знаний в формате списка
            logger.warning("⚠️ Не найдена база знаний, используем fallback")
            return [
                {
                    "id": 1,
                    "question": "Что такое наценка?",
                    "answer": "Наценка - это дополнительная плата за повышенный спрос. Она помогает привлечь больше водителей и сократить время ожидания.",
                    "variations": ["наценка", "дорого", "подорожание", "повышение", "доплата"],
                    "keywords": ["наценка", "дорого", "подорожание", "повышение", "доплата"]
                },
                {
                    "id": 2,
                    "question": "Как заказать доставку?",
                    "answer": "Для заказа доставки: откройте приложение → выберите 'Доставка' → укажите адреса → подтвердите заказ.",
                    "variations": ["доставка", "курьер", "посылка", "отправить", "заказать"],
                    "keywords": ["доставка", "курьер", "посылка", "отправить", "заказать"]
                },
                {
                    "id": 3,
                    "question": "Как пополнить баланс?",
                    "answer": "Для пополнения баланса: откройте приложение → 'Профиль' → 'Пополнить баланс' → выберите способ оплаты.",
                    "variations": ["баланс", "счет", "кошелек", "пополнить", "платеж"],
                    "keywords": ["баланс", "счет", "кошелек", "пополнить", "платеж"]
                }
            ]
            
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
            # Создаем промпт для поиска, а не генерации
            search_prompt = f"""Ты — поисковая система для FAQ APARU. Твоя задача — найти подходящий ответ из базы знаний.

ВОПРОС ПОЛЬЗОВАТЕЛЯ: {question}

БАЗА ЗНАНИЙ:
{self._format_knowledge_base()}

ИНСТРУКЦИИ:
1. Проанализируй вопрос пользователя
2. Найди наиболее подходящий ответ из базы знаний
3. Верни ТОЛЬКО номер категории (например: "1", "2", "3")
4. НЕ генерируй новый текст
5. НЕ объясняй свой выбор

ОТВЕТ (только номер категории):"""

            payload = {
                "model": self.model_name,
                "prompt": search_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.01,  # Минимальная температура для точности
                    "num_predict": 5,     # Только номер категории
                    "num_ctx": 512,       # Достаточно для базы знаний
                    "repeat_penalty": 1.0,
                    "top_k": 1,           # Только лучший вариант
                    "top_p": 0.1,         # Минимальная вероятность
                    "stop": ["\n", ".", "!", "?", "Ответ:", "Категория:"]  # Ранние стоп-слова
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=10  # Короткий таймаут для поиска
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
                            "source": "llm_search"
                        }
                
                logger.warning(f"⚠️ LLM вернул неожиданный ответ: {answer}")
                return None
            
            logger.warning(f"⚠️ LLM вернул ошибку: {response.status_code}")
            return None
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ LLM поиск таймаут (>10с)")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка LLM поиска: {e}")
            return None
    
    def _format_knowledge_base(self) -> str:
        """Форматирует базу знаний для LLM"""
        formatted = ""
        for i, item in enumerate(self.knowledge_base, 1):
            question = item.get("question", f"Вопрос {i}")
            answer = item.get("answer", "Ответ не найден")
            keywords = item.get("keywords", [])
            variations = item.get("variations", [])
            
            formatted += f"{i}. ВОПРОС: {question}\n"
            formatted += f"   ОТВЕТ: {answer}\n"
            formatted += f"   КЛЮЧЕВЫЕ СЛОВА: {', '.join(keywords)}\n"
            formatted += f"   ВАРИАЦИИ: {', '.join(variations[:5])}\n\n"
        
        return formatted
    
    def _parse_category_number(self, answer: str) -> Optional[int]:
        """Парсит номер категории из ответа LLM"""
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
    client = SearchBasedLLMClient()
    
    test_questions = [
        "Что такое наценка?",
        "Как заказать доставку?",
        "Как пополнить баланс?",
        "Что такое тариф комфорта?"
    ]
    
    print("🔍 ТЕСТИРОВАНИЕ ПОИСКОВОЙ LLM СИСТЕМЫ:")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\n❓ Вопрос: {question}")
        result = client.find_best_answer(question)
        print(f"✅ Ответ: {result['answer']}")
        print(f"📊 Категория: {result['category']}")
        print(f"🎯 Уверенность: {result['confidence']}")
        print(f"🔧 Источник: {result['source']}")
        print("-" * 30)

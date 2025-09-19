#!/usr/bin/env python3
"""
🚀 УЛУЧШЕННЫЙ ТЕСТ LLM С ИСПРАВЛЕНИЯМИ
Исправляет проблемы с промптом и категоризацией
"""

import json
import time
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

class ImprovedLLMTest:
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.test_results = []
        self.llm_available = False
        
        # Проверяем доступность LLM
        self._check_llm_availability()
    
    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Загружает базу знаний"""
        try:
            with open("senior_ai_knowledge_base.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✅ Загружена база знаний: {len(data)} вопросов")
                return data
        except Exception as e:
            print(f"❌ Ошибка загрузки базы знаний: {e}")
            return []
    
    def _check_llm_availability(self):
        """Проверяет доступность LLM"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if any(m["name"].startswith("aparu-senior-ai") for m in models):
                    self.llm_available = True
                    print("✅ LLM модель доступна")
                else:
                    print("⚠️ LLM модель не найдена")
            else:
                print("⚠️ Ollama недоступен")
        except Exception as e:
            print(f"⚠️ Не удалось подключиться к Ollama: {e}")
    
    def test_improved_llm_search(self, question: str, expected_category: str) -> Dict[str, Any]:
        """Тестирует улучшенный LLM поиск"""
        start_time = time.time()
        
        try:
            # УЛУЧШЕННЫЙ ПРОМПТ
            search_prompt = f"""Ты — AI-ассистент службы поддержки такси APARU. Твоя задача — найти подходящий ответ из базы знаний.

ВОПРОС ПОЛЬЗОВАТЕЛЯ: "{question}"

БАЗА ЗНАНИЙ APARU:
1. НАЦЕНКА (pricing) - доплата за повышенный спрос, погодные условия
2. ДОСТАВКА (delivery) - курьерские услуги, посылки, отправка
3. БАЛАНС (balance) - пополнение счета, платежи, кошелек
4. ПРИЛОЖЕНИЕ (app) - технические проблемы, ошибки, глючи
5. ТАРИФЫ (tariffs) - виды поездок, комфорт, эконом

ИНСТРУКЦИИ:
- Проанализируй вопрос пользователя
- Найди наиболее подходящую категорию из базы
- Верни ТОЛЬКО номер категории (1, 2, 3, 4 или 5)
- НЕ генерируй новый текст
- НЕ объясняй свой выбор

ОТВЕТ (только номер):"""

            payload = {
                "model": "aparu-senior-ai",
                "prompt": search_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.01,  # Минимальная температура
                    "num_predict": 5,      # Только номер
                    "num_ctx": 512,        # Увеличенный контекст
                    "repeat_penalty": 1.0,
                    "top_k": 1,            # Только лучший вариант
                    "top_p": 0.1,          # Минимальная вероятность
                    "stop": ["\n", ".", "!", "?", "Ответ:", "Категория:", "Объяснение:"]  # Ранние стоп-слова
                }
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=15  # Увеличенный таймаут
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '').strip()
                
                # Парсим номер категории
                category_num = self._parse_category_number(answer)
                
                return {
                    "question": question,
                    "expected_category": expected_category,
                    "llm_response": answer,
                    "parsed_category": category_num,
                    "processing_time": processing_time,
                    "success": category_num is not None,
                    "correct": self._is_correct_category(category_num, expected_category)
                }
            else:
                return {
                    "question": question,
                    "expected_category": expected_category,
                    "llm_response": f"Ошибка: {response.status_code}",
                    "parsed_category": None,
                    "processing_time": processing_time,
                    "success": False,
                    "correct": False
                }
                
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "question": question,
                "expected_category": expected_category,
                "llm_response": f"Ошибка: {e}",
                "parsed_category": None,
                "processing_time": processing_time,
                "success": False,
                "correct": False
            }
    
    def _parse_category_number(self, answer: str) -> Optional[int]:
        """Парсит номер категории из ответа LLM"""
        try:
            import re
            numbers = re.findall(r'\d+', answer)
            if numbers:
                num = int(numbers[0])
                if 1 <= num <= 5:
                    return num
            return None
        except:
            return None
    
    def _is_correct_category(self, category_num: Optional[int], expected_category: str) -> bool:
        """Проверяет правильность категории"""
        if category_num is None:
            return False
        
        # УЛУЧШЕННЫЙ МАППИНГ КАТЕГОРИЙ
        category_mapping = {
            "pricing": 1,      # Наценка
            "delivery": 2,     # Доставка
            "balance": 3,      # Баланс
            "app": 4,          # Приложение
            "tariffs": 5,      # Тарифы
            "general": 1       # Общие вопросы → Наценка (по умолчанию)
        }
        
        expected_num = category_mapping.get(expected_category, 1)
        return category_num == expected_num
    
    def test_simple_search(self, question: str, expected_category: str) -> Dict[str, Any]:
        """Тестирует простой поиск (fallback)"""
        start_time = time.time()
        
        question_lower = question.lower()
        
        # Поиск по ключевым словам
        for item in self.knowledge_base:
            keywords = item.get("keywords", [])
            variations = item.get("variations", [])
            answer = item.get("answer", "Ответ не найден")
            question_text = item.get("question", "")
            category = item.get("category", "unknown")
            
            # Проверяем каждое ключевое слово
            for keyword in keywords:
                if keyword.lower() in question_lower:
                    processing_time = time.time() - start_time
                    return {
                        "question": question,
                        "expected_category": expected_category,
                        "simple_response": answer[:100] + "...",
                        "found_category": category,
                        "processing_time": processing_time,
                        "success": True,
                        "correct": category == expected_category
                    }
            
            # Проверяем вариации
            for variation in variations:
                if variation.lower() in question_lower:
                    processing_time = time.time() - start_time
                    return {
                        "question": question,
                        "expected_category": expected_category,
                        "simple_response": answer[:100] + "...",
                        "found_category": category,
                        "processing_time": processing_time,
                        "success": True,
                        "correct": category == expected_category
                    }
        
        processing_time = time.time() - start_time
        return {
            "question": question,
            "expected_category": expected_category,
            "simple_response": "Ответ не найден",
            "found_category": "unknown",
            "processing_time": processing_time,
            "success": False,
            "correct": False
        }
    
    def run_improved_test(self):
        """Запускает улучшенный тест"""
        print("🚀 УЛУЧШЕННЫЙ ТЕСТ LLM С ИСПРАВЛЕНИЯМИ")
        print("=" * 50)
        
        # Создаем тестовые вопросы
        test_questions = [
            {"question": "Что такое наценка?", "category": "pricing"},
            {"question": "Как заказать доставку?", "category": "delivery"},
            {"question": "Как пополнить баланс?", "category": "balance"},
            {"question": "Приложение не работает", "category": "app"},
            {"question": "Что такое тариф комфорт?", "category": "tariffs"},
            {"question": "Почему дорого?", "category": "pricing"},
            {"question": "Курьер не приехал", "category": "delivery"},
            {"question": "Не могу оплатить", "category": "balance"},
            {"question": "Ошибка в приложении", "category": "app"},
            {"question": "Чем отличается комфорт?", "category": "tariffs"}
        ]
        
        print(f"📊 Тестовых вопросов: {len(test_questions)}")
        print(f"🧠 LLM доступна: {'Да' if self.llm_available else 'Нет'}")
        print()
        
        # Тестируем улучшенный LLM
        if self.llm_available:
            print("🔍 ТЕСТИРОВАНИЕ УЛУЧШЕННОГО LLM ПОИСКА:")
            print("-" * 45)
            
            llm_results = []
            for i, test_item in enumerate(test_questions, 1):
                print(f"{i:2d}. {test_item['question']}")
                
                result = self.test_improved_llm_search(test_item['question'], test_item['category'])
                llm_results.append(result)
                
                status = "✅" if result['correct'] else "❌"
                print(f"    {status} Ответ: '{result['llm_response']}' | Категория: {result['parsed_category']} | Время: {result['processing_time']:.2f}с")
                print()
            
            # Статистика LLM
            llm_success = sum(1 for r in llm_results if r['success'])
            llm_correct = sum(1 for r in llm_results if r['correct'])
            llm_avg_time = sum(r['processing_time'] for r in llm_results) / len(llm_results)
            
            print(f"📊 СТАТИСТИКА УЛУЧШЕННОГО LLM:")
            print(f"   Успешных ответов: {llm_success}/{len(llm_results)} ({llm_success/len(llm_results)*100:.1f}%)")
            print(f"   Правильных ответов: {llm_correct}/{len(llm_results)} ({llm_correct/len(llm_results)*100:.1f}%)")
            print(f"   Среднее время: {llm_avg_time:.2f}с")
            print()
        
        # Тестируем простой поиск
        print("🔍 ТЕСТИРОВАНИЕ ПРОСТОГО ПОИСКА:")
        print("-" * 40)
        
        simple_results = []
        for i, test_item in enumerate(test_questions, 1):
            print(f"{i:2d}. {test_item['question']}")
            
            result = self.test_simple_search(test_item['question'], test_item['category'])
            simple_results.append(result)
            
            status = "✅" if result['correct'] else "❌"
            print(f"    {status} Категория: {result['found_category']} | Время: {result['processing_time']:.3f}с")
            print()
        
        # Статистика простого поиска
        simple_success = sum(1 for r in simple_results if r['success'])
        simple_correct = sum(1 for r in simple_results if r['correct'])
        simple_avg_time = sum(r['processing_time'] for r in simple_results) / len(simple_results)
        
        print(f"📊 СТАТИСТИКА ПРОСТОГО ПОИСКА:")
        print(f"   Успешных ответов: {simple_success}/{len(simple_results)} ({simple_success/len(simple_results)*100:.1f}%)")
        print(f"   Правильных ответов: {simple_correct}/{len(simple_results)} ({simple_correct/len(simple_results)*100:.1f}%)")
        print(f"   Среднее время: {simple_avg_time:.3f}с")
        print()
        
        # Общая статистика
        print("📊 ОБЩАЯ СТАТИСТИКА:")
        print("=" * 30)
        
        if self.llm_available:
            print(f"🧠 Улучшенный LLM поиск:")
            print(f"   Успешность: {llm_success/len(llm_results)*100:.1f}%")
            print(f"   Точность: {llm_correct/len(llm_results)*100:.1f}%")
            print(f"   Скорость: {llm_avg_time:.2f}с")
            print()
        
        print(f"🔍 Простой поиск:")
        print(f"   Успешность: {simple_success/len(simple_results)*100:.1f}%")
        print(f"   Точность: {simple_correct/len(simple_results)*100:.1f}%")
        print(f"   Скорость: {simple_avg_time:.3f}с")
        print()
        
        # Рекомендации
        print("💡 РЕКОМЕНДАЦИИ:")
        print("-" * 20)
        
        if self.llm_available:
            if llm_correct/len(llm_results) < 0.8:
                print("⚠️ LLM поиск все еще требует улучшения:")
                print("   - Промпт может быть слишком сложным")
                print("   - Нужно упростить инструкции")
                print("   - Добавить больше примеров")
            else:
                print("✅ LLM поиск работает хорошо!")
        
        if simple_correct/len(simple_results) < 0.9:
            print("⚠️ Простой поиск требует улучшения")
        else:
            print("✅ Простой поиск работает отлично!")
        
        print()
        print("🎯 УЛУЧШЕННЫЙ ТЕСТ ЗАВЕРШЕН!")

if __name__ == "__main__":
    test = ImprovedLLMTest()
    test.run_improved_test()

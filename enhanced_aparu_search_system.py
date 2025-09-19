#!/usr/bin/env python3
"""
🔍 Улучшенная система поиска APARU
Использует новую базу знаний с вариациями вопросов и ключевыми словами
"""

import json
import logging
import pickle
from typing import Dict, List, Any, Optional
from fuzzywuzzy import fuzz
import re

logger = logging.getLogger(__name__)

class EnhancedAPARUSearch:
    def __init__(self, knowledge_base_path: str = "enhanced_aparu_knowledge_base.json", 
                 index_path: str = "enhanced_search_index.pkl"):
        self.knowledge_base_path = knowledge_base_path
        self.index_path = index_path
        self.knowledge_base = []
        self.keyword_index = {}
        self.question_index = {}
        
        self._load_knowledge_base()
        self._load_search_index()
    
    def _load_knowledge_base(self):
        """Загружает базу знаний"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            logger.info(f"✅ База знаний загружена: {len(self.knowledge_base)} записей")
        except FileNotFoundError:
            logger.error(f"❌ База знаний не найдена: {self.knowledge_base_path}")
            self.knowledge_base = []
    
    def _load_search_index(self):
        """Загружает поисковый индекс"""
        try:
            with open(self.index_path, 'rb') as f:
                index_data = pickle.load(f)
                self.keyword_index = index_data.get('keyword_index', {})
                self.question_index = index_data.get('question_index', {})
            logger.info(f"✅ Поисковый индекс загружен: {len(self.keyword_index)} ключевых слов")
        except FileNotFoundError:
            logger.error(f"❌ Поисковый индекс не найден: {self.index_path}")
            self.keyword_index = {}
            self.question_index = {}
    
    def search_by_keywords(self, question: str, threshold: float = 0.3) -> Optional[Dict[str, Any]]:
        """Поиск по ключевым словам"""
        question_lower = question.lower()
        best_match = None
        best_score = 0
        
        # Ищем совпадения по ключевым словам
        for keyword, indices in self.keyword_index.items():
            if keyword.lower() in question_lower:
                for idx in indices:
                    if idx < len(self.knowledge_base):
                        item = self.knowledge_base[idx]
                        score = fuzz.ratio(question_lower, keyword.lower()) + 20
                        if score > best_score:
                            best_score = score
                            best_match = item
        
        if best_score / 100.0 >= threshold:
            return best_match
        return None
    
    def search_by_question(self, question: str, threshold: float = 0.4) -> Optional[Dict[str, Any]]:
        """Поиск по точному совпадению вопроса"""
        question_lower = question.lower()
        
        # Проверяем точное совпадение
        if question_lower in self.question_index:
            idx = self.question_index[question_lower]
            if idx < len(self.knowledge_base):
                return self.knowledge_base[idx]
        
        # Проверяем нечеткое совпадение
        best_match = None
        best_score = 0
        
        for item in self.knowledge_base:
            # Проверяем основной вопрос
            score = fuzz.ratio(question_lower, item['question'].lower())
            if score > best_score:
                best_score = score
                best_match = item
            
            # Проверяем вариации
            for variation in item.get('variations', []):
                score = fuzz.ratio(question_lower, variation.lower())
                if score > best_score:
                    best_score = score
                    best_match = item
        
        if best_score / 100.0 >= threshold:
            return best_match
        return None
    
    def search_by_category(self, question: str, category: str) -> Optional[Dict[str, Any]]:
        """Поиск в определенной категории"""
        category_items = [item for item in self.knowledge_base if item.get('category') == category]
        
        if not category_items:
            return None
        
        question_lower = question.lower()
        best_match = None
        best_score = 0
        
        for item in category_items:
            # Проверяем основной вопрос
            score = fuzz.ratio(question_lower, item['question'].lower())
            if score > best_score:
                best_score = score
                best_match = item
            
            # Проверяем вариации
            for variation in item.get('variations', []):
                score = fuzz.ratio(question_lower, variation.lower())
                if score > best_score:
                    best_score = score
                    best_match = item
            
            # Проверяем ключевые слова
            for keyword in item.get('keywords', []):
                if keyword.lower() in question_lower:
                    score = fuzz.ratio(question_lower, keyword.lower()) + 30
                    if score > best_score:
                        best_score = score
                        best_match = item
        
        return best_match
    
    def get_enhanced_answer(self, question: str, threshold: float = 0.3) -> Dict[str, Any]:
        """
        Получает улучшенный ответ с использованием всех методов поиска
        """
        question_lower = question.lower()
        
        # 1. Определяем категорию вопроса
        category = self._categorize_question(question_lower)
        
        # 2. Пробуем поиск по точному совпадению
        result = self.search_by_question(question, threshold=0.6)
        if result:
            return {
                'answer': result['answer'],
                'confidence': 0.95,
                'source': 'exact_match',
                'category': category,
                'keywords': result.get('keywords', []),
                'variations': result.get('variations', [])
            }
        
        # 3. Пробуем поиск по ключевым словам
        result = self.search_by_keywords(question, threshold=0.4)
        if result:
            return {
                'answer': result['answer'],
                'confidence': 0.85,
                'source': 'keyword_match',
                'category': category,
                'keywords': result.get('keywords', []),
                'variations': result.get('variations', [])
            }
        
        # 4. Пробуем поиск в категории
        result = self.search_by_category(question, category)
        if result:
            return {
                'answer': result['answer'],
                'confidence': 0.75,
                'source': 'category_match',
                'category': category,
                'keywords': result.get('keywords', []),
                'variations': result.get('variations', [])
            }
        
        # 5. Общий поиск
        result = self.search_by_question(question, threshold=threshold)
        if result:
            return {
                'answer': result['answer'],
                'confidence': 0.65,
                'source': 'fuzzy_match',
                'category': category,
                'keywords': result.get('keywords', []),
                'variations': result.get('variations', [])
            }
        
        # 6. Fallback
        return {
            'answer': "Извините, я не нашел подходящего ответа в базе знаний. Обратитесь к оператору поддержки.",
            'confidence': 0.0,
            'source': 'fallback',
            'category': category,
            'keywords': [],
            'variations': []
        }
    
    def _categorize_question(self, question: str) -> str:
        """Категоризирует вопрос"""
        if any(word in question for word in ['наценка', 'цена', 'стоимость', 'расценка', 'дорого', 'дешево']):
            return 'pricing'
        elif any(word in question for word in ['заказ', 'поездка', 'такси', 'вызов', 'предварительный']):
            return 'booking'
        elif any(word in question for word in ['баланс', 'пополнить', 'оплата', 'платеж', 'карта']):
            return 'payment'
        elif any(word in question for word in ['приложение', 'таксометр', 'моточасы', 'gps', 'не работает']):
            return 'technical'
        elif any(word in question for word in ['доставка', 'курьер', 'посылка']):
            return 'delivery'
        elif any(word in question for word in ['водитель', 'контакты', 'связь', 'принимать заказы']):
            return 'driver'
        elif any(word in question for word in ['отменить', 'отмена', 'отказ']):
            return 'cancellation'
        elif any(word in question for word in ['жалоба', 'проблема', 'недоволен']):
            return 'complaint'
        else:
            return 'general'
    
    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику базы знаний"""
        categories = {}
        total_variations = 0
        total_keywords = 0
        
        for item in self.knowledge_base:
            cat = item.get('category', 'general')
            categories[cat] = categories.get(cat, 0) + 1
            total_variations += len(item.get('variations', []))
            total_keywords += len(item.get('keywords', []))
        
        return {
            'total_records': len(self.knowledge_base),
            'categories': categories,
            'total_variations': total_variations,
            'total_keywords': total_keywords,
            'avg_variations_per_record': total_variations / len(self.knowledge_base) if self.knowledge_base else 0,
            'avg_keywords_per_record': total_keywords / len(self.knowledge_base) if self.knowledge_base else 0
        }

# Глобальный экземпляр для использования в main.py
_enhanced_search = EnhancedAPARUSearch()

def get_enhanced_answer(question: str) -> str:
    """Получает улучшенный ответ"""
    result = _enhanced_search.get_enhanced_answer(question)
    return result['answer']

def get_enhanced_answer_with_metadata(question: str) -> Dict[str, Any]:
    """Получает улучшенный ответ с метаданными"""
    return _enhanced_search.get_enhanced_answer(question)

if __name__ == "__main__":
    # Тестируем систему поиска
    search = EnhancedAPARUSearch()
    
    # Показываем статистику
    stats = search.get_statistics()
    print(f"📊 Статистика базы знаний:")
    print(f"   Записей: {stats['total_records']}")
    print(f"   Вариаций: {stats['total_variations']}")
    print(f"   Ключевых слов: {stats['total_keywords']}")
    print(f"   Среднее вариаций на запись: {stats['avg_variations_per_record']:.1f}")
    print(f"   Среднее ключевых слов на запись: {stats['avg_keywords_per_record']:.1f}")
    
    print(f"\n📋 Категории:")
    for cat, count in stats['categories'].items():
        print(f"   {cat}: {count} записей")
    
    # Тестируем поиск
    test_questions = [
        "Что такое наценка?",
        "Почему так дорого?",
        "Что такое тариф Комфорт?",
        "Как пополнить баланс?"
    ]
    
    print(f"\n🧪 Тестирование поиска:")
    for question in test_questions:
        result = search.get_enhanced_answer(question)
        print(f"❓ {question}")
        print(f"✅ {result['answer'][:100]}...")
        print(f"📊 Уверенность: {result['confidence']:.2f}, Источник: {result['source']}")
        print()

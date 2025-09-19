#!/usr/bin/env python3
"""
🔍 Контекстно-осознанный поиск для APARU
Предотвращает смешивание ответов и улучшает понимание контекста
"""

import json
import logging
from typing import Dict, List, Any, Tuple
from fuzzywuzzy import fuzz
import re

logger = logging.getLogger(__name__)

class ContextAwareSearch:
    def __init__(self, knowledge_base_path: str = "enhanced_aparu_knowledge.json"):
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.context_patterns = self._build_context_patterns()
        
    def _load_knowledge_base(self, path: str) -> List[Dict]:
        """Загружает улучшенную базу знаний"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"База знаний не найдена: {path}")
            return []
    
    def _build_context_patterns(self) -> Dict[str, List[str]]:
        """Строит паттерны контекста"""
        return {
            'pricing': ['тариф', 'цена', 'стоимость', 'расценка', 'наценка', 'дорого', 'дешево'],
            'booking': ['заказ', 'поездка', 'такси', 'вызов', 'вызвать', 'заказать'],
            'payment': ['баланс', 'пополнить', 'оплата', 'платеж', 'карта', 'наличные'],
            'technical': ['приложение', 'таксометр', 'моточасы', 'gps', 'ошибка', 'не работает'],
            'delivery': ['доставка', 'курьер', 'посылка', 'отправить', 'передать'],
            'driver': ['водитель', 'таксист', 'контакты', 'связь', 'номер'],
            'cancellation': ['отменить', 'отмена', 'отказ', 'отменить заказ'],
            'complaint': ['жалоба', 'проблема', 'недоволен', 'плохо', 'грубо'],
            'general': ['что', 'как', 'где', 'когда', 'почему']
        }
    
    def get_contextual_answer(self, question: str, threshold: float = 0.4) -> Dict[str, Any]:
        """
        Получает контекстный ответ на вопрос
        Предотвращает смешивание ответов из разных категорий
        """
        question_lower = question.lower()
        
        # Определяем категорию вопроса
        question_category = self._categorize_question(question_lower)
        
        # Ищем ответы только в соответствующей категории
        category_items = [item for item in self.knowledge_base if item.get('category') == question_category]
        
        if not category_items:
            # Если категория не найдена, ищем во всех
            category_items = self.knowledge_base
        
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
            for keyword in item.get('context_keywords', []):
                if keyword.lower() in question_lower:
                    score = fuzz.ratio(question_lower, keyword.lower()) + 20
                    if score > best_score:
                        best_score = score
                        best_match = item
        
        # Нормализуем score
        normalized_score = best_score / 100.0
        
        if normalized_score >= threshold and best_match:
            return {
                'answer': best_match['answer'],
                'confidence': normalized_score,
                'source': 'knowledge_base',
                'category': question_category,
                'context_keywords': best_match.get('context_keywords', []),
                'prevented_mixing': True
            }
        else:
            return {
                'answer': "Извините, я не нашел подходящего ответа в базе знаний. Обратитесь к оператору поддержки.",
                'confidence': 0.0,
                'source': 'fallback',
                'category': question_category,
                'context_keywords': [],
                'prevented_mixing': True
            }
    
    def _categorize_question(self, question: str) -> str:
        """Категоризирует вопрос по контексту"""
        for category, keywords in self.context_patterns.items():
            if any(keyword in question for keyword in keywords):
                return category
        return 'general'
    
    def validate_answer_consistency(self, question: str, answer: str) -> bool:
        """Проверяет консистентность ответа"""
        question_category = self._categorize_question(question.lower())
        
        # Проверяем, что ответ соответствует категории вопроса
        if question_category == 'pricing' and not any(word in answer.lower() for word in ['тариф', 'цена', 'стоимость']):
            return False
        elif question_category == 'booking' and not any(word in answer.lower() for word in ['заказ', 'поездка', 'такси']):
            return False
        elif question_category == 'payment' and not any(word in answer.lower() for word in ['баланс', 'оплата', 'платеж']):
            return False
        
        return True

# Глобальный экземпляр для использования в main.py
_context_aware_search = ContextAwareSearch()

def get_contextual_answer(question: str) -> str:
    """Получает контекстный ответ"""
    result = _context_aware_search.get_contextual_answer(question)
    return result['answer']

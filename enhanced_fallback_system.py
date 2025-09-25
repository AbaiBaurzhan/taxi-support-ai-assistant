#!/usr/bin/env python3
"""
🔧 УЛУЧШЕННАЯ FALLBACK СИСТЕМА С МОРФОЛОГИЕЙ
"""

import json
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EnhancedFallbackSystem:
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.morphological_forms = self._create_morphological_forms()
        
    def _load_knowledge_base(self):
        """Загружает базу знаний"""
        try:
            with open('BZ.txt', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            return []
    
    def _create_morphological_forms(self):
        """Создает словарь морфологических форм"""
        return {
            # Наценка
            "наценка": ["наценка", "наценки", "наценку", "наценкой", "наценке", "наценках"],
            "доплата": ["доплата", "доплаты", "доплату", "доплатой", "доплате", "доплатах"],
            "надбавка": ["надбавка", "надбавки", "надбавку", "надбавкой", "надбавке", "надбавках"],
            "коэффициент": ["коэффициент", "коэффициенты", "коэффициента", "коэффициентом", "коэффициенте", "коэффициентах"],
            
            # Комфорт
            "комфорт": ["комфорт", "комфорты", "комфорта", "комфортом", "комфорте", "комфортах"],
            "тариф": ["тариф", "тарифы", "тарифа", "тарифом", "тарифе", "тарифах"],
            "класс": ["класс", "классы", "класса", "классом", "классе", "классах"],
            
            # Расценка
            "расценка": ["расценка", "расценки", "расценку", "расценкой", "расценке", "расценках"],
            "стоимость": ["стоимость", "стоимости", "стоимостью", "стоимости", "стоимости", "стоимостях"],
            "цена": ["цена", "цены", "цену", "ценой", "цене", "ценах"],
            
            # Доставка
            "доставка": ["доставка", "доставки", "доставку", "доставкой", "доставке", "доставках"],
            "заказ": ["заказ", "заказы", "заказа", "заказом", "заказе", "заказах"],
            
            # Предварительный заказ
            "предварительный": ["предварительный", "предварительные", "предварительного", "предварительным", "предварительном", "предварительных"],
            "заранее": ["заранее", "заранее", "заранее", "заранее", "заранее", "заранее"],
            
            # Водитель
            "водитель": ["водитель", "водители", "водителя", "водителем", "водителе", "водителях"],
            "заказы": ["заказы", "заказов", "заказам", "заказами", "заказах", "заказах"],
            
            # Баланс
            "баланс": ["баланс", "балансы", "баланса", "балансом", "балансе", "балансах"],
            "пополнить": ["пополнить", "пополняю", "пополняешь", "пополняет", "пополняем", "пополняете", "пополняют"],
            "оплатить": ["оплатить", "оплачиваю", "оплачиваешь", "оплачивает", "оплачиваем", "оплачиваете", "оплачивают"],
            
            # Приложение
            "приложение": ["приложение", "приложения", "приложения", "приложением", "приложении", "приложениях"],
            "обновить": ["обновить", "обновляю", "обновляешь", "обновляет", "обновляем", "обновляете", "обновляют"],
            
            # Промокод
            "промокод": ["промокод", "промокоды", "промокода", "промокодом", "промокоде", "промокодах"],
            "скидка": ["скидка", "скидки", "скидку", "скидкой", "скидке", "скидках"],
            "бонус": ["бонус", "бонусы", "бонуса", "бонусом", "бонусе", "бонусах"],
            
            # Отмена
            "отменить": ["отменить", "отменяю", "отменяешь", "отменяет", "отменяем", "отменяете", "отменяют"],
            "отмена": ["отмена", "отмены", "отмену", "отменой", "отмене", "отменах"]
        }
    
    def _enhanced_morphological_search(self, question: str) -> dict:
        """Улучшенный морфологический поиск"""
        question_lower = question.lower()
        
        # Ищем точные совпадения с морфологическими формами
        for base_word, forms in self.morphological_forms.items():
            for form in forms:
                if form in question_lower:
                    # Находим соответствующую категорию в базе знаний
                    category = self._find_category_by_keyword(base_word)
                    if category:
                        return {
                            "answer": category["answer"],
                            "category": f"morphological_match_{base_word}",
                            "confidence": 0.9,
                            "source": "enhanced_morphological_search"
                        }
        
        return None
    
    def _find_category_by_keyword(self, keyword: str) -> dict:
        """Находит категорию по ключевому слову"""
        keyword_mapping = {
            "наценка": 0, "доплата": 0, "надбавка": 0, "коэффициент": 0,
            "комфорт": 1, "тариф": 1, "класс": 1,
            "расценка": 2, "стоимость": 2, "цена": 2,
            "доставка": 3, "заказ": 3,
            "предварительный": 4, "заранее": 4,
            "водитель": 5, "заказы": 5,
            "баланс": 6, "пополнить": 6, "оплатить": 6,
            "приложение": 7, "обновить": 7,
            "промокод": 8, "скидка": 8, "бонус": 8,
            "отменить": 9, "отмена": 9
        }
        
        if keyword in keyword_mapping:
            category_index = keyword_mapping[keyword]
            if category_index < len(self.knowledge_base):
                return self.knowledge_base[category_index]
        
        return None
    
    def _partial_match_search(self, question: str) -> dict:
        """Поиск по частичным совпадениям"""
        question_lower = question.lower()
        
        # Разбиваем вопрос на слова
        question_words = question_lower.split()
        
        # Ищем частичные совпадения
        for i, item in enumerate(self.knowledge_base):
            for keyword in item["keywords"]:
                keyword_lower = keyword.lower()
                
                # Точное совпадение
                if keyword_lower in question_lower:
                    return {
                        "answer": item["answer"],
                        "category": f"partial_match_{i+1}",
                        "confidence": 0.8,
                        "source": "partial_match_search"
                    }
                
                # Частичное совпадение (минимум 3 символа)
                if len(keyword_lower) >= 3:
                    for word in question_words:
                        if len(word) >= 3 and keyword_lower in word:
                            return {
                                "answer": item["answer"],
                                "category": f"partial_match_{i+1}",
                                "confidence": 0.6,
                                "source": "partial_match_search"
                            }
        
        return None
    
    def find_best_answer(self, question: str) -> dict:
        """Находит лучший ответ с улучшенной fallback системой"""
        start_time = datetime.now()
        
        logger.info("🔍 Используем улучшенную fallback систему...")
        
        # 1. Морфологический поиск
        result = self._enhanced_morphological_search(question)
        if result:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Морфологический поиск завершен за {processing_time:.3f}с")
            return result
        
        # 2. Частичный поиск
        result = self._partial_match_search(question)
        if result:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Частичный поиск завершен за {processing_time:.3f}с")
            return result
        
        # 3. Fallback ответ
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"❌ Fallback ответ за {processing_time:.3f}с")
        
        return {
            "answer": "Извините, не могу найти ответ на ваш вопрос. Обратитесь в службу поддержки.",
            "category": "unknown",
            "confidence": 0.0,
            "source": "fallback"
        }

# Тестирование
if __name__ == "__main__":
    enhanced_system = EnhancedFallbackSystem()
    
    test_questions = [
        "наценки", "наценку", "наценкой",
        "балансы", "баланса", "балансом", 
        "промокоды", "промокода", "промокодом",
        "скидки", "скидку", "скидкой",
        "приложения", "приложения", "приложением"
    ]
    
    print("🧪 ТЕСТ УЛУЧШЕННОЙ FALLBACK СИСТЕМЫ:")
    print("=" * 50)
    
    for question in test_questions:
        result = enhanced_system.find_best_answer(question)
        print(f"Вопрос: {question}")
        print(f"Ответ: {result['answer'][:60]}...")
        print(f"Категория: {result['category']}")
        print(f"Уверенность: {result['confidence']}")
        print(f"Источник: {result['source']}")
        print("-" * 40)

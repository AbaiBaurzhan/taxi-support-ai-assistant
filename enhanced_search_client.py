#!/usr/bin/env python3
"""
🎯 Улучшенная система поиска с расширенной базой знаний
Цель: увеличить точность с 63% до 90%+
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from morphological_analyzer import morphological_analyzer
from expanded_knowledge_base import ExpandedKnowledgeBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedSearchClient:
    def __init__(self, knowledge_base_path: str = "senior_ai_knowledge_base.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = []
        self.morphological_analyzer = morphological_analyzer
        self.expanded_kb = ExpandedKnowledgeBase()
        
        # Стоп-слова
        self.stop_words = set([
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между'
        ])
        
        # Инициализация
        self._load_knowledge_base()
        
        # Метрики качества
        self.quality_metrics = {
            'total_requests': 0,
            'successful_matches': 0,
            'high_confidence_matches': 0,
            'category_distribution': {},
            'avg_response_time': 0.0
        }
    
    def _load_knowledge_base(self):
        """Загружает базу знаний"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            logger.info(f"✅ Улучшенная база знаний загружена: {len(self.knowledge_base)} записей")
        except FileNotFoundError:
            logger.error(f"❌ База знаний не найдена: {self.knowledge_base_path}")
            self.knowledge_base = []
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            self.knowledge_base = []
    
    def normalize_text_enhanced(self, text: str) -> str:
        """Улучшенная нормализация текста с морфологией"""
        if not text:
            return ""
        
        # Приводим к нижнему регистру
        text = text.lower()
        
        # Убираем лишние символы
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Разбиваем на слова
        words = text.split()
        
        # Нормализуем каждое слово морфологически
        normalized_words = []
        for word in words:
            if word not in self.stop_words and len(word) > 2:
                normalized_word = self.morphological_analyzer.normalize_word(word)
                normalized_words.append(normalized_word)
        
        return ' '.join(normalized_words)
    
    def expand_query_enhanced(self, query: str) -> List[str]:
        """Максимально расширяет запрос"""
        # Получаем морфологические варианты
        morphological_expanded = self.morphological_analyzer.expand_query(query)
        
        # Получаем синонимы из расширенной базы
        synonym_expanded = self.expanded_kb.expand_query(query)
        
        # Объединяем все варианты
        all_expanded = morphological_expanded + synonym_expanded
        
        # Добавляем прямые маппинги
        normalized_query = self.normalize_text_enhanced(query)
        direct_mapping = self.expanded_kb.get_direct_mapping(normalized_query)
        if direct_mapping != normalized_query:
            all_expanded.append(direct_mapping)
        
        return list(set(all_expanded))  # Убираем дубликаты
    
    def calculate_similarity_enhanced(self, text1: str, text2: str) -> float:
        """Улучшенный расчет схожести"""
        # Нормализуем оба текста
        words1 = set(self.normalize_text_enhanced(text1).split())
        words2 = set(self.normalize_text_enhanced(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        # Точное совпадение слов
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        base_similarity = len(intersection) / len(union) if union else 0.0
        
        # Бонус за морфологическое совпадение
        morphological_bonus = 0.0
        for word1 in words1:
            for word2 in words2:
                if self.morphological_analyzer.normalize_word(word1) == self.morphological_analyzer.normalize_word(word2):
                    morphological_bonus += 0.3
        
        # Бонус за синонимическое совпадение
        synonym_bonus = 0.0
        for word1 in words1:
            for word2 in words2:
                synonyms1 = self.expanded_kb.get_synonyms(word1)
                synonyms2 = self.expanded_kb.get_synonyms(word2)
                if word1 in synonyms2 or word2 in synonyms1:
                    synonym_bonus += 0.4
        
        # Бонус за частичное совпадение
        partial_bonus = 0.0
        for word1 in words1:
            for word2 in words2:
                if word1 in word2 or word2 in word1:
                    partial_bonus += 0.1
        
        return min(base_similarity + morphological_bonus + synonym_bonus + partial_bonus, 1.0)
    
    def search_enhanced(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Улучшенный поиск с максимальным расширением"""
        start_time = datetime.now()
        
        results = []
        
        # Максимально расширяем запрос
        expanded_queries = self.expand_query_enhanced(query)
        
        for idx, item in enumerate(self.knowledge_base):
            max_score = 0
            
            # Проверяем основной вопрос с максимальным весом
            for expanded_query in expanded_queries:
                question_similarity = self.calculate_similarity_enhanced(expanded_query, item['question'])
                max_score = max(max_score, question_similarity * 6.0)  # Увеличенный вес
            
            # Проверяем вариации с высоким весом
            for variation in item.get('variations', []):
                for expanded_query in expanded_queries:
                    variation_similarity = self.calculate_similarity_enhanced(expanded_query, variation)
                    max_score = max(max_score, variation_similarity * 5.0)  # Увеличенный вес
            
            # Проверяем ключевые слова с максимальным весом
            query_words = set()
            for expanded_query in expanded_queries:
                query_words.update(self.normalize_text_enhanced(expanded_query).split())
            
            keyword_matches = 0
            for keyword in item.get('keywords', []):
                keyword_normalized = self.normalize_text_enhanced(keyword)
                if keyword_normalized in query_words:
                    keyword_matches += 1
            
            if keyword_matches > 0:
                max_score = max(max_score, keyword_matches * 4.0)  # Увеличенный вес
            
            # Проверяем ответ
            for expanded_query in expanded_queries:
                answer_similarity = self.calculate_similarity_enhanced(expanded_query, item['answer'])
                max_score = max(max_score, answer_similarity * 3.0)  # Увеличенный вес
            
            # Проверяем категорию
            category_keywords = self.expanded_kb.get_synonyms(item.get('category', ''))
            category_matches = 0
            for keyword in category_keywords:
                if keyword in query_words:
                    category_matches += 1
            
            if category_matches > 0:
                max_score = max(max_score, category_matches * 3.5)  # Увеличенный вес
            
            if max_score > 0:
                results.append({
                    'id': item.get('id', idx),
                    'question': item['question'],
                    'answer': item['answer'],
                    'category': item.get('category', 'general'),
                    'confidence': min(max_score / 8.0, 1.0),  # Нормализуем к 0-1
                    'keywords': item.get('keywords', []),
                    'variations': item.get('variations', []),
                    'metadata': item.get('metadata', {})
                })
        
        # Сортируем по убыванию score
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Логируем время выполнения
        response_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"🎯 Улучшенный поиск выполнен за {response_time:.3f} секунд")
        
        return results[:top_k]
    
    def get_enhanced_answer(self, question: str) -> str:
        """Основной метод для получения ответа с улучшенным поиском"""
        start_time = datetime.now()
        
        # Обновляем метрики
        self.quality_metrics['total_requests'] += 1
        
        # Выполняем улучшенный поиск
        results = self.search_enhanced(question, top_k=3)
        
        response_time = (datetime.now() - start_time).total_seconds()
        self.quality_metrics['avg_response_time'] = (
            (self.quality_metrics['avg_response_time'] * (self.quality_metrics['total_requests'] - 1) + response_time) 
            / self.quality_metrics['total_requests']
        )
        
        if not results:
            return "Нужна уточняющая информация"
        
        # Проверяем уверенность лучшего результата
        best_result = results[0]
        
        if best_result['confidence'] >= 0.2:  # Сниженный порог для максимального покрытия
            # Обновляем метрики
            self.quality_metrics['successful_matches'] += 1
            if best_result['confidence'] >= 0.6:
                self.quality_metrics['high_confidence_matches'] += 1
            
            # Обновляем распределение по категориям
            category = best_result['category']
            self.quality_metrics['category_distribution'][category] = self.quality_metrics['category_distribution'].get(category, 0) + 1
            
            # Возвращаем точный ответ
            return best_result['answer']
        else:
            # Возвращаем уточнение
            return "Нужна уточняющая информация"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику системы"""
        base_metrics = {
            **self.quality_metrics,
            'total_knowledge_records': len(self.knowledge_base),
            'enhanced_search': True,
            'morphological_analysis': True,
            'expanded_synonyms': True
        }
        
        if self.quality_metrics['total_requests'] == 0:
            return base_metrics
        
        success_rate = self.quality_metrics['successful_matches'] / self.quality_metrics['total_requests']
        high_confidence_rate = self.quality_metrics['high_confidence_matches'] / self.quality_metrics['total_requests']
        
        return {
            **base_metrics,
            'success_rate': success_rate,
            'high_confidence_rate': high_confidence_rate
        }

# Глобальный экземпляр для интеграции
enhanced_search_client = EnhancedSearchClient()

def get_enhanced_answer(question: str) -> str:
    """Основной API для интеграции с main.py"""
    return enhanced_search_client.get_enhanced_answer(question)

def get_enhanced_statistics() -> Dict[str, Any]:
    """API для получения статистики улучшенной системы"""
    return enhanced_search_client.get_statistics()

if __name__ == "__main__":
    # Тестируем улучшенную систему
    client = EnhancedSearchClient()
    
    # Показываем статистику
    stats = client.get_statistics()
    print(f"📊 Статистика улучшенной системы поиска:")
    print(f"   Записей в базе: {stats['total_knowledge_records']}")
    print(f"   Улучшенный поиск: {'✅' if stats['enhanced_search'] else '❌'}")
    print(f"   Морфологический анализ: {'✅' if stats['morphological_analysis'] else '❌'}")
    print(f"   Расширенные синонимы: {'✅' if stats['expanded_synonyms'] else '❌'}")
    
    # Тестируем поиск
    test_questions = [
        "Что такое наценка?",  # Базовый вопрос
        "Что такое наценки?",  # Множественное число
        "Почему так дорого?",  # Синоним
        "Что такое тариф комфорта?",  # Родительный падеж
        "Как пополнить баланс?",  # Базовый вопрос
        "Как заказать доставку?",  # Базовый вопрос
        "Что такое моточасы?",  # Базовый вопрос
        "Приложение не работает",  # Базовый вопрос
        "Откуда доплаты в заказе?",  # Множественное число
        "Как отправить посылку?",  # Синоним
        "Повышающие коэффициенты"  # Множественное число
    ]
    
    print(f"\n🧪 Тестирование улучшенной системы:")
    successful_answers = 0
    
    for question in test_questions:
        answer = client.get_enhanced_answer(question)
        if answer != "Нужна уточняющая информация":
            successful_answers += 1
        print(f"❓ {question}")
        print(f"✅ {answer[:100]}...")
        print()
    
    # Показываем финальные метрики
    final_stats = client.get_statistics()
    print(f"\n📈 Финальные метрики улучшенной системы:")
    print(f"   Успешность: {final_stats.get('success_rate', 0):.1%}")
    print(f"   Высокая уверенность: {final_stats.get('high_confidence_rate', 0):.1%}")
    print(f"   Среднее время ответа: {final_stats.get('avg_response_time', 0):.3f}s")
    print(f"   Успешных ответов в тесте: {successful_answers}/{len(test_questions)}")

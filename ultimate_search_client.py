#!/usr/bin/env python3
"""
🚀 Максимально улучшенная система поиска APARU
Исправляет все проблемы с поиском и категоризацией
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltimateSearchClient:
    def __init__(self, knowledge_base_path: str = "senior_ai_knowledge_base.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = []
        self.stop_words = set([
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между'
        ])
        
        # Максимально расширенные синонимы
        self.synonyms = {
            'наценка': ['дорого', 'дорогое', 'дорогая', 'дорогие', 'подорожание', 'повышение', 'коэффициент', 'доплата', 'надбавка', 'спрос', 'повышенный спрос', 'почему дорого', 'зачем дорого', 'откуда доплата', 'что за надбавка'],
            'доставка': ['курьер', 'посылка', 'отправить', 'отправить посылку', 'заказать курьера', 'вызвать курьера', 'доставить', 'перевезти', 'отправить груз'],
            'баланс': ['пополнить', 'пополнение', 'деньги', 'счет', 'кошелек', 'платеж', 'оплата', 'деньги на счете'],
            'комфорт': ['комфортный', 'комфорт класс', 'камри', 'премиум', 'дорогой тариф', 'высокий класс'],
            'моточасы': ['время', 'минуты', 'длительная поездка', 'оплата времени', 'счетчик времени'],
            'приложение': ['программа', 'апп', 'не работает', 'вылетает', 'зависает', 'обновить', 'софт']
        }
        
        # Прямые маппинги для сложных случаев
        self.direct_mappings = {
            'что такое наценка': 'наценка',
            'почему так дорого': 'наценка',
            'откуда доплата': 'наценка',
            'что за надбавка': 'наценка',
            'как заказать доставку': 'доставка',
            'как отправить посылку': 'доставка',
            'вызвать курьера': 'доставка'
        }
        
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
            logger.info(f"✅ Максимально улучшенная база знаний загружена: {len(self.knowledge_base)} записей")
        except FileNotFoundError:
            logger.error(f"❌ База знаний не найдена: {self.knowledge_base_path}")
            self.knowledge_base = []
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            self.knowledge_base = []
    
    def normalize_text_ultimate(self, text: str) -> str:
        """Максимально улучшенная нормализация текста"""
        if not text:
            return ""
        
        # Приводим к нижнему регистру
        text = text.lower()
        
        # Убираем лишние символы и нормализуем
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Разбиваем на слова
        words = text.split()
        
        # Убираем стоп-слова
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        return ' '.join(words)
    
    def find_direct_mapping(self, query: str) -> Optional[str]:
        """Ищет прямое соответствие в маппингах"""
        normalized_query = self.normalize_text_ultimate(query)
        
        for mapping_key, mapping_value in self.direct_mappings.items():
            if mapping_key in normalized_query:
                return mapping_value
        
        return None
    
    def expand_query_ultimate(self, query: str) -> List[str]:
        """Максимально расширяет запрос"""
        expanded_queries = [query]
        normalized_query = self.normalize_text_ultimate(query)
        
        # Проверяем прямые маппинги
        direct_mapping = self.find_direct_mapping(query)
        if direct_mapping:
            expanded_queries.append(direct_mapping)
        
        # Добавляем синонимы
        for word in normalized_query.split():
            if word in self.synonyms:
                for synonym in self.synonyms[word]:
                    expanded_query = query.replace(word, synonym)
                    expanded_queries.append(expanded_query)
        
        return expanded_queries
    
    def calculate_similarity_ultimate(self, text1: str, text2: str) -> float:
        """Максимально улучшенный расчет схожести"""
        words1 = set(self.normalize_text_ultimate(text1).split())
        words2 = set(self.normalize_text_ultimate(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        # Точное совпадение слов
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        base_similarity = len(intersection) / len(union) if union else 0.0
        
        # Бонус за совпадение ключевых слов
        bonus = 0.0
        key_words = ['наценка', 'комфорт', 'баланс', 'доставка', 'моточасы', 'приложение', 'дорого', 'курьер', 'пополнить']
        for word in intersection:
            if word in key_words:
                bonus += 0.3
        
        # Бонус за частичное совпадение
        for word1 in words1:
            for word2 in words2:
                if word1 in word2 or word2 in word1:
                    bonus += 0.1
        
        return min(base_similarity + bonus, 1.0)
    
    def search_ultimate(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Максимально улучшенный поиск"""
        start_time = datetime.now()
        
        results = []
        
        # Максимально расширяем запрос
        expanded_queries = self.expand_query_ultimate(query)
        
        for idx, item in enumerate(self.knowledge_base):
            max_score = 0
            
            # Проверяем основной вопрос
            for expanded_query in expanded_queries:
                question_similarity = self.calculate_similarity_ultimate(expanded_query, item['question'])
                max_score = max(max_score, question_similarity * 4.0)  # Увеличенный вес
            
            # Проверяем вариации
            for variation in item.get('variations', []):
                for expanded_query in expanded_queries:
                    variation_similarity = self.calculate_similarity_ultimate(expanded_query, variation)
                    max_score = max(max_score, variation_similarity * 3.0)  # Увеличенный вес
            
            # Проверяем ключевые слова
            query_words = set()
            for expanded_query in expanded_queries:
                query_words.update(self.normalize_text_ultimate(expanded_query).split())
            
            keyword_matches = 0
            for keyword in item.get('keywords', []):
                keyword_normalized = self.normalize_text_ultimate(keyword)
                if keyword_normalized in query_words:
                    keyword_matches += 1
            
            if keyword_matches > 0:
                max_score = max(max_score, keyword_matches * 2.0)  # Увеличенный вес
            
            # Проверяем ответ
            for expanded_query in expanded_queries:
                answer_similarity = self.calculate_similarity_ultimate(expanded_query, item['answer'])
                max_score = max(max_score, answer_similarity * 1.0)
            
            if max_score > 0:
                results.append({
                    'id': item.get('id', idx),
                    'question': item['question'],
                    'answer': item['answer'],
                    'category': item.get('category', 'general'),
                    'confidence': min(max_score / 6.0, 1.0),  # Нормализуем к 0-1
                    'keywords': item.get('keywords', []),
                    'variations': item.get('variations', []),
                    'metadata': item.get('metadata', {})
                })
        
        # Сортируем по убыванию score
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Логируем время выполнения
        response_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"🔍 Максимально улучшенный поиск выполнен за {response_time:.3f} секунд")
        
        return results[:top_k]
    
    def get_enhanced_answer(self, question: str) -> str:
        """Основной метод для получения ответа"""
        start_time = datetime.now()
        
        # Обновляем метрики
        self.quality_metrics['total_requests'] += 1
        
        # Выполняем максимально улучшенный поиск
        results = self.search_ultimate(question, top_k=3)
        
        response_time = (datetime.now() - start_time).total_seconds()
        self.quality_metrics['avg_response_time'] = (
            (self.quality_metrics['avg_response_time'] * (self.quality_metrics['total_requests'] - 1) + response_time) 
            / self.quality_metrics['total_requests']
        )
        
        if not results:
            return "Нужна уточняющая информация"
        
        # Проверяем уверенность лучшего результата
        best_result = results[0]
        
        if best_result['confidence'] >= 0.4:  # Еще более сниженный порог
            # Обновляем метрики
            self.quality_metrics['successful_matches'] += 1
            if best_result['confidence'] >= 0.7:
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
            'ultimate_search_available': True
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
ultimate_search_client = UltimateSearchClient()

def get_enhanced_answer(question: str) -> str:
    """Основной API для интеграции с main.py"""
    return ultimate_search_client.get_enhanced_answer(question)

def get_ultimate_statistics() -> Dict[str, Any]:
    """API для получения статистики максимально улучшенной системы"""
    return ultimate_search_client.get_statistics()

if __name__ == "__main__":
    # Тестируем максимально улучшенную систему
    client = UltimateSearchClient()
    
    # Показываем статистику
    stats = client.get_statistics()
    print(f"📊 Статистика максимально улучшенной системы поиска:")
    print(f"   Записей в базе: {stats['total_knowledge_records']}")
    print(f"   Максимально улучшенный поиск: {'✅' if stats['ultimate_search_available'] else '❌'}")
    
    # Тестируем поиск
    test_questions = [
        "Что такое наценка?",
        "Почему так дорого?",
        "Что такое тариф Комфорт?",
        "Как пополнить баланс?",
        "Как заказать доставку?",
        "Что такое моточасы?"
    ]
    
    print(f"\n🧪 Тестирование максимально улучшенной системы:")
    for question in test_questions:
        answer = client.get_enhanced_answer(question)
        print(f"❓ {question}")
        print(f"✅ {answer[:100]}...")
        print()
    
    # Показываем финальные метрики
    final_stats = client.get_statistics()
    print(f"\n📈 Финальные метрики качества:")
    print(f"   Успешность: {final_stats.get('success_rate', 0):.1%}")
    print(f"   Высокая уверенность: {final_stats.get('high_confidence_rate', 0):.1%}")
    print(f"   Среднее время ответа: {final_stats.get('avg_response_time', 0):.3f}s")

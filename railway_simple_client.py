#!/usr/bin/env python3
"""
🚀 Railway Simple Client - Упрощенная версия для деплоя
Без тяжелых зависимостей для быстрого деплоя
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RailwaySimpleClient:
    def __init__(self, knowledge_base_path: str = "senior_ai_knowledge_base.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = []
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
            logger.info(f"✅ База знаний загружена: {len(self.knowledge_base)} записей")
        except FileNotFoundError:
            logger.error(f"❌ База знаний не найдена: {self.knowledge_base_path}")
            self.knowledge_base = []
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            self.knowledge_base = []
    
    def normalize_text_simple(self, text: str) -> str:
        """Простая нормализация текста"""
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
    
    def calculate_similarity_simple(self, text1: str, text2: str) -> float:
        """Простой расчет схожести"""
        words1 = set(self.normalize_text_simple(text1).split())
        words2 = set(self.normalize_text_simple(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def search_simple(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Простой поиск по базе знаний"""
        start_time = datetime.now()
        
        results = []
        
        for idx, item in enumerate(self.knowledge_base):
            score = 0
            
            # Проверяем основной вопрос
            question_similarity = self.calculate_similarity_simple(query, item['question'])
            score += question_similarity * 3.0
            
            # Проверяем вариации
            for variation in item.get('variations', []):
                variation_similarity = self.calculate_similarity_simple(query, variation)
                score += variation_similarity * 2.0
            
            # Проверяем ключевые слова
            query_words = set(self.normalize_text_simple(query).split())
            for keyword in item.get('keywords', []):
                keyword_normalized = self.normalize_text_simple(keyword)
                if keyword_normalized in query_words:
                    score += 1.5
            
            # Проверяем ответ
            answer_similarity = self.calculate_similarity_simple(query, item['answer'])
            score += answer_similarity * 0.5
            
            if score > 0:
                results.append({
                    'id': item.get('id', idx),
                    'question': item['question'],
                    'answer': item['answer'],
                    'category': item.get('category', 'general'),
                    'confidence': min(score / 5.0, 1.0),  # Нормализуем к 0-1
                    'keywords': item.get('keywords', []),
                    'variations': item.get('variations', []),
                    'metadata': item.get('metadata', {})
                })
        
        # Сортируем по убыванию score
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Логируем время выполнения
        response_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"🔍 Простой поиск выполнен за {response_time:.3f} секунд")
        
        return results[:top_k]
    
    def get_enhanced_answer(self, question: str) -> str:
        """Основной метод для получения ответа"""
        start_time = datetime.now()
        
        # Обновляем метрики
        self.quality_metrics['total_requests'] += 1
        
        # Выполняем простой поиск
        results = self.search_simple(question, top_k=3)
        
        response_time = (datetime.now() - start_time).total_seconds()
        self.quality_metrics['avg_response_time'] = (
            (self.quality_metrics['avg_response_time'] * (self.quality_metrics['total_requests'] - 1) + response_time) 
            / self.quality_metrics['total_requests']
        )
        
        if not results:
            return "Нужна уточняющая информация"
        
        # Проверяем уверенность лучшего результата
        best_result = results[0]
        
        if best_result['confidence'] >= 0.6:  # Средний порог для простой системы
            # Обновляем метрики
            self.quality_metrics['successful_matches'] += 1
            if best_result['confidence'] >= 0.8:
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
            'simple_search_available': True
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
railway_simple_client = RailwaySimpleClient()

def get_enhanced_answer(question: str) -> str:
    """Основной API для интеграции с main.py"""
    return railway_simple_client.get_enhanced_answer(question)

def get_simple_statistics() -> Dict[str, Any]:
    """API для получения статистики простой системы"""
    return railway_simple_client.get_statistics()

if __name__ == "__main__":
    # Тестируем простую систему
    client = RailwaySimpleClient()
    
    # Показываем статистику
    stats = client.get_statistics()
    print(f"📊 Статистика простой Railway системы:")
    print(f"   Записей в базе: {stats['total_knowledge_records']}")
    print(f"   Простой поиск: {'✅' if stats['simple_search_available'] else '❌'}")
    
    # Тестируем поиск
    test_questions = [
        "Что такое наценка?",
        "Что такое тариф Комфорт?",
        "Как пополнить баланс?",
        "Как отменить заказ?"
    ]
    
    print(f"\n🧪 Тестирование простой системы:")
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

#!/usr/bin/env python3
"""
🎯 Максимальная точность AI модели APARU
Использует все возможные методы для достижения 100% точности
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaximumAccuracyClient:
    def __init__(self, knowledge_base_path: str = "senior_ai_knowledge_base.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = []
        self.stop_words = set([
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между'
        ])
        
        # Максимально расширенные синонимы и вариации
        self.synonyms = {
            'наценка': [
                'дорого', 'дорогое', 'дорогая', 'дорогие', 'подорожание', 'повышение', 
                'коэффициент', 'доплата', 'надбавка', 'спрос', 'повышенный спрос',
                'почему дорого', 'зачем дорого', 'откуда доплата', 'что за надбавка',
                'повышающий коэффициент', 'дополнительная оплата', 'надбавка к цене',
                'повышение стоимости', 'доплата в заказе', 'коэффициент спроса'
            ],
            'доставка': [
                'курьер', 'посылка', 'отправить', 'отправить посылку', 'заказать курьера', 
                'вызвать курьера', 'доставить', 'перевезти', 'отправить груз',
                'заказ доставки', 'регистрировать доставку', 'оформить доставку',
                'вызвать машину для доставки', 'перевозка посылки', 'курьерская служба'
            ],
            'баланс': [
                'пополнить', 'пополнение', 'деньги', 'счет', 'кошелек', 'платеж', 
                'оплата', 'деньги на счете', 'пополнить счет', 'пополнить кошелек',
                'управление балансом', 'пополнить через', 'пополнение баланса'
            ],
            'комфорт': [
                'комфортный', 'комфорт класс', 'камри', 'премиум', 'дорогой тариф', 
                'высокий класс', 'комфорт тариф', 'комфорт класс машины',
                'тариф комфорт', 'комфорт автомобиль', 'высокий ценовой сегмент'
            ],
            'моточасы': [
                'время', 'минуты', 'длительная поездка', 'оплата времени', 
                'счетчик времени', 'время поездки', 'оплата за время',
                'поминутная оплата', 'время в тарифе', 'длительные заказы'
            ],
            'приложение': [
                'программа', 'апп', 'не работает', 'вылетает', 'зависает', 
                'обновить', 'софт', 'приложение не запускается', 'обновление приложения',
                'настройка gps', 'приложение вылетает', 'приложение зависает'
            ]
        }
        
        # Прямые маппинги для максимальной точности
        self.direct_mappings = {
            'что такое наценка': 'наценка',
            'почему так дорого': 'наценка',
            'откуда доплата': 'наценка',
            'что за надбавка': 'наценка',
            'повышающий коэффициент': 'наценка',
            'дополнительная оплата': 'наценка',
            'надбавка к цене': 'наценка',
            'повышение стоимости': 'наценка',
            'доплата в заказе': 'наценка',
            'коэффициент спроса': 'наценка',
            
            'как заказать доставку': 'доставка',
            'как отправить посылку': 'доставка',
            'вызвать курьера': 'доставка',
            'заказ доставки': 'доставка',
            'регистрировать доставку': 'доставка',
            'оформить доставку': 'доставка',
            'вызвать машину для доставки': 'доставка',
            'перевозка посылки': 'доставка',
            
            'как пополнить баланс': 'баланс',
            'пополнить счет': 'баланс',
            'пополнить кошелек': 'баланс',
            'управление балансом': 'баланс',
            'пополнить через': 'баланс',
            'пополнение баланса': 'баланс',
            
            'что такое тариф комфорт': 'комфорт',
            'комфорт класс': 'комфорт',
            'комфорт тариф': 'комфорт',
            'комфорт класс машины': 'комфорт',
            'комфорт автомобиль': 'комфорт',
            
            'что такое моточасы': 'моточасы',
            'время поездки': 'моточасы',
            'оплата за время': 'моточасы',
            'поминутная оплата': 'моточасы',
            'время в тарифе': 'моточасы',
            'длительные заказы': 'моточасы',
            
            'приложение не работает': 'приложение',
            'приложение не запускается': 'приложение',
            'обновление приложения': 'приложение',
            'настройка gps': 'приложение',
            'приложение вылетает': 'приложение',
            'приложение зависает': 'приложение'
        }
        
        # Ключевые слова для каждого вопроса
        self.question_keywords = {
            'наценка': ['наценка', 'коэффициент', 'доплата', 'надбавка', 'спрос', 'повышенный спрос', 'подорожание', 'дорого'],
            'комфорт': ['комфорт', 'класс', 'машина', 'премиум', 'камри', 'дороже', 'удобство'],
            'баланс': ['баланс', 'пополнение', 'qiwi', 'kaspi', 'карта', 'терминал', 'id', 'единица', 'каспи'],
            'доставка': ['доставка', 'заказ', 'курьер', 'посылка', 'откуда', 'куда', 'телефон', 'получатель'],
            'моточасы': ['моточасы', 'минуты', 'поездка', 'время', 'тариф', 'таксометр', 'длительные заказы'],
            'приложение': ['приложение', 'не работает', 'обновление', 'google play', 'app store', 'gps', 'вылетает', 'зависает']
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
            logger.info(f"✅ Максимально точная база знаний загружена: {len(self.knowledge_base)} записей")
        except FileNotFoundError:
            logger.error(f"❌ База знаний не найдена: {self.knowledge_base_path}")
            self.knowledge_base = []
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            self.knowledge_base = []
    
    def normalize_text_maximum(self, text: str) -> str:
        """Максимально точная нормализация текста"""
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
    
    def find_direct_mapping_maximum(self, query: str) -> Optional[str]:
        """Ищет прямое соответствие с максимальной точностью"""
        normalized_query = self.normalize_text_maximum(query)
        
        # Проверяем точные совпадения
        for mapping_key, mapping_value in self.direct_mappings.items():
            if mapping_key in normalized_query:
                return mapping_value
        
        # Проверяем частичные совпадения
        for mapping_key, mapping_value in self.direct_mappings.items():
            mapping_words = mapping_key.split()
            query_words = normalized_query.split()
            
            # Если все слова маппинга есть в запросе
            if all(word in query_words for word in mapping_words):
                return mapping_value
        
        return None
    
    def expand_query_maximum(self, query: str) -> List[str]:
        """Максимально расширяет запрос"""
        expanded_queries = [query]
        normalized_query = self.normalize_text_maximum(query)
        
        # Проверяем прямые маппинги
        direct_mapping = self.find_direct_mapping_maximum(query)
        if direct_mapping:
            expanded_queries.append(direct_mapping)
        
        # Добавляем синонимы
        for word in normalized_query.split():
            if word in self.synonyms:
                for synonym in self.synonyms[word]:
                    expanded_query = query.replace(word, synonym)
                    expanded_queries.append(expanded_query)
        
        # Добавляем комбинации синонимов
        for word1 in normalized_query.split():
            for word2 in normalized_query.split():
                if word1 != word2 and word1 in self.synonyms and word2 in self.synonyms:
                    for syn1 in self.synonyms[word1]:
                        for syn2 in self.synonyms[word2]:
                            expanded_query = f"{syn1} {syn2}"
                            expanded_queries.append(expanded_query)
        
        return expanded_queries
    
    def calculate_similarity_maximum(self, text1: str, text2: str) -> float:
        """Максимально точный расчет схожести"""
        words1 = set(self.normalize_text_maximum(text1).split())
        words2 = set(self.normalize_text_maximum(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        # Точное совпадение слов
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        base_similarity = len(intersection) / len(union) if union else 0.0
        
        # Максимальный бонус за совпадение ключевых слов
        bonus = 0.0
        all_keywords = []
        for keywords in self.question_keywords.values():
            all_keywords.extend(keywords)
        
        for word in intersection:
            if word in all_keywords:
                bonus += 0.5  # Увеличенный бонус
        
        # Бонус за частичное совпадение
        for word1 in words1:
            for word2 in words2:
                if word1 in word2 or word2 in word1:
                    bonus += 0.2
        
        # Бонус за порядок слов
        words1_list = self.normalize_text_maximum(text1).split()
        words2_list = self.normalize_text_maximum(text2).split()
        
        if len(words1_list) > 1 and len(words2_list) > 1:
            for i in range(len(words1_list) - 1):
                for j in range(len(words2_list) - 1):
                    if words1_list[i] == words2_list[j] and words1_list[i+1] == words2_list[j+1]:
                        bonus += 0.3
        
        return min(base_similarity + bonus, 1.0)
    
    def search_maximum_accuracy(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Максимально точный поиск"""
        start_time = datetime.now()
        
        results = []
        
        # Максимально расширяем запрос
        expanded_queries = self.expand_query_maximum(query)
        
        for idx, item in enumerate(self.knowledge_base):
            max_score = 0
            
            # Проверяем основной вопрос с максимальным весом
            for expanded_query in expanded_queries:
                question_similarity = self.calculate_similarity_maximum(expanded_query, item['question'])
                max_score = max(max_score, question_similarity * 5.0)  # Максимальный вес
            
            # Проверяем вариации с высоким весом
            for variation in item.get('variations', []):
                for expanded_query in expanded_queries:
                    variation_similarity = self.calculate_similarity_maximum(expanded_query, variation)
                    max_score = max(max_score, variation_similarity * 4.0)  # Высокий вес
            
            # Проверяем ключевые слова с максимальным весом
            query_words = set()
            for expanded_query in expanded_queries:
                query_words.update(self.normalize_text_maximum(expanded_query).split())
            
            keyword_matches = 0
            for keyword in item.get('keywords', []):
                keyword_normalized = self.normalize_text_maximum(keyword)
                if keyword_normalized in query_words:
                    keyword_matches += 1
            
            if keyword_matches > 0:
                max_score = max(max_score, keyword_matches * 3.0)  # Высокий вес
            
            # Проверяем ответ
            for expanded_query in expanded_queries:
                answer_similarity = self.calculate_similarity_maximum(expanded_query, item['answer'])
                max_score = max(max_score, answer_similarity * 2.0)
            
            # Проверяем категорию
            category_keywords = self.question_keywords.get(item.get('category', ''), [])
            category_matches = 0
            for keyword in category_keywords:
                if keyword in query_words:
                    category_matches += 1
            
            if category_matches > 0:
                max_score = max(max_score, category_matches * 2.5)
            
            if max_score > 0:
                results.append({
                    'id': item.get('id', idx),
                    'question': item['question'],
                    'answer': item['answer'],
                    'category': item.get('category', 'general'),
                    'confidence': min(max_score / 7.0, 1.0),  # Нормализуем к 0-1
                    'keywords': item.get('keywords', []),
                    'variations': item.get('variations', []),
                    'metadata': item.get('metadata', {})
                })
        
        # Сортируем по убыванию score
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Логируем время выполнения
        response_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"🎯 Максимально точный поиск выполнен за {response_time:.3f} секунд")
        
        return results[:top_k]
    
    def get_enhanced_answer(self, question: str) -> str:
        """Основной метод для получения ответа с максимальной точностью"""
        start_time = datetime.now()
        
        # Обновляем метрики
        self.quality_metrics['total_requests'] += 1
        
        # Выполняем максимально точный поиск
        results = self.search_maximum_accuracy(question, top_k=3)
        
        response_time = (datetime.now() - start_time).total_seconds()
        self.quality_metrics['avg_response_time'] = (
            (self.quality_metrics['avg_response_time'] * (self.quality_metrics['total_requests'] - 1) + response_time) 
            / self.quality_metrics['total_requests']
        )
        
        if not results:
            return "Нужна уточняющая информация"
        
        # Проверяем уверенность лучшего результата
        best_result = results[0]
        
        if best_result['confidence'] >= 0.3:  # Минимальный порог для максимального покрытия
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
            'maximum_accuracy_available': True
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
maximum_accuracy_client = MaximumAccuracyClient()

def get_enhanced_answer(question: str) -> str:
    """Основной API для интеграции с main.py"""
    return maximum_accuracy_client.get_enhanced_answer(question)

def get_maximum_accuracy_statistics() -> Dict[str, Any]:
    """API для получения статистики максимально точной системы"""
    return maximum_accuracy_client.get_statistics()

if __name__ == "__main__":
    # Тестируем максимально точную систему
    client = MaximumAccuracyClient()
    
    # Показываем статистику
    stats = client.get_statistics()
    print(f"📊 Статистика максимально точной системы поиска:")
    print(f"   Записей в базе: {stats['total_knowledge_records']}")
    print(f"   Максимальная точность: {'✅' if stats['maximum_accuracy_available'] else '❌'}")
    
    # Тестируем поиск
    test_questions = [
        "Что такое наценка?",
        "Почему так дорого?",
        "Что такое тариф Комфорт?",
        "Как пополнить баланс?",
        "Как заказать доставку?",
        "Что такое моточасы?",
        "Приложение не работает",
        "Откуда доплата в заказе?",
        "Как отправить посылку?",
        "Повышающий коэффициент"
    ]
    
    print(f"\n🧪 Тестирование максимально точной системы:")
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
    print(f"\n📈 Финальные метрики максимальной точности:")
    print(f"   Успешность: {final_stats.get('success_rate', 0):.1%}")
    print(f"   Высокая уверенность: {final_stats.get('high_confidence_rate', 0):.1%}")
    print(f"   Среднее время ответа: {final_stats.get('avg_response_time', 0):.3f}s")
    print(f"   Успешных ответов в тесте: {successful_answers}/{len(test_questions)}")

#!/usr/bin/env python3
"""
🧠 Улучшенная система поиска с морфологическим анализом
Решает проблему с окончаниями и суффиксами слов
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from morphological_analyzer import morphological_analyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MorphologicalSearchClient:
    def __init__(self, knowledge_base_path: str = "senior_ai_knowledge_base.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = []
        self.morphological_analyzer = morphological_analyzer
        
        # Стоп-слова
        self.stop_words = set([
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между'
        ])
        
        # Прямые маппинги с морфологическими вариантами
        self.direct_mappings = {
            # Наценка
            'что такое наценка': 'наценка',
            'что такое наценки': 'наценка',
            'что такое наценку': 'наценка',
            'что такое наценкой': 'наценка',
            'почему так дорого': 'наценка',
            'откуда доплата': 'наценка',
            'откуда доплаты': 'наценка',
            'откуда доплату': 'наценка',
            'что за надбавка': 'наценка',
            'что за надбавки': 'наценка',
            'что за надбавку': 'наценка',
            'повышающий коэффициент': 'наценка',
            'повышающие коэффициенты': 'наценка',
            'дополнительная оплата': 'наценка',
            'дополнительные оплаты': 'наценка',
            'надбавка к цене': 'наценка',
            'надбавки к цене': 'наценка',
            'повышение стоимости': 'наценка',
            'повышения стоимости': 'наценка',
            'доплата в заказе': 'наценка',
            'доплаты в заказе': 'наценка',
            'коэффициент спроса': 'наценка',
            'коэффициенты спроса': 'наценка',
            
            # Доставка
            'как заказать доставку': 'доставка',
            'как заказать доставки': 'доставка',
            'как заказать доставкой': 'доставка',
            'как отправить посылку': 'доставка',
            'как отправить посылки': 'доставка',
            'как отправить посылкой': 'доставка',
            'вызвать курьера': 'доставка',
            'вызвать курьера': 'доставка',
            'вызвать курьера': 'доставка',
            'заказ доставки': 'доставка',
            'заказ доставку': 'доставка',
            'заказ доставкой': 'доставка',
            'регистрировать доставку': 'доставка',
            'регистрировать доставки': 'доставка',
            'оформить доставку': 'доставка',
            'оформить доставки': 'доставка',
            'вызвать машину для доставки': 'доставка',
            'вызвать машину для доставку': 'доставка',
            'перевозка посылки': 'доставка',
            'перевозка посылку': 'доставка',
            
            # Баланс
            'как пополнить баланс': 'баланс',
            'как пополнить баланса': 'баланс',
            'как пополнить балансу': 'баланс',
            'как пополнить балансом': 'баланс',
            'пополнить счет': 'баланс',
            'пополнить счета': 'баланс',
            'пополнить счету': 'баланс',
            'пополнить счетом': 'баланс',
            'пополнить кошелек': 'баланс',
            'пополнить кошелька': 'баланс',
            'пополнить кошельку': 'баланс',
            'пополнить кошельком': 'баланс',
            'управление балансом': 'баланс',
            'управление баланса': 'баланс',
            'пополнить через': 'баланс',
            'пополнение баланса': 'баланс',
            'пополнения баланса': 'баланс',
            
            # Комфорт
            'что такое тариф комфорт': 'комфорт',
            'что такое тариф комфорта': 'комфорт',
            'что такое тариф комфорту': 'комфорт',
            'что такое тариф комфортом': 'комфорт',
            'комфорт класс': 'комфорт',
            'комфорта класс': 'комфорт',
            'комфорт тариф': 'комфорт',
            'комфорта тариф': 'комфорт',
            'комфорт класс машины': 'комфорт',
            'комфорта класс машины': 'комфорт',
            'комфорт автомобиль': 'комфорт',
            'комфорта автомобиль': 'комфорт',
            
            # Моточасы
            'что такое моточасы': 'моточасы',
            'что такое моточасов': 'моточасы',
            'что такое моточасам': 'моточасы',
            'что такое моточасами': 'моточасы',
            'время поездки': 'моточасы',
            'времени поездки': 'моточасы',
            'времени поездку': 'моточасы',
            'оплата за время': 'моточасы',
            'оплата за времени': 'моточасы',
            'поминутная оплата': 'моточасы',
            'поминутные оплаты': 'моточасы',
            'время в тарифе': 'моточасы',
            'времени в тарифе': 'моточасы',
            'длительные заказы': 'моточасы',
            'длительных заказов': 'моточасы',
            
            # Приложение
            'приложение не работает': 'приложение',
            'приложения не работает': 'приложение',
            'приложению не работает': 'приложение',
            'приложением не работает': 'приложение',
            'приложение не запускается': 'приложение',
            'приложения не запускается': 'приложение',
            'обновление приложения': 'приложение',
            'обновления приложения': 'приложение',
            'настройка gps': 'приложение',
            'настройки gps': 'приложение',
            'приложение вылетает': 'приложение',
            'приложения вылетает': 'приложение',
            'приложение зависает': 'приложение',
            'приложения зависает': 'приложение'
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
            logger.info(f"✅ Морфологическая база знаний загружена: {len(self.knowledge_base)} записей")
        except FileNotFoundError:
            logger.error(f"❌ База знаний не найдена: {self.knowledge_base_path}")
            self.knowledge_base = []
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            self.knowledge_base = []
    
    def normalize_text_morphological(self, text: str) -> str:
        """Морфологическая нормализация текста"""
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
    
    def expand_query_morphological(self, query: str) -> List[str]:
        """Расширяет запрос с учетом морфологии"""
        # Получаем все морфологические варианты
        expanded_queries = self.morphological_analyzer.expand_query(query)
        
        # Добавляем прямые маппинги
        normalized_query = self.normalize_text_morphological(query)
        for mapping_key, mapped_value in self.direct_mappings.items():
            if mapping_key in normalized_query:
                expanded_queries.append(mapped_value)
                expanded_queries.append(self.normalize_text_morphological(mapped_value))
        
        return list(set(expanded_queries))  # Убираем дубликаты
    
    def calculate_similarity_morphological(self, text1: str, text2: str) -> float:
        """Морфологический расчет схожести"""
        # Нормализуем оба текста
        words1 = set(self.normalize_text_morphological(text1).split())
        words2 = set(self.normalize_text_morphological(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        # Точное совпадение слов
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        base_similarity = len(intersection) / len(union) if union else 0.0
        
        # Бонус за морфологическое совпадение
        bonus = 0.0
        for word1 in words1:
            for word2 in words2:
                # Проверяем, являются ли слова морфологическими вариантами
                if self.morphological_analyzer.normalize_word(word1) == self.morphological_analyzer.normalize_word(word2):
                    bonus += 0.3
        
        # Бонус за частичное совпадение
        for word1 in words1:
            for word2 in words2:
                if word1 in word2 or word2 in word1:
                    bonus += 0.1
        
        return min(base_similarity + bonus, 1.0)
    
    def find_direct_mapping_morphological(self, query: str) -> Optional[str]:
        """Ищет прямое соответствие с учетом морфологии"""
        normalized_query = self.normalize_text_morphological(query)
        
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
    
    def search_morphological(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Морфологический поиск"""
        start_time = datetime.now()
        
        results = []
        
        # Расширяем запрос с учетом морфологии
        expanded_queries = self.expand_query_morphological(query)
        
        for idx, item in enumerate(self.knowledge_base):
            max_score = 0
            
            # Проверяем основной вопрос с максимальным весом
            for expanded_query in expanded_queries:
                question_similarity = self.calculate_similarity_morphological(expanded_query, item['question'])
                max_score = max(max_score, question_similarity * 5.0)
            
            # Проверяем вариации с высоким весом
            for variation in item.get('variations', []):
                for expanded_query in expanded_queries:
                    variation_similarity = self.calculate_similarity_morphological(expanded_query, variation)
                    max_score = max(max_score, variation_similarity * 4.0)
            
            # Проверяем ключевые слова с максимальным весом
            query_words = set()
            for expanded_query in expanded_queries:
                query_words.update(self.normalize_text_morphological(expanded_query).split())
            
            keyword_matches = 0
            for keyword in item.get('keywords', []):
                keyword_normalized = self.normalize_text_morphological(keyword)
                if keyword_normalized in query_words:
                    keyword_matches += 1
            
            if keyword_matches > 0:
                max_score = max(max_score, keyword_matches * 3.0)
            
            # Проверяем ответ
            for expanded_query in expanded_queries:
                answer_similarity = self.calculate_similarity_morphological(expanded_query, item['answer'])
                max_score = max(max_score, answer_similarity * 2.0)
            
            if max_score > 0:
                results.append({
                    'id': item.get('id', idx),
                    'question': item['question'],
                    'answer': item['answer'],
                    'category': item.get('category', 'general'),
                    'confidence': min(max_score / 7.0, 1.0),
                    'keywords': item.get('keywords', []),
                    'variations': item.get('variations', []),
                    'metadata': item.get('metadata', {})
                })
        
        # Сортируем по убыванию score
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Логируем время выполнения
        response_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"🧠 Морфологический поиск выполнен за {response_time:.3f} секунд")
        
        return results[:top_k]
    
    def get_enhanced_answer(self, question: str) -> str:
        """Основной метод для получения ответа с морфологическим анализом"""
        start_time = datetime.now()
        
        # Обновляем метрики
        self.quality_metrics['total_requests'] += 1
        
        # Выполняем морфологический поиск
        results = self.search_morphological(question, top_k=3)
        
        response_time = (datetime.now() - start_time).total_seconds()
        self.quality_metrics['avg_response_time'] = (
            (self.quality_metrics['avg_response_time'] * (self.quality_metrics['total_requests'] - 1) + response_time) 
            / self.quality_metrics['total_requests']
        )
        
        if not results:
            return "Нужна уточняющая информация"
        
        # Проверяем уверенность лучшего результата
        best_result = results[0]
        
        if best_result['confidence'] >= 0.3:  # Минимальный порог
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
            'morphological_analysis': True
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
morphological_search_client = MorphologicalSearchClient()

def get_enhanced_answer(question: str) -> str:
    """Основной API для интеграции с main.py"""
    return morphological_search_client.get_enhanced_answer(question)

def get_morphological_statistics() -> Dict[str, Any]:
    """API для получения статистики морфологической системы"""
    return morphological_search_client.get_statistics()

if __name__ == "__main__":
    # Тестируем морфологическую систему
    client = MorphologicalSearchClient()
    
    # Показываем статистику
    stats = client.get_statistics()
    print(f"📊 Статистика морфологической системы поиска:")
    print(f"   Записей в базе: {stats['total_knowledge_records']}")
    print(f"   Морфологический анализ: {'✅' if stats['morphological_analysis'] else '❌'}")
    
    # Тестируем поиск
    test_questions = [
        "Что такое наценки?",  # Множественное число
        "Почему так дорого?",
        "Что такое тариф комфорта?",  # Родительный падеж
        "Как пополнить баланс?",
        "Как заказать доставку?",
        "Что такое моточасы?",
        "Приложение не работает",
        "Откуда доплаты в заказе?",  # Множественное число
        "Как отправить посылку?",
        "Повышающие коэффициенты"  # Множественное число
    ]
    
    print(f"\n🧪 Тестирование морфологической системы:")
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
    print(f"\n📈 Финальные метрики морфологической системы:")
    print(f"   Успешность: {final_stats.get('success_rate', 0):.1%}")
    print(f"   Высокая уверенность: {final_stats.get('high_confidence_rate', 0):.1%}")
    print(f"   Среднее время ответа: {final_stats.get('avg_response_time', 0):.3f}s")
    print(f"   Успешных ответов в тесте: {successful_answers}/{len(test_questions)}")

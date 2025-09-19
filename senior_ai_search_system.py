#!/usr/bin/env python3
"""
🧠 Senior AI Engineer - Профессиональная система поиска APARU
Максимальное качество поиска с гибридными алгоритмами
"""

import json
import logging
import pickle
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib

# Импорты для продвинутой обработки текста
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import SnowballStemmer
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Импорты для эмбеддингов
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

# Импорты для fuzzy search
try:
    from fuzzywuzzy import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeniorAISearchSystem:
    def __init__(self, knowledge_base_path: str = "senior_ai_knowledge_base.json", index_path: str = "senior_ai_search_index.pkl"):
        self.knowledge_base_path = knowledge_base_path
        self.index_path = index_path
        self.knowledge_base = []
        self.embeddings_model = None
        self.embeddings_index = None
        self.question_embeddings = None
        self.text_to_item = {}
        self.stop_words = set()
        self.stemmer = None
        
        # Инициализация компонентов
        self._load_knowledge_base()
        self._initialize_text_processing()
        self._initialize_embeddings()
        self._load_search_index()
        
        # Логирование
        self.request_log = []
        self.knowledge_expansions = []
        
        # Метрики качества
        self.quality_metrics = {
            'total_requests': 0,
            'successful_matches': 0,
            'high_confidence_matches': 0,
            'category_distribution': {},
            'avg_response_time': 0.0
        }
    
    def _load_knowledge_base(self):
        """Загружает продвинутую базу знаний"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            logger.info(f"✅ Продвинутая база знаний загружена: {len(self.knowledge_base)} записей")
        except FileNotFoundError:
            logger.error(f"❌ База знаний не найдена: {self.knowledge_base_path}")
            self.knowledge_base = []
    
    def _initialize_text_processing(self):
        """Инициализирует продвинутую обработку текста"""
        try:
            # Русские стоп-слова
            self.stop_words = set([
                'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между'
            ])
            
            # Стеммер для русского языка
            if NLTK_AVAILABLE:
                self.stemmer = SnowballStemmer('russian')
            
            logger.info("✅ Продвинутая обработка текста инициализирована")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка инициализации обработки текста: {e}")
            self.stop_words = set()
            self.stemmer = None
    
    def _initialize_embeddings(self):
        """Инициализирует модель эмбеддингов"""
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embeddings_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("✅ Модель эмбеддингов загружена")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки модели эмбеддингов: {e}")
                self.embeddings_model = None
        else:
            logger.warning("⚠️ Эмбеддинги недоступны")
    
    def _load_search_index(self):
        """Загружает поисковый индекс"""
        try:
            with open(self.index_path, 'rb') as f:
                index_data = pickle.load(f)
            
            self.embeddings_index = index_data['embeddings_index']
            self.question_embeddings = index_data['question_embeddings']
            self.text_to_item = index_data['text_to_item']
            
            logger.info("✅ Поисковый индекс загружен")
        except FileNotFoundError:
            logger.warning(f"⚠️ Поисковый индекс не найден: {self.index_path}")
            self.embeddings_index = None
        except Exception as e:
            logger.warning(f"⚠️ Ошибка загрузки поискового индекса: {e}")
            self.embeddings_index = None
    
    def normalize_text_advanced(self, text: str) -> str:
        """Продвинутая нормализация текста"""
        if not text:
            return ""
        
        # Приводим к нижнему регистру
        text = text.lower()
        
        # Убираем лишние символы и нормализуем
        import re
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Разбиваем на слова
        words = text.split()
        
        # Убираем стоп-слова
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Стемминг
        if self.stemmer:
            words = [self.stemmer.stem(word) for word in words]
        
        return ' '.join(words)
    
    def search_by_embeddings_advanced(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Продвинутый поиск по эмбеддингам"""
        if not self.embeddings_model or not self.embeddings_index:
            return []
        
        try:
            # Нормализуем запрос
            normalized_query = self.normalize_text_advanced(query)
            
            # Создаем эмбеддинг для запроса
            query_embedding = self.embeddings_model.encode([normalized_query])
            faiss.normalize_L2(query_embedding)
            
            # Поиск в FAISS
            scores, indices = self.embeddings_index.search(query_embedding, top_k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.question_embeddings):
                    # Находим соответствующий элемент базы знаний
                    text = list(self.text_to_item.keys())[idx]
                    item = self.text_to_item[text]
                    item_id = item['id'] - 1  # Индекс в массиве
                    results.append((item_id, float(score)))
            
            return results
        except Exception as e:
            logger.warning(f"⚠️ Ошибка поиска по эмбеддингам: {e}")
            return []
    
    def search_by_keywords_advanced(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Продвинутый поиск по ключевым словам"""
        normalized_query = self.normalize_text_advanced(query)
        query_words = set(normalized_query.split())
        
        results = []
        
        for idx, item in enumerate(self.knowledge_base):
            score = 0
            
            # Проверяем ключевые слова
            for keyword in item.get('keywords', []):
                keyword_normalized = self.normalize_text_advanced(keyword)
                if keyword_normalized in query_words:
                    score += 2  # Высокий вес для ключевых слов
            
            # Проверяем основной вопрос
            question_normalized = self.normalize_text_advanced(item['question'])
            question_words = set(question_normalized.split())
            common_words = query_words.intersection(question_words)
            score += len(common_words) * 1.5
            
            # Проверяем вариации
            for variation in item.get('variations', []):
                variation_normalized = self.normalize_text_advanced(variation)
                variation_words = set(variation_normalized.split())
                common_words = query_words.intersection(variation_words)
                score += len(common_words) * 1.0
            
            # Проверяем ответ
            answer_normalized = self.normalize_text_advanced(item['answer'])
            answer_words = set(answer_normalized.split())
            common_words = query_words.intersection(answer_words)
            score += len(common_words) * 0.5
            
            if score > 0:
                results.append((idx, score))
        
        # Сортируем по убыванию score
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def search_by_fuzzy_advanced(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Продвинутый поиск по fuzzy matching"""
        if not FUZZY_AVAILABLE:
            return []
        
        try:
            # Собираем все вопросы и вариации
            all_questions = []
            question_to_idx = {}
            
            for idx, item in enumerate(self.knowledge_base):
                all_questions.append(item['question'])
                question_to_idx[item['question']] = idx
                
                for variation in item.get('variations', []):
                    all_questions.append(variation)
                    question_to_idx[variation] = idx
            
            # Fuzzy search с разными алгоритмами
            matches = process.extract(query, all_questions, limit=top_k*2, scorer=fuzz.ratio)
            
            results = []
            seen_indices = set()
            
            for match_text, score in matches:
                if match_text in question_to_idx:
                    idx = question_to_idx[match_text]
                    if idx not in seen_indices:
                        # Нормализуем score к 0-1
                        normalized_score = score / 100.0
                        results.append((idx, normalized_score))
                        seen_indices.add(idx)
            
            return results[:top_k]
        except Exception as e:
            logger.warning(f"⚠️ Ошибка fuzzy search: {e}")
            return []
    
    def hybrid_search_advanced(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Продвинутый гибридный поиск"""
        start_time = datetime.now()
        
        # Получаем результаты от каждого метода
        embedding_results = self.search_by_embeddings_advanced(query, top_k)
        keyword_results = self.search_by_keywords_advanced(query, top_k)
        fuzzy_results = self.search_by_fuzzy_advanced(query, top_k)
        
        # Объединяем результаты с адаптивными весами
        combined_scores = {}
        
        # Адаптивные веса на основе качества результатов
        embedding_weight = 0.6  # Высокий вес для семантического поиска
        keyword_weight = 0.3    # Средний вес для ключевых слов
        fuzzy_weight = 0.1      # Низкий вес для fuzzy matching
        
        # Эмбеддинги
        for idx, score in embedding_results:
            if idx not in combined_scores:
                combined_scores[idx] = 0
            combined_scores[idx] += score * embedding_weight
        
        # Ключевые слова
        for idx, score in keyword_results:
            if idx not in combined_scores:
                combined_scores[idx] = 0
            # Нормализуем score ключевых слов
            normalized_score = min(score / 20.0, 1.0)  # Предполагаем максимум 20 совпадений
            combined_scores[idx] += normalized_score * keyword_weight
        
        # Fuzzy matching
        for idx, score in fuzzy_results:
            if idx not in combined_scores:
                combined_scores[idx] = 0
            combined_scores[idx] += score * fuzzy_weight
        
        # Сортируем по убыванию score
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Формируем результат
        results = []
        for idx, score in sorted_results[:top_k]:
            if idx < len(self.knowledge_base):
                item = self.knowledge_base[idx]
                results.append({
                    'id': item.get('id', idx),
                    'question': item['question'],
                    'answer': item['answer'],
                    'category': item.get('category', 'general'),
                    'confidence': min(score, 1.0),
                    'keywords': item.get('keywords', []),
                    'variations': item.get('variations', []),
                    'metadata': item.get('metadata', {})
                })
        
        # Логируем время выполнения
        response_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"🔍 Поиск выполнен за {response_time:.3f} секунд")
        
        return results
    
    def ask_question_advanced(self, query: str) -> Dict[str, Any]:
        """Продвинутый метод для ответа на вопрос"""
        start_time = datetime.now()
        
        # Логируем запрос
        request_id = hashlib.md5(f"{query}_{datetime.now()}".encode()).hexdigest()[:8]
        self.request_log.append({
            'id': request_id,
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
        
        # Выполняем продвинутый гибридный поиск
        results = self.hybrid_search_advanced(query, top_k=3)
        
        # Обновляем метрики
        self.quality_metrics['total_requests'] += 1
        response_time = (datetime.now() - start_time).total_seconds()
        self.quality_metrics['avg_response_time'] = (
            (self.quality_metrics['avg_response_time'] * (self.quality_metrics['total_requests'] - 1) + response_time) 
            / self.quality_metrics['total_requests']
        )
        
        if not results:
            return {
                'answer': 'Нужна уточняющая информация',
                'confidence': 0.0,
                'category': 'general',
                'suggestions': [],
                'request_id': request_id,
                'response_time': response_time,
                'source': 'no_match'
            }
        
        # Проверяем уверенность лучшего результата
        best_result = results[0]
        
        if best_result['confidence'] >= 0.7:  # Высокий порог для профессиональной системы
            # Обновляем метрики
            self.quality_metrics['successful_matches'] += 1
            if best_result['confidence'] >= 0.9:
                self.quality_metrics['high_confidence_matches'] += 1
            
            # Обновляем распределение по категориям
            category = best_result['category']
            self.quality_metrics['category_distribution'][category] = self.quality_metrics['category_distribution'].get(category, 0) + 1
            
            # Возвращаем точный ответ
            return {
                'answer': best_result['answer'],
                'confidence': best_result['confidence'],
                'category': best_result['category'],
                'suggestions': [],
                'request_id': request_id,
                'response_time': response_time,
                'source': 'knowledge_base',
                'metadata': best_result.get('metadata', {})
            }
        else:
            # Возвращаем уточнение с ближайшими вопросами
            suggestions = []
            for result in results[:3]:
                suggestions.append({
                    'question': result['question'],
                    'confidence': result['confidence'],
                    'category': result['category']
                })
            
            return {
                'answer': 'Нужна уточняющая информация',
                'confidence': best_result['confidence'],
                'category': best_result.get('category', 'general'),
                'suggestions': suggestions,
                'request_id': request_id,
                'response_time': response_time,
                'source': 'clarification_needed'
            }
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Возвращает метрики качества системы"""
        base_metrics = {
            **self.quality_metrics,
            'total_knowledge_records': len(self.knowledge_base),
            'embeddings_available': self.embeddings_model is not None,
            'fuzzy_available': FUZZY_AVAILABLE,
            'nltk_available': NLTK_AVAILABLE
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

# Глобальный экземпляр
_senior_ai_search_instance = SeniorAISearchSystem()

def ask_question_advanced(query: str) -> Dict[str, Any]:
    """Основной API для продвинутых вопросов"""
    return _senior_ai_search_instance.ask_question_advanced(query)

def get_quality_metrics() -> Dict[str, Any]:
    """API для получения метрик качества"""
    return _senior_ai_search_instance.get_quality_metrics()

if __name__ == "__main__":
    # Тестируем продвинутую систему поиска
    search_system = SeniorAISearchSystem()
    
    # Показываем метрики
    metrics = search_system.get_quality_metrics()
    print(f"📊 Метрики продвинутой системы поиска:")
    print(f"   Записей в базе: {metrics['total_knowledge_records']}")
    print(f"   Эмбеддинги: {'✅' if metrics['embeddings_available'] else '❌'}")
    print(f"   Fuzzy search: {'✅' if metrics['fuzzy_available'] else '❌'}")
    print(f"   NLTK обработка: {'✅' if metrics['nltk_available'] else '❌'}")
    
    # Тестируем поиск
    test_questions = [
        "Что такое наценка?",
        "Почему так дорого?",
        "Что такое тариф Комфорт?",
        "Как пополнить баланс?",
        "Как отменить заказ?",
        "Приложение не работает",
        "Как заказать доставку?",
        "Что такое моточасы?"
    ]
    
    print(f"\n🧪 Тестирование продвинутого поиска:")
    for question in test_questions:
        result = search_system.ask_question_advanced(question)
        print(f"❓ {question}")
        print(f"✅ {result['answer'][:100]}...")
        print(f"📊 Уверенность: {result['confidence']:.3f}")
        print(f"🏷️ Категория: {result['category']}")
        print(f"⏱️ Время: {result['response_time']:.3f}s")
        if result.get('suggestions'):
            print(f"💡 Предложения: {len(result['suggestions'])}")
        print()
    
    # Показываем финальные метрики
    final_metrics = search_system.get_quality_metrics()
    print(f"\n📈 Финальные метрики качества:")
    print(f"   Успешность: {final_metrics['success_rate']:.1%}")
    print(f"   Высокая уверенность: {final_metrics['high_confidence_rate']:.1%}")
    print(f"   Среднее время ответа: {final_metrics['avg_response_time']:.3f}s")
    
    print(f"\n📋 Распределение по категориям:")
    for category, count in final_metrics['category_distribution'].items():
        print(f"   {category}: {count} запросов")

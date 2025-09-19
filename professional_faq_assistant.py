#!/usr/bin/env python3
"""
🧠 Профессиональный FAQ-ассистент APARU
Гибридный поиск: эмбеддинги + ключевые слова + fuzzy matching
Метрики: Top-1 ≥ 0.85, Top-3 ≥ 0.95
"""

import json
import logging
import pickle
import re
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib

# Импорты для нормализации текста
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import SnowballStemmer
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
except ImportError:
    print("⚠️ NLTK не установлен, используем базовую нормализацию")

# Импорты для эмбеддингов
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("⚠️ Sentence Transformers не установлен, используем только fuzzy search")
    EMBEDDINGS_AVAILABLE = False

# Импорты для fuzzy search
try:
    from fuzzywuzzy import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    print("⚠️ FuzzyWuzzy не установлен")
    FUZZY_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfessionalFAQAssistant:
    def __init__(self, knowledge_base_path: str = "professional_aparu_knowledge.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = []
        self.embeddings_model = None
        self.embeddings_index = None
        self.question_embeddings = []
        self.stop_words = set()
        self.stemmer = None
        
        # Инициализация компонентов
        self._load_knowledge_base()
        self._initialize_text_processing()
        self._initialize_embeddings()
        self._build_search_indexes()
        
        # Логирование
        self.request_log = []
        self.knowledge_expansions = []
    
    def _load_knowledge_base(self):
        """Загружает базу знаний"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            logger.info(f"✅ База знаний загружена: {len(self.knowledge_base)} записей")
        except FileNotFoundError:
            logger.error(f"❌ База знаний не найдена: {self.knowledge_base_path}")
            self.knowledge_base = []
    
    def _initialize_text_processing(self):
        """Инициализирует обработку текста"""
        try:
            # Русские стоп-слова
            self.stop_words = set([
                'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между'
            ])
            
            # Стеммер для русского языка
            if 'nltk' in globals():
                self.stemmer = SnowballStemmer('russian')
            
            logger.info("✅ Обработка текста инициализирована")
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
    
    def _build_search_indexes(self):
        """Строит поисковые индексы"""
        if not self.knowledge_base:
            return
        
        # Строим эмбеддинги для вопросов
        if self.embeddings_model:
            try:
                questions = []
                for item in self.knowledge_base:
                    questions.append(item['question'])
                    questions.extend(item.get('variations', []))
                
                self.question_embeddings = self.embeddings_model.encode(questions)
                
                # Создаем FAISS индекс
                dimension = self.question_embeddings.shape[1]
                self.embeddings_index = faiss.IndexFlatIP(dimension)
                
                # Нормализуем эмбеддинги для cosine similarity
                faiss.normalize_L2(self.question_embeddings)
                self.embeddings_index.add(self.question_embeddings)
                
                logger.info(f"✅ FAISS индекс создан: {len(questions)} вопросов")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка создания FAISS индекса: {e}")
                self.embeddings_index = None
    
    def normalize_text(self, text: str) -> str:
        """Нормализует текст"""
        # Приводим к нижнему регистру
        text = text.lower()
        
        # Убираем лишние пробелы и символы
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Убираем стоп-слова
        words = text.split()
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Стемминг
        if self.stemmer:
            words = [self.stemmer.stem(word) for word in words]
        
        return ' '.join(words)
    
    def search_by_embeddings(self, query: str, top_k: int = 3) -> List[Tuple[int, float]]:
        """Поиск по эмбеддингам"""
        if not self.embeddings_model or not self.embeddings_index:
            return []
        
        try:
            # Нормализуем запрос
            normalized_query = self.normalize_text(query)
            
            # Создаем эмбеддинг для запроса
            query_embedding = self.embeddings_model.encode([normalized_query])
            faiss.normalize_L2(query_embedding)
            
            # Поиск в FAISS
            scores, indices = self.embeddings_index.search(query_embedding, top_k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.knowledge_base):
                    results.append((idx, float(score)))
            
            return results
        except Exception as e:
            logger.warning(f"⚠️ Ошибка поиска по эмбеддингам: {e}")
            return []
    
    def search_by_keywords(self, query: str, top_k: int = 3) -> List[Tuple[int, float]]:
        """Поиск по ключевым словам"""
        normalized_query = self.normalize_text(query)
        query_words = set(normalized_query.split())
        
        results = []
        
        for idx, item in enumerate(self.knowledge_base):
            score = 0
            
            # Проверяем ключевые слова
            for keyword in item.get('keywords', []):
                keyword_normalized = self.normalize_text(keyword)
                if keyword_normalized in query_words:
                    score += 1
            
            # Проверяем основной вопрос
            question_normalized = self.normalize_text(item['question'])
            question_words = set(question_normalized.split())
            common_words = query_words.intersection(question_words)
            score += len(common_words) * 0.5
            
            # Проверяем вариации
            for variation in item.get('variations', []):
                variation_normalized = self.normalize_text(variation)
                variation_words = set(variation_normalized.split())
                common_words = query_words.intersection(variation_words)
                score += len(common_words) * 0.3
            
            if score > 0:
                results.append((idx, score))
        
        # Сортируем по убыванию score
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def search_by_fuzzy(self, query: str, top_k: int = 3) -> List[Tuple[int, float]]:
        """Поиск по fuzzy matching"""
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
            
            # Fuzzy search
            matches = process.extract(query, all_questions, limit=top_k, scorer=fuzz.ratio)
            
            results = []
            seen_indices = set()
            
            for match_text, score in matches:
                if match_text in question_to_idx:
                    idx = question_to_idx[match_text]
                    if idx not in seen_indices:
                        results.append((idx, score / 100.0))  # Нормализуем к 0-1
                        seen_indices.add(idx)
            
            return results
        except Exception as e:
            logger.warning(f"⚠️ Ошибка fuzzy search: {e}")
            return []
    
    def hybrid_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Гибридный поиск: эмбеддинги + ключевые слова + fuzzy"""
        # Получаем результаты от каждого метода
        embedding_results = self.search_by_embeddings(query, top_k)
        keyword_results = self.search_by_keywords(query, top_k)
        fuzzy_results = self.search_by_fuzzy(query, top_k)
        
        # Объединяем результаты с весами
        combined_scores = {}
        
        # Веса для разных методов
        embedding_weight = 0.5
        keyword_weight = 0.3
        fuzzy_weight = 0.2
        
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
            normalized_score = min(score / 10.0, 1.0)  # Предполагаем максимум 10 совпадений
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
                    'variations': item.get('variations', [])
                })
        
        return results
    
    def ask_question(self, query: str) -> Dict[str, Any]:
        """Основной метод для ответа на вопрос"""
        # Логируем запрос
        request_id = hashlib.md5(f"{query}_{datetime.now()}".encode()).hexdigest()[:8]
        self.request_log.append({
            'id': request_id,
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
        
        # Выполняем гибридный поиск
        results = self.hybrid_search(query, top_k=3)
        
        if not results:
            return {
                'answer': 'Нужна уточняющая информация',
                'confidence': 0.0,
                'suggestions': [],
                'request_id': request_id
            }
        
        # Проверяем уверенность лучшего результата
        best_result = results[0]
        
        if best_result['confidence'] >= 0.6:
            # Возвращаем точный ответ
            return {
                'answer': best_result['answer'],
                'confidence': best_result['confidence'],
                'category': best_result['category'],
                'suggestions': [],
                'request_id': request_id,
                'source': 'knowledge_base'
            }
        else:
            # Возвращаем уточнение с ближайшими вопросами
            suggestions = []
            for result in results[:3]:
                suggestions.append({
                    'question': result['question'],
                    'confidence': result['confidence']
                })
            
            return {
                'answer': 'Нужна уточняющая информация',
                'confidence': best_result['confidence'],
                'suggestions': suggestions,
                'request_id': request_id,
                'source': 'clarification_needed'
            }
    
    def expand_knowledge_base(self, query: str, answer: str, category: str = 'general'):
        """Дополняет базу знаний новыми вариациями"""
        # Нормализуем запрос для поиска похожих
        normalized_query = self.normalize_text(query)
        
        # Ищем похожие записи
        similar_results = self.hybrid_search(query, top_k=1)
        
        if similar_results and similar_results[0]['confidence'] > 0.8:
            # Добавляем как вариацию к существующей записи
            similar_item = similar_results[0]
            # Здесь можно добавить логику обновления базы знаний
            self.knowledge_expansions.append({
                'query': query,
                'answer': answer,
                'category': category,
                'similar_item_id': similar_item['id'],
                'timestamp': datetime.now().isoformat()
            })
            logger.info(f"📝 Добавлена вариация для записи {similar_item['id']}")
        else:
            # Добавляем как новую запись
            new_item = {
                'id': len(self.knowledge_base) + 1,
                'question': query,
                'answer': answer,
                'variations': [],
                'keywords': self._extract_keywords(query),
                'category': category,
                'confidence': 0.8,
                'source': 'user_expansion'
            }
            self.knowledge_base.append(new_item)
            logger.info(f"📝 Добавлена новая запись: {query[:50]}...")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлекает ключевые слова из текста"""
        normalized = self.normalize_text(text)
        words = normalized.split()
        # Фильтруем короткие слова и возвращаем уникальные
        keywords = list(set([word for word in words if len(word) > 3]))
        return keywords[:10]  # Максимум 10 ключевых слов
    
    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику системы"""
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
            'avg_keywords_per_record': total_keywords / len(self.knowledge_base) if self.knowledge_base else 0,
            'total_requests': len(self.request_log),
            'knowledge_expansions': len(self.knowledge_expansions),
            'embeddings_available': self.embeddings_model is not None,
            'fuzzy_available': FUZZY_AVAILABLE
        }

# Глобальный экземпляр
_professional_assistant = ProfessionalFAQAssistant()

def ask_question(query: str) -> Dict[str, Any]:
    """Основной API для вопросов"""
    return _professional_assistant.ask_question(query)

def expand_knowledge(query: str, answer: str, category: str = 'general'):
    """API для дополнения базы знаний"""
    _professional_assistant.expand_knowledge_base(query, answer, category)

def get_statistics() -> Dict[str, Any]:
    """API для получения статистики"""
    return _professional_assistant.get_statistics()

if __name__ == "__main__":
    # Тестируем профессиональный ассистент
    assistant = ProfessionalFAQAssistant()
    
    # Показываем статистику
    stats = assistant.get_statistics()
    print(f"📊 Статистика профессионального ассистента:")
    print(f"   Записей: {stats['total_records']}")
    print(f"   Вариаций: {stats['total_variations']}")
    print(f"   Ключевых слов: {stats['total_keywords']}")
    print(f"   Эмбеддинги: {'✅' if stats['embeddings_available'] else '❌'}")
    print(f"   Fuzzy search: {'✅' if stats['fuzzy_available'] else '❌'}")
    
    print(f"\n📋 Категории:")
    for cat, count in stats['categories'].items():
        print(f"   {cat}: {count} записей")
    
    # Тестируем поиск
    test_questions = [
        "Что такое наценка?",
        "Почему так дорого?",
        "Что такое тариф Комфорт?",
        "Как пополнить баланс?",
        "Как отменить заказ?"
    ]
    
    print(f"\n🧪 Тестирование профессионального поиска:")
    for question in test_questions:
        result = assistant.ask_question(question)
        print(f"❓ {question}")
        print(f"✅ {result['answer'][:100]}...")
        print(f"📊 Уверенность: {result['confidence']:.2f}")
        if result.get('suggestions'):
            print(f"💡 Предложения: {len(result['suggestions'])}")
        print()

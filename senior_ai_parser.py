#!/usr/bin/env python3
"""
🚀 Профессиональный парсер JSON базы знаний APARU
Senior AI Engineer - максимальное качество обучения
"""

import json
import logging
import pickle
import numpy as np
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime
import hashlib

# Импорты для продвинутой обработки текста
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import SnowballStemmer
    from nltk.tokenize import word_tokenize
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
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

class SeniorAIParser:
    def __init__(self):
        self.knowledge_base = []
        self.embeddings_model = None
        self.embeddings_index = None
        self.question_embeddings = []
        self.stop_words = set()
        self.stemmer = None
        
        # Инициализация компонентов
        self._initialize_text_processing()
        self._initialize_embeddings()
    
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
                # Используем лучшую модель для русского языка
                self.embeddings_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("✅ Модель эмбеддингов загружена")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки модели эмбеддингов: {e}")
                self.embeddings_model = None
        else:
            logger.warning("⚠️ Эмбеддинги недоступны")
    
    def parse_json_knowledge_base(self, file_path: str = "BZ.txt") -> List[Dict[str, Any]]:
        """Парсит JSON базу знаний"""
        logger.info(f"📚 Парсим JSON базу знаний: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                logger.error("❌ Неверный формат JSON - ожидается массив")
                return []
            
            for i, item in enumerate(data):
                parsed_item = self._parse_knowledge_item(item, i + 1)
                if parsed_item:
                    self.knowledge_base.append(parsed_item)
            
            logger.info(f"✅ Парсинг завершен: {len(self.knowledge_base)} записей")
            return self.knowledge_base
            
        except FileNotFoundError:
            logger.error(f"❌ Файл не найден: {file_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка декодирования JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга: {e}")
            return []
    
    def _parse_knowledge_item(self, item: Dict[str, Any], item_id: int) -> Dict[str, Any]:
        """Парсит один элемент базы знаний"""
        try:
            # Извлекаем данные
            question_variations = item.get('question_variations', [])
            keywords = item.get('keywords', [])
            answer = item.get('answer', '')
            
            if not question_variations or not answer:
                logger.warning(f"⚠️ Элемент {item_id}: отсутствуют вариации вопросов или ответ")
                return None
            
            # Основной вопрос - первый в списке вариаций
            main_question = question_variations[0]
            
            # Расширенные ключевые слова
            expanded_keywords = self._expand_keywords(keywords, question_variations, answer)
            
            # Профессиональная категоризация
            category = self._categorize_question_advanced(main_question, answer, keywords)
            
            # Рассчитываем уверенность
            confidence = self._calculate_advanced_confidence(main_question, answer, keywords, question_variations)
            
            parsed_item = {
                'id': item_id,
                'question': main_question,
                'answer': answer,
                'variations': question_variations,
                'keywords': expanded_keywords,
                'category': category,
                'confidence': confidence,
                'source': 'BZ.txt',
                'metadata': {
                    'total_variations': len(question_variations),
                    'total_keywords': len(expanded_keywords),
                    'answer_length': len(answer),
                    'complexity_score': self._calculate_complexity_score(answer),
                    'parsed_at': datetime.now().isoformat()
                }
            }
            
            logger.info(f"✅ Элемент {item_id} обработан: {main_question[:50]}...")
            return parsed_item
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки элемента {item_id}: {e}")
            return None
    
    def _expand_keywords(self, keywords: List[str], variations: List[str], answer: str) -> List[str]:
        """Расширяет ключевые слова на основе вариаций и ответа"""
        expanded = set(keywords)
        
        # Добавляем ключевые слова из вариаций
        for variation in variations:
            words = self._extract_keywords_from_text(variation)
            expanded.update(words)
        
        # Добавляем ключевые слова из ответа
        answer_words = self._extract_keywords_from_text(answer)
        expanded.update(answer_words)
        
        # Фильтруем и сортируем
        filtered_keywords = [kw for kw in expanded if len(kw) > 2 and kw not in self.stop_words]
        return sorted(list(set(filtered_keywords)))[:20]  # Максимум 20 ключевых слов
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Извлекает ключевые слова из текста"""
        if not text:
            return []
        
        # Нормализуем текст
        text = text.lower()
        
        # Убираем пунктуацию и разбиваем на слова
        import re
        words = re.findall(r'\b\w+\b', text)
        
        # Фильтруем стоп-слова и короткие слова
        keywords = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Стемминг если доступен
        if self.stemmer:
            keywords = [self.stemmer.stem(word) for word in keywords]
        
        return keywords
    
    def _categorize_question_advanced(self, question: str, answer: str, keywords: List[str]) -> str:
        """Продвинутая категоризация вопросов"""
        text = (question + " " + answer + " ".join(keywords)).lower()
        
        # Расширенные категории с ключевыми словами
        categories = {
            'pricing': ['наценка', 'цена', 'стоимость', 'расценка', 'дорого', 'дешево', 'тариф', 'комфорт', 'коэффициент', 'доплата', 'надбавка', 'спрос', 'подорожание'],
            'booking': ['заказ', 'поездка', 'такси', 'вызов', 'предварительный', 'отменить', 'зарегистрировать', 'доставка', 'курьер', 'посылка'],
            'payment': ['баланс', 'пополнить', 'оплата', 'платеж', 'карта', 'qiwi', 'kaspi', 'терминал', 'id', 'единица', 'касса24'],
            'technical': ['приложение', 'таксометр', 'моточасы', 'gps', 'не работает', 'обновить', 'вылетает', 'зависает', 'google play', 'app store'],
            'delivery': ['доставка', 'курьер', 'посылка', 'отправить', 'получатель', 'телефон', 'откуда', 'куда'],
            'driver': ['водитель', 'контакты', 'связь', 'принимать заказы', 'работать', 'регистрация', 'лента заказов', 'клиент', 'пробный'],
            'cancellation': ['отменить', 'отмена', 'отказ', 'прекратить'],
            'complaint': ['жалоба', 'проблема', 'недоволен', 'плохо'],
            'general': ['здравствуйте', 'спасибо', 'вопрос', 'информация', 'расценка', 'стоимость', 'цена', 'таксометр', 'калькулятор']
        }
        
        # Подсчитываем совпадения для каждой категории
        category_scores = {}
        for category, cat_keywords in categories.items():
            score = sum(1 for kw in cat_keywords if kw in text)
            category_scores[category] = score
        
        # Возвращаем категорию с наибольшим количеством совпадений
        best_category = max(category_scores, key=category_scores.get)
        return best_category if category_scores[best_category] > 0 else 'general'
    
    def _calculate_advanced_confidence(self, question: str, answer: str, keywords: List[str], variations: List[str]) -> float:
        """Рассчитывает продвинутую уверенность"""
        confidence = 0.8  # Базовый высокий уровень для профессиональной системы
        
        # Увеличиваем уверенность за структуру ответа
        if 'здравствуйте' in answer.lower():
            confidence += 0.05
        if 'команда апару' in answer.lower():
            confidence += 0.05
        if 'с уважением' in answer.lower():
            confidence += 0.05
        
        # Увеличиваем уверенность за длину и детализацию ответа
        if len(answer) > 200:
            confidence += 0.05
        if len(answer) > 400:
            confidence += 0.05
        
        # Увеличиваем уверенность за количество вариаций
        if len(variations) > 10:
            confidence += 0.05
        if len(variations) > 15:
            confidence += 0.05
        
        # Увеличиваем уверенность за количество ключевых слов
        if len(keywords) > 5:
            confidence += 0.05
        if len(keywords) > 10:
            confidence += 0.05
        
        # Увеличиваем уверенность за сложность вопроса
        complexity = self._calculate_complexity_score(question)
        if complexity > 0.7:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Рассчитывает сложность текста"""
        if not text:
            return 0.0
        
        # Простая метрика сложности
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        avg_sentence_length = len(words) / sentence_count if sentence_count > 0 else len(words)
        
        # Нормализуем к 0-1
        complexity = (avg_word_length / 10.0 + avg_sentence_length / 20.0) / 2.0
        return min(complexity, 1.0)
    
    def build_advanced_search_index(self):
        """Строит продвинутый поисковый индекс"""
        if not self.knowledge_base:
            logger.warning("⚠️ База знаний пуста, индекс не создан")
            return
        
        logger.info("🔍 Строим продвинутый поисковый индекс")
        
        # Строим эмбеддинги для всех вопросов и вариаций
        if self.embeddings_model:
            try:
                all_texts = []
                text_to_item = {}
                
                for item in self.knowledge_base:
                    # Основной вопрос
                    all_texts.append(item['question'])
                    text_to_item[item['question']] = item
                    
                    # Вариации
                    for variation in item['variations']:
                        all_texts.append(variation)
                        text_to_item[variation] = item
                
                # Создаем эмбеддинги
                self.question_embeddings = self.embeddings_model.encode(all_texts)
                
                # Создаем FAISS индекс
                dimension = self.question_embeddings.shape[1]
                self.embeddings_index = faiss.IndexFlatIP(dimension)
                
                # Нормализуем эмбеддинги для cosine similarity
                faiss.normalize_L2(self.question_embeddings)
                self.embeddings_index.add(self.question_embeddings)
                
                # Сохраняем маппинг
                self.text_to_item = text_to_item
                
                logger.info(f"✅ Продвинутый индекс создан: {len(all_texts)} текстов")
                
            except Exception as e:
                logger.warning(f"⚠️ Ошибка создания продвинутого индекса: {e}")
                self.embeddings_index = None
    
    def save_advanced_knowledge_base(self, output_path: str = "senior_ai_knowledge_base.json"):
        """Сохраняет продвинутую базу знаний"""
        logger.info(f"💾 Сохраняем продвинутую базу знаний: {output_path}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Продвинутая база знаний сохранена: {len(self.knowledge_base)} записей")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения базы знаний: {e}")
            return None
    
    def save_search_index(self, output_path: str = "senior_ai_search_index.pkl"):
        """Сохраняет поисковый индекс"""
        if not self.embeddings_index:
            logger.warning("⚠️ Поисковый индекс не создан")
            return None
        
        try:
            index_data = {
                'embeddings_index': self.embeddings_index,
                'question_embeddings': self.question_embeddings,
                'text_to_item': self.text_to_item
            }
            
            with open(output_path, 'wb') as f:
                pickle.dump(index_data, f)
            
            logger.info(f"✅ Поисковый индекс сохранен: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения поискового индекса: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает подробную статистику"""
        if not self.knowledge_base:
            return {'error': 'База знаний пуста'}
        
        categories = {}
        total_variations = 0
        total_keywords = 0
        total_answer_length = 0
        complexity_scores = []
        
        for item in self.knowledge_base:
            cat = item['category']
            categories[cat] = categories.get(cat, 0) + 1
            total_variations += len(item['variations'])
            total_keywords += len(item['keywords'])
            total_answer_length += len(item['answer'])
            complexity_scores.append(item['metadata']['complexity_score'])
        
        return {
            'total_records': len(self.knowledge_base),
            'categories': categories,
            'total_variations': total_variations,
            'total_keywords': total_keywords,
            'avg_variations_per_record': total_variations / len(self.knowledge_base),
            'avg_keywords_per_record': total_keywords / len(self.knowledge_base),
            'avg_answer_length': total_answer_length / len(self.knowledge_base),
            'avg_complexity_score': sum(complexity_scores) / len(complexity_scores),
            'embeddings_available': self.embeddings_model is not None,
            'fuzzy_available': FUZZY_AVAILABLE,
            'nltk_available': NLTK_AVAILABLE
        }

if __name__ == "__main__":
    parser = SeniorAIParser()
    
    print("🚀 Senior AI Engineer - Парсинг JSON базы знаний APARU")
    print("=" * 70)
    
    # Парсим JSON базу знаний
    parsed_data = parser.parse_json_knowledge_base("BZ.txt")
    
    if parsed_data:
        # Строим продвинутый поисковый индекс
        parser.build_advanced_search_index()
        
        # Сохраняем результаты
        json_path = parser.save_advanced_knowledge_base()
        index_path = parser.save_search_index()
        
        print(f"\n🎯 Парсинг завершен успешно!")
        print(f"📁 JSON: {json_path}")
        print(f"🔍 Индекс: {index_path}")
        
        # Показываем статистику
        stats = parser.get_statistics()
        print(f"\n📊 Статистика:")
        print(f"   Записей: {stats['total_records']}")
        print(f"   Вариаций: {stats['total_variations']}")
        print(f"   Ключевых слов: {stats['total_keywords']}")
        print(f"   Среднее вариаций на запись: {stats['avg_variations_per_record']:.1f}")
        print(f"   Среднее ключевых слов на запись: {stats['avg_keywords_per_record']:.1f}")
        print(f"   Средняя длина ответа: {stats['avg_answer_length']:.0f} символов")
        print(f"   Средняя сложность: {stats['avg_complexity_score']:.2f}")
        
        print(f"\n📋 Категории:")
        for cat, count in stats['categories'].items():
            print(f"   {cat}: {count} записей")
        
        print(f"\n🔧 Технические возможности:")
        print(f"   Эмбеддинги: {'✅' if stats['embeddings_available'] else '❌'}")
        print(f"   Fuzzy search: {'✅' if stats['fuzzy_available'] else '❌'}")
        print(f"   NLTK обработка: {'✅' if stats['nltk_available'] else '❌'}")
        
        # Показываем примеры
        print(f"\n📝 Примеры обработанных записей:")
        for i, item in enumerate(parsed_data[:3]):
            print(f"   {i+1}. {item['question']}")
            print(f"      Ответ: {item['answer'][:100]}...")
            print(f"      Категория: {item['category']}")
            print(f"      Вариаций: {len(item['variations'])}")
            print(f"      Ключевых слов: {len(item['keywords'])}")
            print(f"      Уверенность: {item['confidence']:.3f}")
            print()
    else:
        print("❌ Ошибка парсинга!")

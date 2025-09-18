#!/usr/bin/env python3
"""
🧠 APARU Knowledge Base Training System
Обучение LLM на базе данных поддержки такси
"""

import json
import sqlite3
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os

class TaxiKnowledgeBase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.knowledge_base = []
        self.logger = logging.getLogger(__name__)
        
    def load_from_database(self, db_path: str):
        """Загружает данные из базы данных"""
        self.logger.info(f"Загружаю данные из {db_path}")
        
        try:
            # Подключение к базе данных
            conn = sqlite3.connect(db_path)
            
            # Получаем все таблицы
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.logger.info(f"Найдено таблиц: {len(tables)}")
            
            # Загружаем данные из каждой таблицы
            for table_name in tables:
                table_name = table_name[0]
                self.logger.info(f"Обрабатываю таблицу: {table_name}")
                
                # Получаем структуру таблицы
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Получаем данные
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                
                # Обрабатываем данные
                self._process_table_data(table_name, df, columns)
            
            conn.close()
            self.logger.info(f"Загружено {len(self.knowledge_base)} записей")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки базы данных: {e}")
            raise
    
    def load_from_csv(self, csv_path: str):
        """Загружает данные из CSV файла"""
        self.logger.info(f"Загружаю данные из {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            
            # Предполагаем структуру: question, answer, category, etc.
            for _, row in df.iterrows():
                knowledge_item = {
                    'question': str(row.get('question', '')),
                    'answer': str(row.get('answer', '')),
                    'category': str(row.get('category', 'general')),
                    'keywords': str(row.get('keywords', '')).split(',') if row.get('keywords') else [],
                    'source': 'csv',
                    'id': len(self.knowledge_base)
                }
                self.knowledge_base.append(knowledge_item)
            
            self.logger.info(f"Загружено {len(self.knowledge_base)} записей из CSV")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки CSV: {e}")
            raise
    
    def load_from_json(self, json_path: str):
        """Загружает данные из JSON файла"""
        self.logger.info(f"Загружаю данные из {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for item in data:
                    self.knowledge_base.append(self._normalize_knowledge_item(item))
            elif isinstance(data, dict):
                # Предполагаем структуру с ключами
                for key, value in data.items():
                    if isinstance(value, list):
                        for item in value:
                            item['category'] = key
                            self.knowledge_base.append(self._normalize_knowledge_item(item))
            
            self.logger.info(f"Загружено {len(self.knowledge_base)} записей из JSON")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки JSON: {e}")
            raise
    
    def _process_table_data(self, table_name: str, df: pd.DataFrame, columns: List):
        """Обрабатывает данные из таблицы базы данных"""
        
        # Определяем структуру на основе названий колонок
        question_col = None
        answer_col = None
        category_col = None
        
        for col in columns:
            col_name = col[1].lower()
            if 'question' in col_name or 'вопрос' in col_name:
                question_col = col[1]
            elif 'answer' in col_name or 'ответ' in col_name or 'reply' in col_name:
                answer_col = col[1]
            elif 'category' in col_name or 'категория' in col_name or 'type' in col_name:
                category_col = col[1]
        
        # Обрабатываем каждую строку
        for _, row in df.iterrows():
            knowledge_item = {
                'question': str(row.get(question_col, '')),
                'answer': str(row.get(answer_col, '')),
                'category': str(row.get(category_col, table_name)),
                'keywords': [],
                'source': f'db_{table_name}',
                'id': len(self.knowledge_base)
            }
            
            # Извлекаем ключевые слова из вопроса
            if knowledge_item['question']:
                keywords = self._extract_keywords(knowledge_item['question'])
                knowledge_item['keywords'] = keywords
            
            self.knowledge_base.append(knowledge_item)
    
    def _normalize_knowledge_item(self, item: Dict) -> Dict:
        """Нормализует элемент базы знаний"""
        normalized = {
            'question': str(item.get('question', '')),
            'answer': str(item.get('answer', '')),
            'category': str(item.get('category', 'general')),
            'keywords': item.get('keywords', []),
            'source': str(item.get('source', 'json')),
            'id': len(self.knowledge_base)
        }
        
        # Извлекаем ключевые слова если их нет
        if not normalized['keywords'] and normalized['question']:
            normalized['keywords'] = self._extract_keywords(normalized['question'])
        
        return normalized
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлекает ключевые слова из текста"""
        # Простое извлечение ключевых слов
        import re
        
        # Убираем знаки препинания и приводим к нижнему регистру
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Фильтруем короткие слова и стоп-слова
        stop_words = {'и', 'в', 'на', 'с', 'по', 'для', 'от', 'до', 'как', 'что', 'где', 'когда', 'почему'}
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords[:10]  # Максимум 10 ключевых слов
    
    def build_embeddings_index(self):
        """Строит индекс эмбеддингов для поиска"""
        self.logger.info("Строю индекс эмбеддингов...")
        
        if not self.knowledge_base:
            raise ValueError("База знаний пуста")
        
        # Создаем тексты для эмбеддингов
        texts = []
        for item in self.knowledge_base:
            # Комбинируем вопрос, ответ и ключевые слова
            text = f"{item['question']} {item['answer']} {' '.join(item['keywords'])}"
            texts.append(text)
        
        # Генерируем эмбеддинги
        self.logger.info("Генерирую эмбеддинги...")
        embeddings = self.embeddings_model.encode(texts)
        
        # Создаем FAISS индекс
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product для косинусного сходства
        
        # Нормализуем эмбеддинги для косинусного сходства
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        self.logger.info(f"Индекс построен: {self.index.ntotal} векторов")
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """Ищет похожие записи в базе знаний"""
        if self.index is None:
            raise ValueError("Индекс не построен")
        
        # Генерируем эмбеддинг для запроса
        query_embedding = self.embeddings_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Ищем похожие векторы
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Возвращаем результаты
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.knowledge_base):
                result = self.knowledge_base[idx].copy()
                result['similarity_score'] = float(score)
                results.append(result)
        
        return results
    
    def save_index(self, path: str):
        """Сохраняет индекс и базу знаний"""
        self.logger.info(f"Сохраняю индекс в {path}")
        
        data = {
            'knowledge_base': self.knowledge_base,
            'index': self.index
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        
        self.logger.info("Индекс сохранен")
    
    def load_index(self, path: str):
        """Загружает индекс и базу знаний"""
        self.logger.info(f"Загружаю индекс из {path}")
        
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.knowledge_base = data['knowledge_base']
        self.index = data['index']
        
        self.logger.info(f"Индекс загружен: {len(self.knowledge_base)} записей")
    
    def generate_training_data(self, output_path: str):
        """Генерирует данные для обучения LLM"""
        self.logger.info("Генерирую данные для обучения...")
        
        training_data = []
        
        for item in self.knowledge_base:
            # Создаем промпт для обучения
            prompt = f"""Ты - ИИ-ассистент службы поддержки такси-сервиса.

Вопрос: {item['question']}
Ответ: {item['answer']}

Категория: {item['category']}
Ключевые слова: {', '.join(item['keywords'])}

Правила ответа:
- Отвечай кратко и по делу
- Будь вежливым и профессиональным
- Используй информацию из базы знаний
- Если не знаешь ответа, предложи связаться с оператором"""
            
            training_data.append({
                'prompt': prompt,
                'question': item['question'],
                'answer': item['answer'],
                'category': item['category'],
                'keywords': item['keywords']
            })
        
        # Сохраняем данные
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Данные для обучения сохранены в {output_path}")
        return training_data
    
    def get_statistics(self) -> Dict:
        """Возвращает статистику базы знаний"""
        if not self.knowledge_base:
            return {}
        
        categories = {}
        total_questions = len(self.knowledge_base)
        
        for item in self.knowledge_base:
            category = item['category']
            categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_questions': total_questions,
            'categories': categories,
            'avg_keywords_per_item': np.mean([len(item['keywords']) for item in self.knowledge_base]),
            'sources': list(set([item['source'] for item in self.knowledge_base]))
        }

def main():
    """Пример использования"""
    logging.basicConfig(level=logging.INFO)
    
    # Создаем экземпляр
    kb = TaxiKnowledgeBase()
    
    # Загружаем данные (выберите один из способов)
    # kb.load_from_database('support_database.db')
    # kb.load_from_csv('support_data.csv')
    # kb.load_from_json('support_data.json')
    
    # Строим индекс
    kb.build_embeddings_index()
    
    # Сохраняем индекс
    kb.save_index('taxi_knowledge_index.pkl')
    
    # Генерируем данные для обучения
    kb.generate_training_data('training_data.json')
    
    # Показываем статистику
    stats = kb.get_statistics()
    print("Статистика базы знаний:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # Тестируем поиск
    query = "Где мой водитель?"
    results = kb.search_similar(query, top_k=3)
    
    print(f"\nРезультаты поиска для '{query}':")
    for result in results:
        print(f"Score: {result['similarity_score']:.3f}")
        print(f"Question: {result['question']}")
        print(f"Answer: {result['answer']}")
        print("-" * 50)

if __name__ == "__main__":
    main()

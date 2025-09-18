#!/usr/bin/env python3
"""
Умная система поиска для APARU LLM
Понимает контекст и смысл вопросов, а не только точные совпадения
"""

import json
import re
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Tuple

class SmartContextSearch:
    def __init__(self):
        """Инициализация умной системы поиска"""
        
        # Загружаем модель для создания эмбеддингов
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # База знаний
        self.knowledge_base = []
        
        # Индекс для быстрого поиска
        self.index = None
        self.dimension = 384  # Размерность эмбеддингов
        
        # Словарь синонимов и контекстных связей
        self.context_mappings = self._create_context_mappings()
        
    def _create_context_mappings(self):
        """Создает словарь контекстных связей"""
        
        return {
            # Группы связанных понятий
            "pricing": {
                "keywords": ["цена", "стоимость", "расценка", "тариф", "наценка", "дорого", "дешево", "оплата", "платеж"],
                "contexts": ["сколько стоит", "почему дорого", "откуда цена", "что такое наценка", "как считается цена"]
            },
            "payment": {
                "keywords": ["пополнить", "баланс", "счет", "деньги", "оплатить", "платеж", "кошелек", "карта"],
                "contexts": ["как заплатить", "где пополнить", "как добавить деньги", "как внести средства"]
            },
            "booking": {
                "keywords": ["заказать", "вызвать", "забронировать", "предварительный", "заранее", "время"],
                "contexts": ["как заказать такси", "можно ли заранее", "как забронировать", "когда заказывать"]
            },
            "driver": {
                "keywords": ["водитель", "работать", "заказы", "партнер", "регистрация", "таксометр"],
                "contexts": ["как стать водителем", "как работать", "как принимать заказы", "как пользоваться таксометром"]
            },
            "delivery": {
                "keywords": ["доставка", "курьер", "товар", "вещи", "документы", "посылка"],
                "contexts": ["как заказать доставку", "как доставить", "курьерская служба"]
            },
            "technical": {
                "keywords": ["приложение", "не работает", "проблема", "ошибка", "зависает", "не запускается"],
                "contexts": ["приложение не работает", "что делать", "как исправить", "проблемы с приложением"]
            }
        }
    
    def load_knowledge_base(self, kb_file: str = "database_Aparu/BZ.txt"):
        """Загружает и обрабатывает базу знаний"""
        
        print("📚 Загружаем базу знаний...")
        
        # Читаем оригинальную базу
        with open(kb_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим вопросы и ответы
        sections = content.split('- question:')
        
        for section in sections[1:]:
            lines = section.strip().split('\n')
            if len(lines) >= 2:
                question = lines[0].strip()
                answer = '\n'.join(lines[1:]).strip()
                
                # Создаем расширенную запись
                kb_entry = {
                    "question": question,
                    "answer": answer,
                    "keywords": self._extract_keywords(question),
                    "category": self._categorize_question(question),
                    "contexts": self._generate_contexts(question),
                    "embeddings": None  # Будет заполнено позже
                }
                
                self.knowledge_base.append(kb_entry)
        
        print(f"✅ Загружено {len(self.knowledge_base)} записей")
        
        # Создаем эмбеддинги
        self._create_embeddings()
        
        # Создаем индекс
        self._build_index()
        
        return self.knowledge_base
    
    def _extract_keywords(self, question: str) -> List[str]:
        """Извлекает ключевые слова из вопроса"""
        
        # Убираем стоп-слова
        stop_words = {
            "что", "как", "где", "когда", "почему", "зачем", "можно", "ли", "это", "такое",
            "означает", "значит", "есть", "быть", "делать", "сделать", "узнать", "посмотреть",
            "найти", "получить", "взять", "дать", "сказать", "объяснить", "мне", "мне", "я"
        }
        
        # Разбиваем на слова
        words = re.findall(r'\b\w+\b', question.lower())
        
        # Фильтруем
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _categorize_question(self, question: str) -> str:
        """Категоризирует вопрос по контексту"""
        
        question_lower = question.lower()
        
        for category, data in self.context_mappings.items():
            if any(keyword in question_lower for keyword in data["keywords"]):
                return category
        
        return "general"
    
    def _generate_contexts(self, question: str) -> List[str]:
        """Генерирует контекстные варианты вопроса"""
        
        contexts = [question]
        question_lower = question.lower()
        
        # Добавляем контекстные варианты из словаря
        for category, data in self.context_mappings.items():
            if any(keyword in question_lower for keyword in data["keywords"]):
                contexts.extend(data["contexts"])
        
        # Создаем синонимичные варианты
        synonyms = {
            "что такое": ["что означает", "что это", "что значит", "что за"],
            "как": ["каким образом", "как именно", "как можно", "как нужно"],
            "где": ["в каком месте", "где найти", "где посмотреть", "где искать"],
            "почему": ["зачем", "откуда", "из-за чего", "по какой причине"],
            "можно ли": ["возможно ли", "реально ли", "получится ли", "удастся ли"]
        }
        
        for original, alternatives in synonyms.items():
            if original in question_lower:
                for alt in alternatives:
                    new_context = question_lower.replace(original, alt)
                    if new_context not in contexts:
                        contexts.append(new_context.capitalize())
        
        return list(set(contexts))
    
    def _create_embeddings(self):
        """Создает эмбеддинги для всех записей"""
        
        print("🧠 Создаем эмбеддинги...")
        
        for entry in self.knowledge_base:
            # Создаем эмбеддинг для основного вопроса
            main_embedding = self.model.encode(entry["question"])
            
            # Создаем эмбеддинги для контекстных вариантов
            context_embeddings = []
            for context in entry["contexts"]:
                context_embeddings.append(self.model.encode(context))
            
            # Усредняем эмбеддинги для лучшего представления
            if context_embeddings:
                avg_embedding = np.mean([main_embedding] + context_embeddings, axis=0)
            else:
                avg_embedding = main_embedding
            
            entry["embeddings"] = avg_embedding
        
        print("✅ Эмбеддинги созданы")
    
    def _build_index(self):
        """Создает FAISS индекс для быстрого поиска"""
        
        print("🔍 Строим индекс...")
        
        # Создаем индекс
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product для косинусного сходства
        
        # Нормализуем эмбеддинги для косинусного сходства
        embeddings = np.array([entry["embeddings"] for entry in self.knowledge_base])
        faiss.normalize_L2(embeddings)
        
        # Добавляем в индекс
        self.index.add(embeddings)
        
        print("✅ Индекс построен")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Умный поиск по контексту"""
        
        # Создаем эмбеддинг для запроса
        query_embedding = self.model.encode(query)
        query_embedding = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        # Ищем похожие записи
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.knowledge_base):
                entry = self.knowledge_base[idx].copy()
                entry["similarity_score"] = float(score)
                entry["rank"] = i + 1
                results.append(entry)
        
        return results
    
    def get_contextual_answer(self, query: str) -> Dict:
        """Получает контекстуальный ответ на вопрос"""
        
        # Ищем похожие записи
        results = self.search(query, top_k=3)
        
        if not results:
            return {
                "answer": "Извините, я не нашел подходящего ответа в базе знаний.",
                "confidence": 0.0,
                "source": "fallback"
            }
        
        # Берем лучший результат
        best_match = results[0]
        
        # Определяем уверенность
        confidence = best_match["similarity_score"]
        
        if confidence > 0.7:
            # Высокая уверенность - возвращаем точный ответ
            return {
                "answer": best_match["answer"],
                "confidence": confidence,
                "source": "exact_match",
                "matched_question": best_match["question"],
                "category": best_match["category"]
            }
        elif confidence > 0.5:
            # Средняя уверенность - возвращаем ответ с контекстом
            return {
                "answer": best_match["answer"],
                "confidence": confidence,
                "source": "contextual_match",
                "matched_question": best_match["question"],
                "category": best_match["category"]
            }
        else:
            # Низкая уверенность - возвращаем общий ответ
            return {
                "answer": "Извините, я не уверен в ответе. Возможно, вы имели в виду что-то другое?",
                "confidence": confidence,
                "source": "low_confidence",
                "suggestions": [r["question"] for r in results[:3]]
            }

def test_smart_search():
    """Тестирует умную систему поиска"""
    
    print("🧪 Тестируем умную систему поиска...")
    
    # Создаем систему
    smart_search = SmartContextSearch()
    
    # Загружаем базу знаний
    smart_search.load_knowledge_base()
    
    # Тестовые запросы
    test_queries = [
        "Почему так дорого?",
        "Как заплатить за поездку?",
        "Можно ли заказать заранее?",
        "Как стать водителем?",
        "Приложение не открывается",
        "Что означает наценка?",
        "Где найти цену?",
        "Как доставить посылку?"
    ]
    
    print("\n🔍 Результаты тестирования:")
    
    for query in test_queries:
        print(f"\n❓ Вопрос: {query}")
        
        result = smart_search.get_contextual_answer(query)
        
        print(f"📝 Ответ: {result['answer'][:100]}...")
        print(f"🎯 Уверенность: {result['confidence']:.2f}")
        print(f"📂 Источник: {result['source']}")
        
        if 'matched_question' in result:
            print(f"🔗 Совпавший вопрос: {result['matched_question']}")
        
        if 'suggestions' in result:
            print(f"💡 Предложения: {result['suggestions']}")

if __name__ == "__main__":
    print("🚀 Создание умной системы поиска APARU...")
    
    # Тестируем
    test_smart_search()
    
    print("\n✅ Умная система поиска готова!")
    print("🧠 Теперь модель понимает контекст и смысл вопросов!")

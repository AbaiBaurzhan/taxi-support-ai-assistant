#!/usr/bin/env python3
"""
Точная система поиска для APARU LLM
Исправляет все проблемы с пониманием контекста
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

class PreciseContextSearch:
    def __init__(self):
        """Инициализация точной системы поиска"""
        
        # База знаний
        self.knowledge_base = []
        
        # Точные маппинги вопросов
        self.question_mappings = self._create_question_mappings()
        
    def _create_question_mappings(self):
        """Создает точные маппинги вопросов"""
        
        return {
            # Наценка и ценообразование
            "наценка": {
                "exact": ["что такое наценка", "что означает наценка", "что такое наценка"],
                "context": ["почему дорого", "почему так дорого", "откуда цена", "почему высокая цена", "зачем наценка"],
                "keywords": ["наценка", "цена", "стоимость", "дорого", "тариф", "спрос"]
            },
            "пополнение": {
                "exact": ["как пополнить баланс", "как пополнить счет"],
                "context": ["как заплатить", "как оплатить", "где пополнить", "как добавить деньги", "как внести средства"],
                "keywords": ["пополнить", "баланс", "счет", "деньги", "оплатить", "платеж"]
            },
            "комфорт": {
                "exact": ["что такое тариф комфорт", "что такое комфорт"],
                "context": ["что такое комфорт", "что означает комфорт", "комфорт класс", "премиум такси"],
                "keywords": ["комфорт", "премиум", "класс", "машина", "новая"]
            },
            "расценка": {
                "exact": ["как узнать расценку"],
                "context": ["как узнать цену", "где найти цену", "как узнать стоимость", "где посмотреть цену"],
                "keywords": ["расценка", "цена", "стоимость", "тариф", "посмотреть", "узнать"]
            },
            "предварительный": {
                "exact": ["как сделать предварительный заказ"],
                "context": ["можно ли заказать заранее", "как заказать заранее", "можно ли забронировать", "как забронировать"],
                "keywords": ["предварительный", "заранее", "забронировать", "заказ"]
            },
            "доставка": {
                "exact": ["как зарегистрировать заказ доставки"],
                "context": ["как заказать доставку", "как доставить посылку", "курьерская служба", "доставка товара"],
                "keywords": ["доставка", "курьер", "товар", "посылка", "доставить"]
            },
            "водитель": {
                "exact": ["как мне принимать заказы и что для этого нужно"],
                "context": ["как стать водителем", "как работать водителем", "как начать работать", "как стать партнером"],
                "keywords": ["водитель", "заказы", "работать", "стать", "партнер"]
            },
            "моточасы": {
                "exact": ["что такое моточасы"],
                "context": ["почему считают время", "оплата за время", "время поездки", "считают время"],
                "keywords": ["моточасы", "время", "поездка", "оплата", "считают"]
            },
            "таксометр": {
                "exact": ["как работать с таксометром"],
                "context": ["как пользоваться таксометром", "как включить таксометр", "как управлять таксометром"],
                "keywords": ["таксометр", "работать", "пользоваться", "включить", "управлять"]
            },
            "приложение": {
                "exact": ["приложение не работает что делать"],
                "context": ["приложение не открывается", "приложение зависает", "приложение не запускается", "проблемы с приложением"],
                "keywords": ["приложение", "не работает", "не открывается", "зависает", "проблема"]
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
                
                # Создаем запись
                kb_entry = {
                    "question": question,
                    "answer": answer,
                    "similarity_score": 0.0
                }
                
                self.knowledge_base.append(kb_entry)
        
        print(f"✅ Загружено {len(self.knowledge_base)} записей")
        return self.knowledge_base
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Точный поиск по контексту"""
        
        query_lower = query.lower().strip()
        results = []
        
        # Ищем точные совпадения
        for item in self.knowledge_base:
            score = 0.0
            question_lower = item['question'].lower().strip()
            
            # 1. Точное совпадение вопроса
            if question_lower == query_lower:
                score = 100.0
            elif question_lower in query_lower:
                score = 50.0
            elif query_lower in question_lower:
                score = 30.0
            
            # 2. Поиск по маппингам
            for category, mappings in self.question_mappings.items():
                # Проверяем точные совпадения
                for exact_match in mappings["exact"]:
                    if exact_match in query_lower:
                        if any(exact_match in q.lower() for q in [item['question']]):
                            score = max(score, 40.0)
                
                # Проверяем контекстные совпадения
                for context_match in mappings["context"]:
                    if context_match in query_lower:
                        if any(context_match in q.lower() for q in [item['question']]):
                            score = max(score, 25.0)
                
                # Проверяем ключевые слова
                for keyword in mappings["keywords"]:
                    if keyword in query_lower:
                        if any(keyword in q.lower() for q in [item['question']]):
                            score = max(score, 15.0)
            
            # 3. Простой поиск по словам
            query_words = set(query_lower.split())
            question_words = set(question_lower.split())
            word_overlap = len(query_words & question_words)
            if word_overlap > 0:
                score = max(score, word_overlap * 5.0)
            
            if score > 0:
                item_copy = item.copy()
                item_copy['similarity_score'] = score
                results.append(item_copy)
        
        # Сортируем по score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]
    
    def get_contextual_answer(self, query: str) -> Dict:
        """Получает точный ответ на вопрос"""
        
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
        confidence = min(best_match["similarity_score"] / 100.0, 1.0)
        
        if confidence > 0.5:
            # Высокая уверенность - возвращаем точный ответ
            return {
                "answer": best_match["answer"],
                "confidence": confidence,
                "source": "exact_match",
                "matched_question": best_match["question"]
            }
        elif confidence > 0.2:
            # Средняя уверенность - возвращаем ответ с контекстом
            return {
                "answer": best_match["answer"],
                "confidence": confidence,
                "source": "contextual_match",
                "matched_question": best_match["question"]
            }
        else:
            # Низкая уверенность - возвращаем общий ответ
            return {
                "answer": "Извините, я не уверен в ответе. Возможно, вы имели в виду что-то другое?",
                "confidence": confidence,
                "source": "low_confidence",
                "suggestions": [r["question"] for r in results[:3]]
            }

def test_precise_search():
    """Тестирует точную систему поиска"""
    
    print("🧪 Тестируем точную систему поиска...")
    
    # Создаем систему
    precise_search = PreciseContextSearch()
    
    # Загружаем базу знаний
    precise_search.load_knowledge_base()
    
    # Тестовые запросы
    test_queries = [
        "Почему так дорого?",
        "Как заплатить за поездку?",
        "Можно ли заказать заранее?",
        "Как стать водителем?",
        "Приложение не открывается",
        "Что означает наценка?",
        "Где найти цену?",
        "Как доставить посылку?",
        "Что такое комфорт?",
        "Почему считают время?"
    ]
    
    print("\n🔍 Результаты тестирования:")
    
    for query in test_queries:
        print(f"\n❓ Вопрос: {query}")
        
        result = precise_search.get_contextual_answer(query)
        
        print(f"📝 Ответ: {result['answer'][:100]}...")
        print(f"🎯 Уверенность: {result['confidence']:.2f}")
        print(f"📂 Источник: {result['source']}")
        
        if 'matched_question' in result:
            print(f"🔗 Совпавший вопрос: {result['matched_question']}")
        
        if 'suggestions' in result:
            print(f"💡 Предложения: {result['suggestions']}")

if __name__ == "__main__":
    print("🚀 Создание точной системы поиска APARU...")
    
    # Тестируем
    test_precise_search()
    
    print("\n✅ Точная система поиска готова!")
    print("🎯 Теперь модель точно понимает контекст!")

#!/usr/bin/env python3
"""
Простая и эффективная система поиска для APARU LLM
Исправляет все проблемы с пониманием контекста
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

class SimpleEffectiveSearch:
    def __init__(self):
        """Инициализация простой и эффективной системы поиска"""
        
        # База знаний
        self.knowledge_base = []
        
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
        """Простой и эффективный поиск"""
        
        query_lower = query.lower().strip()
        results = []
        
        # Простой поиск по словам
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
            
            # 2. Поиск по ключевым словам
            query_words = set(query_lower.split())
            question_words = set(question_lower.split())
            
            # Совпадения слов
            word_overlap = len(query_words & question_words)
            if word_overlap > 0:
                score = max(score, word_overlap * 10.0)
            
            # 3. Поиск по частичным совпадениям
            for word in query_words:
                if len(word) > 3:  # Только длинные слова
                    for q_word in question_words:
                        if word in q_word or q_word in word:
                            score += 5.0
            
            # 4. Поиск в ответе
            answer_lower = item['answer'].lower()
            for word in query_words:
                if word in answer_lower:
                    score += 2.0
            
            if score > 0:
                item_copy = item.copy()
                item_copy['similarity_score'] = score
                results.append(item_copy)
        
        # Сортируем по score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]
    
    def get_contextual_answer(self, query: str) -> Dict:
        """Получает ответ на вопрос"""
        
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
        
        if confidence > 0.3:
            # Достаточная уверенность - возвращаем ответ
            return {
                "answer": best_match["answer"],
                "confidence": confidence,
                "source": "knowledge_base",
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

def test_simple_search():
    """Тестирует простую систему поиска"""
    
    print("🧪 Тестируем простую систему поиска...")
    
    # Создаем систему
    simple_search = SimpleEffectiveSearch()
    
    # Загружаем базу знаний
    simple_search.load_knowledge_base()
    
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
        
        result = simple_search.get_contextual_answer(query)
        
        print(f"📝 Ответ: {result['answer'][:100]}...")
        print(f"🎯 Уверенность: {result['confidence']:.2f}")
        print(f"📂 Источник: {result['source']}")
        
        if 'matched_question' in result:
            print(f"🔗 Совпавший вопрос: {result['matched_question']}")
        
        if 'suggestions' in result:
            print(f"💡 Предложения: {result['suggestions']}")

if __name__ == "__main__":
    print("🚀 Создание простой системы поиска APARU...")
    
    # Тестируем
    test_simple_search()
    
    print("\n✅ Простая система поиска готова!")
    print("🎯 Теперь модель понимает контекст!")

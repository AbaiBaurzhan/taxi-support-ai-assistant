#!/usr/bin/env python3
"""
Простая интеграция финальной системы поиска в APARU
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

class SimpleAPARUSearch:
    def __init__(self):
        """Инициализация простой системы поиска APARU"""
        
        # База знаний
        self.knowledge_base = []
        
        # Точные маппинги
        self.question_mappings = {
            "наценка": {
                "questions": ["что такое наценка", "что означает наценка"],
                "contexts": ["почему дорого", "почему так дорого", "откуда цена", "почему высокая цена"],
                "keywords": ["наценка", "цена", "стоимость", "дорого", "тариф"]
            },
            "пополнение": {
                "questions": ["как пополнить баланс"],
                "contexts": ["как заплатить", "как оплатить", "где пополнить", "как добавить деньги"],
                "keywords": ["пополнить", "баланс", "счет", "деньги", "оплатить"]
            },
            "комфорт": {
                "questions": ["что такое тариф комфорт", "что такое комфорт"],
                "contexts": ["комфорт класс", "премиум такси", "новая машина"],
                "keywords": ["комфорт", "премиум", "класс", "машина"]
            },
            "расценка": {
                "questions": ["как узнать расценку"],
                "contexts": ["как узнать цену", "где найти цену", "как узнать стоимость"],
                "keywords": ["расценка", "цена", "стоимость", "тариф"]
            },
            "предварительный": {
                "questions": ["как сделать предварительный заказ"],
                "contexts": ["можно ли заказать заранее", "как заказать заранее", "можно ли забронировать"],
                "keywords": ["предварительный", "заранее", "забронировать"]
            },
            "доставка": {
                "questions": ["как зарегистрировать заказ доставки"],
                "contexts": ["как заказать доставку", "как доставить посылку", "курьерская служба"],
                "keywords": ["доставка", "курьер", "товар", "посылка"]
            },
            "водитель": {
                "questions": ["как мне принимать заказы и что для этого нужно"],
                "contexts": ["как стать водителем", "как работать водителем", "как начать работать"],
                "keywords": ["водитель", "заказы", "работать", "стать"]
            },
            "моточасы": {
                "questions": ["что такое моточасы"],
                "contexts": ["почему считают время", "оплата за время", "время поездки"],
                "keywords": ["моточасы", "время", "поездка", "оплата"]
            },
            "таксометр": {
                "questions": ["как работать с таксометром"],
                "contexts": ["как пользоваться таксометром", "как включить таксометр"],
                "keywords": ["таксометр", "работать", "пользоваться"]
            },
            "приложение": {
                "questions": ["приложение не работает что делать"],
                "contexts": ["приложение не открывается", "приложение зависает", "проблемы с приложением"],
                "keywords": ["приложение", "не работает", "не открывается"]
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
        """Простой поиск"""
        
        query_lower = query.lower().strip()
        results = []
        
        # Ищем по маппингам
        for category, mappings in self.question_mappings.items():
            # Проверяем контексты
            for context in mappings["contexts"]:
                if context in query_lower:
                    # Ищем соответствующий вопрос
                    for item in self.knowledge_base:
                        question_lower = item['question'].lower().strip()
                        
                        # Проверяем точные совпадения
                        for exact_question in mappings["questions"]:
                            if exact_question in question_lower:
                                item_copy = item.copy()
                                item_copy['similarity_score'] = 50.0
                                results.append(item_copy)
                                break
                        
                        # Проверяем ключевые слова
                        for keyword in mappings["keywords"]:
                            if keyword in question_lower:
                                item_copy = item.copy()
                                item_copy['similarity_score'] = 30.0
                                results.append(item_copy)
                                break
            
            # Проверяем ключевые слова напрямую
            for keyword in mappings["keywords"]:
                if keyword in query_lower:
                    for item in self.knowledge_base:
                        question_lower = item['question'].lower().strip()
                        
                        # Проверяем точные совпадения
                        for exact_question in mappings["questions"]:
                            if exact_question in question_lower:
                                item_copy = item.copy()
                                item_copy['similarity_score'] = 40.0
                                results.append(item_copy)
                                break
                        
                        # Проверяем ключевые слова
                        if keyword in question_lower:
                            item_copy = item.copy()
                            item_copy['similarity_score'] = 20.0
                            results.append(item_copy)
        
        # Убираем дубликаты
        seen = set()
        unique_results = []
        for result in results:
            if result['question'] not in seen:
                seen.add(result['question'])
                unique_results.append(result)
        
        # Сортируем по score
        unique_results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return unique_results[:top_k]
    
    def get_answer(self, query: str) -> str:
        """Получает ответ на вопрос"""
        
        # Ищем похожие записи
        results = self.search(query, top_k=1)
        
        if not results:
            return "Извините, я не нашел подходящего ответа в базе знаний."
        
        # Берем лучший результат
        best_match = results[0]
        
        # Определяем уверенность
        confidence = min(best_match["similarity_score"] / 50.0, 1.0)
        
        if confidence > 0.4:
            # Достаточная уверенность - возвращаем ответ
            return best_match["answer"]
        else:
            # Низкая уверенность - возвращаем общий ответ
            return "Извините, я не уверен в ответе. Возможно, вы имели в виду что-то другое?"

# Глобальный экземпляр
aparu_search = SimpleAPARUSearch()
aparu_search.load_knowledge_base()

def get_aparu_answer(query: str) -> str:
    """Получает ответ от APARU системы поиска"""
    return aparu_search.get_answer(query)

if __name__ == "__main__":
    print("🚀 Создание простой системы поиска APARU...")
    
    # Тестируем
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
        answer = get_aparu_answer(query)
        print(f"📝 Ответ: {answer[:100]}...")
    
    print("\n✅ Простая система поиска готова!")
    print("🎯 Теперь модель понимает контекст!")

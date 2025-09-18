#!/usr/bin/env python3
"""
Улучшенная система поиска для APARU LLM
Исправляет проблемы с пониманием контекста
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

class ImprovedContextSearch:
    def __init__(self):
        """Инициализация улучшенной системы поиска"""
        
        # База знаний
        self.knowledge_base = []
        
        # Словарь синонимов и контекстных связей
        self.context_mappings = self._create_context_mappings()
        
        # Словарь ключевых слов для каждого вопроса
        self.question_keywords = {}
        
    def _create_context_mappings(self):
        """Создает словарь контекстных связей"""
        
        return {
            # Группы связанных понятий
            "pricing": {
                "keywords": ["цена", "стоимость", "расценка", "тариф", "наценка", "дорого", "дешево", "оплата", "платеж", "стоит", "сколько"],
                "contexts": ["сколько стоит", "почему дорого", "откуда цена", "что такое наценка", "как считается цена", "почему так дорого"]
            },
            "payment": {
                "keywords": ["пополнить", "баланс", "счет", "деньги", "оплатить", "платеж", "кошелек", "карта", "заплатить", "внести"],
                "contexts": ["как заплатить", "где пополнить", "как добавить деньги", "как внести средства", "как пополнить баланс"]
            },
            "booking": {
                "keywords": ["заказать", "вызвать", "забронировать", "предварительный", "заранее", "время", "заказ"],
                "contexts": ["как заказать такси", "можно ли заранее", "как забронировать", "когда заказывать", "предварительный заказ"]
            },
            "driver": {
                "keywords": ["водитель", "работать", "заказы", "партнер", "регистрация", "таксометр", "работа"],
                "contexts": ["как стать водителем", "как работать", "как принимать заказы", "как пользоваться таксометром"]
            },
            "delivery": {
                "keywords": ["доставка", "курьер", "товар", "вещи", "документы", "посылка", "доставить"],
                "contexts": ["как заказать доставку", "как доставить", "курьерская служба", "доставка товара"]
            },
            "technical": {
                "keywords": ["приложение", "не работает", "проблема", "ошибка", "зависает", "не запускается", "не открывается"],
                "contexts": ["приложение не работает", "что делать", "как исправить", "проблемы с приложением"]
            },
            "comfort": {
                "keywords": ["комфорт", "премиум", "класс", "машина", "тариф", "лучше", "новая"],
                "contexts": ["что такое комфорт", "комфорт класс", "премиум такси", "новая машина"]
            },
            "motohours": {
                "keywords": ["моточасы", "время", "поездка", "оплата", "тариф", "считают", "минуты"],
                "contexts": ["что такое моточасы", "оплата за время", "считают время", "время поездки"]
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
                    "similarity_score": 0.0
                }
                
                self.knowledge_base.append(kb_entry)
                
                # Сохраняем ключевые слова для быстрого поиска
                self.question_keywords[question.lower()] = kb_entry["keywords"]
        
        print(f"✅ Загружено {len(self.knowledge_base)} записей")
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
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Умный поиск по контексту"""
        
        query_lower = query.lower()
        results = []
        
        for item in self.knowledge_base:
            score = 0.0
            
            # 1. Точное совпадение вопроса
            if item['question'].lower() in query_lower:
                score += 10.0
            
            # 2. Совпадение ключевых слов
            for keyword in item['keywords']:
                if keyword.lower() in query_lower:
                    score += 2.0
            
            # 3. Совпадение контекстных слов
            for context in item['contexts']:
                if context.lower() in query_lower:
                    score += 1.5
            
            # 4. Совпадение по категории
            category_keywords = self.context_mappings.get(item['category'], {}).get('keywords', [])
            for keyword in category_keywords:
                if keyword.lower() in query_lower:
                    score += 1.0
            
            # 5. Совпадение в ответе
            answer_words = set(item['answer'].lower().split())
            query_words = set(query_lower.split())
            answer_overlap = len(answer_words & query_words)
            if answer_overlap > 0:
                score += answer_overlap * 0.5
            
            if score > 0:
                item_copy = item.copy()
                item_copy['similarity_score'] = score
                results.append(item_copy)
        
        # Сортируем по score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]
    
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
        confidence = min(best_match["similarity_score"] / 10.0, 1.0)
        
        if confidence > 0.7:
            # Высокая уверенность - возвращаем точный ответ
            return {
                "answer": best_match["answer"],
                "confidence": confidence,
                "source": "exact_match",
                "matched_question": best_match["question"],
                "category": best_match["category"]
            }
        elif confidence > 0.3:
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

def test_improved_search():
    """Тестирует улучшенную систему поиска"""
    
    print("🧪 Тестируем улучшенную систему поиска...")
    
    # Создаем систему
    improved_search = ImprovedContextSearch()
    
    # Загружаем базу знаний
    improved_search.load_knowledge_base()
    
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
        
        result = improved_search.get_contextual_answer(query)
        
        print(f"📝 Ответ: {result['answer'][:100]}...")
        print(f"🎯 Уверенность: {result['confidence']:.2f}")
        print(f"📂 Источник: {result['source']}")
        
        if 'matched_question' in result:
            print(f"🔗 Совпавший вопрос: {result['matched_question']}")
        
        if 'suggestions' in result:
            print(f"💡 Предложения: {result['suggestions']}")

if __name__ == "__main__":
    print("🚀 Создание улучшенной системы поиска APARU...")
    
    # Тестируем
    test_improved_search()
    
    print("\n✅ Улучшенная система поиска готова!")
    print("🧠 Теперь модель лучше понимает контекст!")

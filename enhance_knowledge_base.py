#!/usr/bin/env python3
"""
Скрипт для расширения базы знаний APARU
Добавляет вариации вопросов для большей гибкости модели
"""

import json
import re
from pathlib import Path

def create_enhanced_knowledge_base():
    """Создает расширенную базу знаний с вариациями вопросов"""
    
    # Читаем оригинальную базу
    with open('database_Aparu/BZ.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Парсим вопросы и ответы
    questions_answers = []
    sections = content.split('- question:')
    
    for section in sections[1:]:  # Пропускаем первый пустой элемент
        lines = section.strip().split('\n')
        if len(lines) >= 2:
            question = lines[0].strip()
            answer = '\n'.join(lines[1:]).strip()
            questions_answers.append((question, answer))
    
    # Создаем расширенную базу с вариациями
    enhanced_kb = []
    
    for question, answer in questions_answers:
        # Создаем вариации для каждого вопроса
        variations = create_question_variations(question)
        
        # Извлекаем ключевые слова
        keywords = extract_keywords(question)
        
        # Создаем запись
        kb_entry = {
            "original_question": question,
            "variations": variations,
            "keywords": keywords,
            "answer": answer,
            "category": categorize_question(question)
        }
        
        enhanced_kb.append(kb_entry)
    
    # Сохраняем расширенную базу
    with open('enhanced_aparu_knowledge_base.json', 'w', encoding='utf-8') as f:
        json.dump(enhanced_kb, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Создана расширенная база знаний: {len(enhanced_kb)} записей")
    return enhanced_kb

def create_question_variations(question):
    """Создает вариации вопроса"""
    
    # Базовые вариации
    variations = [question]
    
    # Словарь синонимов и альтернативных формулировок
    synonyms = {
        "что такое": ["что означает", "что это", "что значит", "что за"],
        "как": ["каким образом", "как именно", "как можно", "как нужно"],
        "где": ["в каком месте", "где найти", "где посмотреть", "где искать"],
        "почему": ["зачем", "откуда", "из-за чего", "по какой причине"],
        "можно ли": ["возможно ли", "реально ли", "получится ли", "удастся ли"],
        "как узнать": ["как посмотреть", "как найти", "как проверить", "как увидеть"],
        "как сделать": ["как выполнить", "как осуществить", "как провести", "как реализовать"],
        "как заказать": ["как забронировать", "как вызвать", "как попросить", "как запросить"],
        "как пополнить": ["как добавить", "как внести", "как заплатить", "как оплатить"],
        "как работать": ["как пользоваться", "как использовать", "как применять", "как управлять"]
    }
    
    # Создаем вариации на основе синонимов
    for original, alternatives in synonyms.items():
        if original in question.lower():
            for alt in alternatives:
                new_question = question.lower().replace(original, alt)
                if new_question not in variations:
                    variations.append(new_question.capitalize())
    
    # Добавляем вариации с разными формулировками
    if "что такое" in question.lower():
        # Для вопросов "что такое X"
        subject = question.lower().replace("что такое", "").strip().strip('"').strip("'")
        if subject:
            variations.extend([
                f"Что означает {subject}?",
                f"Что это {subject}?",
                f"Что значит {subject}?",
                f"Что за {subject}?",
                f"Почему {subject}?",
                f"Зачем {subject}?"
            ])
    
    elif "как" in question.lower():
        # Для вопросов "как X"
        action = question.lower().replace("как", "").strip()
        if action:
            variations.extend([
                f"Каким образом {action}?",
                f"Как именно {action}?",
                f"Как можно {action}?",
                f"Как нужно {action}?",
                f"Где {action}?",
                f"Когда {action}?"
            ])
    
    # Убираем дубликаты и возвращаем
    return list(set(variations))

def extract_keywords(question):
    """Извлекает ключевые слова из вопроса"""
    
    # Убираем стоп-слова
    stop_words = {
        "что", "как", "где", "когда", "почему", "зачем", "можно", "ли", "это", "такое",
        "означает", "значит", "есть", "быть", "делать", "сделать", "узнать", "посмотреть",
        "найти", "найти", "получить", "взять", "дать", "сказать", "объяснить"
    }
    
    # Разбиваем на слова и убираем знаки препинания
    words = re.findall(r'\b\w+\b', question.lower())
    
    # Фильтруем стоп-слова и короткие слова
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    return keywords

def categorize_question(question):
    """Категоризирует вопрос"""
    
    question_lower = question.lower()
    
    if any(word in question_lower for word in ["наценка", "цена", "стоимость", "дорого"]):
        return "pricing"
    elif any(word in question_lower for word in ["пополнить", "баланс", "счет", "оплатить"]):
        return "payment"
    elif any(word in question_lower for word in ["комфорт", "тариф", "класс"]):
        return "tariff"
    elif any(word in question_lower for word in ["расценка", "тариф", "цена"]):
        return "pricing"
    elif any(word in question_lower for word in ["предварительный", "заранее", "забронировать"]):
        return "booking"
    elif any(word in question_lower for word in ["доставка", "курьер", "товар"]):
        return "delivery"
    elif any(word in question_lower for word in ["водитель", "заказы", "работать"]):
        return "driver"
    elif any(word in question_lower for word in ["моточасы", "время", "поездка"]):
        return "pricing"
    elif any(word in question_lower for word in ["таксометр", "работать", "пользоваться"]):
        return "driver"
    elif any(word in question_lower for word in ["приложение", "не работает", "проблема"]):
        return "technical"
    else:
        return "general"

def test_enhanced_knowledge_base():
    """Тестирует расширенную базу знаний"""
    
    # Загружаем базу
    with open('enhanced_aparu_knowledge_base.json', 'r', encoding='utf-8') as f:
        kb = json.load(f)
    
    print(f"\n🧪 Тестирование расширенной базы знаний:")
    print(f"Всего записей: {len(kb)}")
    
    # Показываем примеры
    for i, entry in enumerate(kb[:3]):  # Показываем первые 3
        print(f"\n📝 Запись {i+1}:")
        print(f"Оригинальный вопрос: {entry['original_question']}")
        print(f"Вариации ({len(entry['variations'])}): {entry['variations'][:3]}...")
        print(f"Ключевые слова: {entry['keywords']}")
        print(f"Категория: {entry['category']}")
    
    return kb

if __name__ == "__main__":
    print("🚀 Создание расширенной базы знаний APARU...")
    
    # Создаем расширенную базу
    enhanced_kb = create_enhanced_knowledge_base()
    
    # Тестируем
    test_enhanced_knowledge_base()
    
    print("\n✅ Расширенная база знаний готова!")
    print("📁 Файл: enhanced_aparu_knowledge_base.json")
    print("🔄 Теперь можно переобучить модель с новыми данными!")

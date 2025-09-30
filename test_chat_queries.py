"""
Тест реальных запросов из чата
"""

import sys
import os
sys.path.append('backend')

from enhanced_morphological_analyzer import enhance_classification_with_morphology
import json

def load_kb_data():
    """Загружает данные базы знаний"""
    try:
        with open('backend/kb.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки kb.json: {e}")
        return None

def test_real_chat_queries():
    """Тестирует реальные запросы из чата"""
    print("🧪 Тестирование реальных запросов из чата")
    print("=" * 60)
    
    kb_data = load_kb_data()
    if not kb_data:
        return
    
    # Реальные запросы из чата
    chat_queries = [
        "че там по доставке ?",  # Первый запрос - НЕ НАШЕЛ
        "доставка как работает",  # Второй запрос - НАШЕЛ
    ]
    
    print("Тестируем реальные запросы из чата:")
    print()
    
    for i, query in enumerate(chat_queries, 1):
        print(f"{i}. Запрос: '{query}'")
        
        # Тестируем морфологический анализ
        result = enhance_classification_with_morphology(query, kb_data)
        
        confidence = result.get('confidence', 0)
        matched_item = result.get('matched_item')
        
        print(f"   Confidence: {confidence:.3f}")
        print(f"   Порог: 0.1")
        print(f"   Проходит порог: {'✅ ДА' if confidence > 0.1 else '❌ НЕТ'}")
        
        if matched_item:
            print(f"   ✅ НАЙДЕНО!")
            print(f"   📋 Question: {matched_item.get('question', '')[:80]}...")
            answer = matched_item.get('answer', '')
            if 'доставк' in answer.lower():
                print(f"   🎯 Правильно распознано как доставка!")
            else:
                print(f"   ⚠️ Распознано, но не про доставку")
        else:
            print(f"   ❌ НЕ НАЙДЕНО")
        
        print()

if __name__ == "__main__":
    test_real_chat_queries()

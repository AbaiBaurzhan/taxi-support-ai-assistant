"""
Тест исправления проблемы с доставкой
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

def test_delivery_queries():
    """Тестирует запросы про доставку"""
    print("🧪 Тестирование исправлений для запросов про доставку")
    print("=" * 60)
    
    kb_data = load_kb_data()
    if not kb_data:
        return
    
    # Тестовые запросы про доставку
    delivery_queries = [
        "доставка",
        "как сделать доставку", 
        "доставка как сделать",
        "как зарегистрировать заказ доставки",
        "как оформить заказ на доставку",
        "где выбрать тип заказа доставка",
        "как вызвать курьера",
        "курьер",
        "посылка",
        "перевозка"
    ]
    
    print(f"Тестируем {len(delivery_queries)} запросов про доставку:")
    print()
    
    success_count = 0
    for i, query in enumerate(delivery_queries, 1):
        print(f"{i:2d}. Запрос: '{query}'")
        
        # Тестируем морфологический анализ
        result = enhance_classification_with_morphology(query, kb_data)
        
        if result.get('matched_item'):
            confidence = result.get('confidence', 0)
            matched_item = result['matched_item']
            
            print(f"    ✅ НАЙДЕНО! Confidence: {confidence:.3f}")
            print(f"    📋 Question: {matched_item.get('question', '')[:60]}...")
            
            # Проверяем, что это действительно про доставку
            answer = matched_item.get('answer', '')
            if 'доставк' in answer.lower():
                print(f"    🎯 Правильно распознано как доставка!")
                success_count += 1
            else:
                print(f"    ⚠️ Распознано, но не про доставку")
        else:
            print(f"    ❌ НЕ НАЙДЕНО")
        
        print()
    
    success_rate = (success_count / len(delivery_queries)) * 100
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"Успешно распознано: {success_count}/{len(delivery_queries)} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 Отлично! Проблема исправлена!")
    elif success_rate >= 70:
        print("✅ Хорошо! Есть улучшения!")
    else:
        print("❌ Нужны дополнительные исправления")

if __name__ == "__main__":
    test_delivery_queries()

#!/usr/bin/env python3
"""
Тест для проверки каждого ключевого слова и каждой вариации вопросов из базы знаний
"""

import requests
import json
import time
from typing import Dict, List, Any

def load_kb() -> List[Dict]:
    """Загружает базу знаний"""
    try:
        with open('backend/kb.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'faq' in data:
                return data['faq']
            else:
                return []
    except Exception as e:
        print(f"❌ Ошибка загрузки kb.json: {e}")
        return []

def test_api(query: str) -> Dict[str, Any]:
    """Тестирует API с одним запросом"""
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={
                "text": query,
                "user_id": "test_individual",
                "locale": "ru"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"HTTP {response.status_code}: {response.text}",
                "success": False
            }
    except Exception as e:
        return {
            "error": f"Exception: {str(e)}",
            "success": False
        }

def check_answer_match(expected_answer: str, actual_answer: str) -> bool:
    """Проверяет соответствие ответов"""
    if not expected_answer or not actual_answer:
        return False
    
    # Нормализуем строки для сравнения
    expected = expected_answer.lower().strip()
    actual = actual_answer.lower().strip()
    
    # Проверяем точное совпадение или совпадение первых 100 символов
    if expected == actual:
        return True
    
    # Проверяем совпадение начала ответа (первые 100 символов)
    if len(expected) > 100 and len(actual) > 100:
        return expected[:100] == actual[:100]
    
    return False

def test_keywords(faq_item: Dict, results: List[Dict]):
    """Тестирует все ключевые слова для одного FAQ"""
    question = faq_item.get('question', 'Неизвестно')
    expected_answer = faq_item.get('answer', '')
    keywords = faq_item.get('keywords', [])
    
    print(f"\n🔑 ТЕСТИРОВАНИЕ КЛЮЧЕВЫХ СЛОВ ДЛЯ: '{question}'")
    print(f"📝 Ожидаемый ответ: {expected_answer[:100]}...")
    print(f"🔍 Ключевых слов: {len(keywords)}")
    
    for keyword in keywords:
        print(f"   🧪 Тестирую ключевое слово: '{keyword}'")
        
        result = test_api(keyword)
        
        if 'error' in result:
            print(f"      ❌ Ошибка: {result['error']}")
            results.append({
                "type": "keyword",
                "faq_question": question,
                "keyword": keyword,
                "success": False,
                "error": result['error']
            })
        else:
            actual_answer = result.get('response', '')
            confidence = result.get('confidence', 0)
            source = result.get('source', 'unknown')
            
            # Проверяем соответствие ответа
            answer_matches = check_answer_match(expected_answer, actual_answer)
            
            if answer_matches:
                print(f"      ✅ Ответ соответствует ожидаемому")
                print(f"      📊 Уверенность: {confidence}")
                print(f"      🔍 Источник: {source}")
            else:
                print(f"      ⚠️ Ответ НЕ соответствует ожидаемому")
                print(f"      📝 Ожидалось: {expected_answer[:100]}...")
                print(f"      💬 Получено: {actual_answer[:100]}...")
                print(f"      📊 Уверенность: {confidence}")
                print(f"      🔍 Источник: {source}")
            
            results.append({
                "type": "keyword",
                "faq_question": question,
                "keyword": keyword,
                "success": answer_matches,
                "expected_answer": expected_answer,
                "actual_answer": actual_answer,
                "confidence": confidence,
                "source": source,
                "answer_matches": answer_matches
            })

def test_variations(faq_item: Dict, results: List[Dict]):
    """Тестирует все вариации вопросов для одного FAQ"""
    question = faq_item.get('question', 'Неизвестно')
    expected_answer = faq_item.get('answer', '')
    variations = faq_item.get('question_variations', [])
    
    print(f"\n📝 ТЕСТИРОВАНИЕ ВАРИАЦИЙ ВОПРОСОВ ДЛЯ: '{question}'")
    print(f"📝 Ожидаемый ответ: {expected_answer[:100]}...")
    print(f"🔍 Вариаций вопросов: {len(variations)}")
    
    for variation in variations:
        print(f"   🧪 Тестирую вариацию: '{variation}'")
        
        result = test_api(variation)
        
        if 'error' in result:
            print(f"      ❌ Ошибка: {result['error']}")
            results.append({
                "type": "variation",
                "faq_question": question,
                "variation": variation,
                "success": False,
                "error": result['error']
            })
        else:
            actual_answer = result.get('response', '')
            confidence = result.get('confidence', 0)
            source = result.get('source', 'unknown')
            
            # Проверяем соответствие ответа
            answer_matches = check_answer_match(expected_answer, actual_answer)
            
            if answer_matches:
                print(f"      ✅ Ответ соответствует ожидаемому")
                print(f"      📊 Уверенность: {confidence}")
                print(f"      🔍 Источник: {source}")
            else:
                print(f"      ⚠️ Ответ НЕ соответствует ожидаемому")
                print(f"      📝 Ожидалось: {expected_answer[:100]}...")
                print(f"      💬 Получено: {actual_answer[:100]}...")
                print(f"      📊 Уверенность: {confidence}")
                print(f"      🔍 Источник: {source}")
            
            results.append({
                "type": "variation",
                "faq_question": question,
                "variation": variation,
                "success": answer_matches,
                "expected_answer": expected_answer,
                "actual_answer": actual_answer,
                "confidence": confidence,
                "source": source,
                "answer_matches": answer_matches
            })

def wait_for_server():
    """Ждет запуска сервера"""
    print("🔄 Ожидание запуска сервера...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Сервер запущен и готов к тестированию")
                return True
        except:
            pass
        time.sleep(1)
    
    print("❌ Сервер не запустился за 30 секунд")
    return False

def generate_report(results: List[Dict]):
    """Генерирует детальный отчет"""
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.get('success', False))
    failed_tests = total_tests - successful_tests
    
    # Статистика по типам
    keyword_tests = [r for r in results if r['type'] == 'keyword']
    variation_tests = [r for r in results if r['type'] == 'variation']
    
    keyword_success = sum(1 for r in keyword_tests if r.get('success', False))
    variation_success = sum(1 for r in variation_tests if r.get('success', False))
    
    print(f"\n{'='*80}")
    print(f"📊 ДЕТАЛЬНЫЙ ОТЧЕТ О ТЕСТИРОВАНИИ КАЖДОГО ЭЛЕМЕНТА БАЗЫ ЗНАНИЙ")
    print(f"{'='*80}")
    
    print(f"\n📈 Общая статистика:")
    print(f"   Всего тестов: {total_tests}")
    print(f"   ✅ Успешных: {successful_tests}")
    print(f"   ❌ Неудачных: {failed_tests}")
    print(f"   📊 Процент успеха: {(successful_tests/total_tests*100):.1f}%")
    
    print(f"\n🎯 Анализ по типам тестов:")
    print(f"   Ключевые слова: {len(keyword_tests)} (успешно: {keyword_success}, {keyword_success/len(keyword_tests)*100:.1f}%)")
    print(f"   Вариации вопросов: {len(variation_tests)} (успешно: {variation_success}, {variation_success/len(variation_tests)*100:.1f}%)")
    
    # Статистика по FAQ
    faq_stats = {}
    for result in results:
        faq = result['faq_question']
        if faq not in faq_stats:
            faq_stats[faq] = {'total': 0, 'success': 0}
        faq_stats[faq]['total'] += 1
        if result.get('success', False):
            faq_stats[faq]['success'] += 1
    
    print(f"\n📋 Анализ по FAQ:")
    for faq, stats in faq_stats.items():
        success_rate = stats['success'] / stats['total'] * 100
        print(f"   '{faq}': {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    # Список неудачных тестов
    failed_tests_list = [r for r in results if not r.get('success', False)]
    if failed_tests_list:
        print(f"\n❌ НЕУДАЧНЫЕ ТЕСТЫ ({len(failed_tests_list)}):")
        for test in failed_tests_list[:10]:  # Показываем первые 10
            if test['type'] == 'keyword':
                print(f"   🔑 '{test['keyword']}' для '{test['faq_question']}'")
            else:
                print(f"   📝 '{test['variation']}' для '{test['faq_question']}'")
        
        if len(failed_tests_list) > 10:
            print(f"   ... и еще {len(failed_tests_list) - 10} неудачных тестов")
    
    # Сохраняем результаты в файл
    with open('individual_kb_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': successful_tests/total_tests*100,
                'keyword_tests': len(keyword_tests),
                'keyword_success': keyword_success,
                'variation_tests': len(variation_tests),
                'variation_success': variation_success
            },
            'faq_stats': faq_stats,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Подробные результаты сохранены в: individual_kb_test_results.json")
    print(f"🎉 Тестирование каждого элемента базы знаний завершено!")

def main():
    """Основная функция"""
    print("🚀 ТЕСТИРОВАНИЕ КАЖДОГО ЭЛЕМЕНТА БАЗЫ ЗНАНИЙ")
    print("="*80)
    
    # Загружаем базу знаний
    kb_data = load_kb()
    if not kb_data:
        print("❌ Не удалось загрузить базу знаний")
        return
    
    print(f"✅ Загружена база знаний: {len(kb_data)} FAQ записей")
    
    # Ждем запуска сервера
    if not wait_for_server():
        return
    
    results = []
    
    # Тестируем каждый FAQ
    for i, faq_item in enumerate(kb_data, 1):
        print(f"\n{'='*80}")
        print(f"📋 FAQ {i}/{len(kb_data)}: {faq_item.get('question', 'Неизвестно')}")
        
        # Тестируем ключевые слова
        test_keywords(faq_item, results)
        
        # Тестируем вариации вопросов
        test_variations(faq_item, results)
    
    # Генерируем отчет
    generate_report(results)

if __name__ == "__main__":
    main()

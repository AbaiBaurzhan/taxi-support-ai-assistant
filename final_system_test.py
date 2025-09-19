#!/usr/bin/env python3
"""
🧪 Финальный тест улучшенной системы APARU
Проверяет понимание контекста и предотвращение смешивания ответов
"""

import requests
import json
import time
from typing import Dict, List, Any

class APARUFinalTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def test_question(self, question: str, expected_keywords: List[str], test_name: str) -> Dict[str, Any]:
        """Тестирует один вопрос"""
        print(f"\n🧪 Тест: {test_name}")
        print(f"❓ Вопрос: {question}")
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={
                    "text": question,
                    "user_id": "test123",
                    "locale": "ru"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '')
                confidence = data.get('confidence', 0)
                source = data.get('source', 'unknown')
                
                print(f"✅ Ответ: {answer[:100]}...")
                print(f"📊 Уверенность: {confidence}")
                print(f"🔍 Источник: {source}")
                
                # Проверяем наличие ключевых слов
                answer_lower = answer.lower()
                found_keywords = [kw for kw in expected_keywords if kw.lower() in answer_lower]
                
                result = {
                    'test_name': test_name,
                    'question': question,
                    'answer': answer,
                    'confidence': confidence,
                    'source': source,
                    'expected_keywords': expected_keywords,
                    'found_keywords': found_keywords,
                    'success': len(found_keywords) > 0,
                    'timestamp': time.time()
                }
                
                if result['success']:
                    print(f"✅ Успех! Найдены ключевые слова: {found_keywords}")
                else:
                    print(f"❌ Не найдены ожидаемые ключевые слова: {expected_keywords}")
                
                return result
            else:
                print(f"❌ Ошибка HTTP: {response.status_code}")
                return {
                    'test_name': test_name,
                    'question': question,
                    'error': f"HTTP {response.status_code}",
                    'success': False
                }
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return {
                'test_name': test_name,
                'question': question,
                'error': str(e),
                'success': False
            }
    
    def run_comprehensive_tests(self):
        """Запускает комплексные тесты"""
        print("🚀 Запускаем финальные тесты улучшенной системы APARU")
        print("=" * 60)
        
        # Тесты на понимание контекста
        tests = [
            {
                'question': 'Что такое наценка?',
                'expected_keywords': ['наценка', 'тариф', 'спрос', 'погодные условия'],
                'test_name': 'Понимание наценки'
            },
            {
                'question': 'Почему так дорого?',
                'expected_keywords': ['наценка', 'спрос', 'погодные условия', 'дополнительные водители'],
                'test_name': 'Контекстное понимание цены'
            },
            {
                'question': 'Как пополнить баланс?',
                'expected_keywords': ['баланс', 'пополнить', 'qiwi', 'kaspi', 'карта'],
                'test_name': 'Пополнение баланса'
            },
            {
                'question': 'Где можно положить деньги на счет?',
                'expected_keywords': ['баланс', 'пополнить', 'qiwi', 'kaspi', 'карта'],
                'test_name': 'Контекстное понимание пополнения'
            },
            {
                'question': 'Что такое тариф Комфорт?',
                'expected_keywords': ['комфорт', 'новая машина', 'toyota camry', '20% выше'],
                'test_name': 'Понимание тарифов'
            },
            {
                'question': 'Какой самый дорогой класс?',
                'expected_keywords': ['комфорт', 'новая машина', 'toyota camry', '20% выше'],
                'test_name': 'Контекстное понимание тарифов'
            },
            {
                'question': 'Как отменить заказ?',
                'expected_keywords': ['отменить', 'заказ', 'поездка'],
                'test_name': 'Отмена заказа'
            },
            {
                'question': 'Можно ли отказаться от поездки?',
                'expected_keywords': ['отменить', 'заказ', 'поездка'],
                'test_name': 'Контекстное понимание отмены'
            },
            {
                'question': 'Приложение не работает',
                'expected_keywords': ['приложение', 'обновить', 'google play', 'app store'],
                'test_name': 'Технические проблемы'
            },
            {
                'question': 'Аппару глючит',
                'expected_keywords': ['приложение', 'обновить', 'google play', 'app store'],
                'test_name': 'Контекстное понимание технических проблем'
            }
        ]
        
        # Запускаем тесты
        for test in tests:
            result = self.test_question(
                test['question'],
                test['expected_keywords'],
                test['test_name']
            )
            self.test_results.append(result)
            time.sleep(1)  # Пауза между тестами
        
        # Анализируем результаты
        self.analyze_results()
    
    def analyze_results(self):
        """Анализирует результаты тестов"""
        print("\n" + "=" * 60)
        print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get('success', False))
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"📈 Общее количество тестов: {total_tests}")
        print(f"✅ Успешных тестов: {successful_tests}")
        print(f"❌ Неудачных тестов: {total_tests - successful_tests}")
        print(f"🎯 Процент успеха: {success_rate:.1f}%")
        
        # Анализ по источникам
        kb_tests = [r for r in self.test_results if r.get('source') == 'kb']
        llm_tests = [r for r in self.test_results if r.get('source') == 'llm']
        
        print(f"\n🔍 Анализ по источникам:")
        print(f"   📚 Из базы знаний: {len(kb_tests)} тестов")
        print(f"   🧠 Из LLM: {len(llm_tests)} тестов")
        
        # Анализ уверенности
        avg_confidence = sum(r.get('confidence', 0) for r in self.test_results) / total_tests if total_tests > 0 else 0
        print(f"   📊 Средняя уверенность: {avg_confidence:.2f}")
        
        # Детальный анализ
        print(f"\n📋 ДЕТАЛЬНЫЙ АНАЛИЗ:")
        for result in self.test_results:
            status = "✅" if result.get('success', False) else "❌"
            print(f"   {status} {result.get('test_name', 'Unknown')}: {result.get('confidence', 0):.2f}")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        if success_rate >= 90:
            print("   🎉 Отличные результаты! Система готова к продакшену.")
        elif success_rate >= 80:
            print("   👍 Хорошие результаты. Можно улучшить несколько тестов.")
        elif success_rate >= 70:
            print("   ⚠️ Средние результаты. Рекомендуется доработка.")
        else:
            print("   🚨 Низкие результаты. Требуется серьезная доработка.")
        
        if len(kb_tests) < len(llm_tests):
            print("   📚 Рекомендуется расширить базу знаний для большего покрытия.")
        
        if avg_confidence < 0.7:
            print("   📊 Рекомендуется повысить уверенность системы.")
        
        print(f"\n🎯 ФИНАЛЬНАЯ ОЦЕНКА: {success_rate:.1f}%")
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': success_rate,
            'avg_confidence': avg_confidence,
            'kb_tests': len(kb_tests),
            'llm_tests': len(llm_tests)
        }

if __name__ == "__main__":
    tester = APARUFinalTester()
    results = tester.run_comprehensive_tests()
    print(f"\n🏁 Тестирование завершено!")
    print(f"📊 Результаты: {results}")

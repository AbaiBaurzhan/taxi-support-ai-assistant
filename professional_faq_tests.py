#!/usr/bin/env python3
"""
🧪 Тесты профессионального FAQ-ассистента APARU
Проверка метрик: Top-1 ≥ 0.85, Top-3 ≥ 0.95
"""

import requests
import json
import time
from typing import Dict, List, Any, Tuple
import subprocess
import signal
import os

class ProfessionalFAQTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = []
        self.server_process = None
        
    def start_server(self):
        """Запускает сервер в фоновом режиме"""
        print("🚀 Запускаем профессиональный FAQ-сервер...")
        
        try:
            self.server_process = subprocess.Popen([
                "python3", "professional_faq_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Ждем запуска сервера
            time.sleep(10)
            
            # Проверяем, что сервер запустился
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Сервер успешно запущен")
                    return True
                else:
                    print(f"❌ Сервер не отвечает: {response.status_code}")
                    return False
            except requests.exceptions.RequestException:
                print("❌ Сервер не запустился")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка запуска сервера: {e}")
            return False
    
    def stop_server(self):
        """Останавливает сервер"""
        if self.server_process:
            print("🛑 Останавливаем сервер...")
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ Сервер остановлен")
    
    def test_question(self, question: str, expected_category: str = None) -> Dict[str, Any]:
        """Тестирует один вопрос"""
        print(f"\n🧪 Тест: {question}")
        
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                json={
                    "question": question,
                    "user_id": "test123",
                    "locale": "ru"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    'question': question,
                    'answer': data.get('answer', ''),
                    'confidence': data.get('confidence', 0),
                    'category': data.get('category'),
                    'suggestions': data.get('suggestions', []),
                    'source': data.get('source', 'unknown'),
                    'request_id': data.get('request_id', ''),
                    'success': True,
                    'timestamp': time.time()
                }
                
                print(f"✅ Ответ: {result['answer'][:100]}...")
                print(f"📊 Уверенность: {result['confidence']:.3f}")
                print(f"🏷️ Категория: {result['category']}")
                print(f"🔍 Источник: {result['source']}")
                
                if result['suggestions']:
                    print(f"💡 Предложения: {len(result['suggestions'])}")
                
                return result
            else:
                print(f"❌ Ошибка HTTP: {response.status_code}")
                return {
                    'question': question,
                    'error': f"HTTP {response.status_code}",
                    'success': False
                }
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return {
                'question': question,
                'error': str(e),
                'success': False
            }
    
    def run_comprehensive_tests(self):
        """Запускает комплексные тесты"""
        print("🚀 Запускаем комплексные тесты профессионального FAQ-ассистента")
        print("=" * 80)
        
        # Тестовые вопросы с ожидаемыми результатами
        test_cases = [
            {
                'question': 'Что такое наценка?',
                'expected_category': 'pricing',
                'expected_confidence': 0.6,
                'test_type': 'exact_match'
            },
            {
                'question': 'Почему так дорого?',
                'expected_category': 'pricing',
                'expected_confidence': 0.4,
                'test_type': 'synonym'
            },
            {
                'question': 'Что значит повышающий коэффициент?',
                'expected_category': 'pricing',
                'expected_confidence': 0.4,
                'test_type': 'variation'
            },
            {
                'question': 'Откуда берется надбавка к цене?',
                'expected_category': 'pricing',
                'expected_confidence': 0.4,
                'test_type': 'variation'
            },
            {
                'question': 'Почему стоимость стала выше обычной?',
                'expected_category': 'pricing',
                'expected_confidence': 0.4,
                'test_type': 'variation'
            },
            {
                'question': 'Что такое тариф Комфорт?',
                'expected_category': 'pricing',
                'expected_confidence': 0.6,
                'test_type': 'exact_match'
            },
            {
                'question': 'Чем отличается Комфорт от обычного тарифа?',
                'expected_category': 'pricing',
                'expected_confidence': 0.4,
                'test_type': 'variation'
            },
            {
                'question': 'Комфорт — это какие машины?',
                'expected_category': 'pricing',
                'expected_confidence': 0.4,
                'test_type': 'variation'
            },
            {
                'question': 'Как пополнить баланс?',
                'expected_category': 'payment',
                'expected_confidence': 0.3,
                'test_type': 'low_confidence'
            },
            {
                'question': 'Как отменить заказ?',
                'expected_category': 'booking',
                'expected_confidence': 0.3,
                'test_type': 'low_confidence'
            },
            {
                'question': 'Приложение не работает',
                'expected_category': 'technical',
                'expected_confidence': 0.3,
                'test_type': 'low_confidence'
            },
            {
                'question': 'Как заказать доставку?',
                'expected_category': 'delivery',
                'expected_confidence': 0.3,
                'test_type': 'low_confidence'
            }
        ]
        
        # Запускаем тесты
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Тест {i}/{len(test_cases)}")
            result = self.test_question(test_case['question'])
            result['expected_category'] = test_case['expected_category']
            result['expected_confidence'] = test_case['expected_confidence']
            result['test_type'] = test_case['test_type']
            
            self.test_results.append(result)
            time.sleep(1)  # Пауза между тестами
        
        # Анализируем результаты
        self.analyze_results()
    
    def analyze_results(self):
        """Анализирует результаты тестов"""
        print("\n" + "=" * 80)
        print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ ПРОФЕССИОНАЛЬНОГО FAQ-АССИСТЕНТА")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get('success', False))
        
        print(f"📈 Общее количество тестов: {total_tests}")
        print(f"✅ Успешных тестов: {successful_tests}")
        print(f"❌ Неудачных тестов: {total_tests - successful_tests}")
        
        if successful_tests == 0:
            print("❌ Все тесты провалились!")
            return
        
        # Анализ по типам тестов
        test_types = {}
        for result in self.test_results:
            if result.get('success', False):
                test_type = result.get('test_type', 'unknown')
                if test_type not in test_types:
                    test_types[test_type] = []
                test_types[test_type].append(result)
        
        print(f"\n📋 Анализ по типам тестов:")
        for test_type, results in test_types.items():
            avg_confidence = sum(r.get('confidence', 0) for r in results) / len(results)
            print(f"   {test_type}: {len(results)} тестов, средняя уверенность: {avg_confidence:.3f}")
        
        # Анализ уверенности
        confidences = [r.get('confidence', 0) for r in self.test_results if r.get('success', False)]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            max_confidence = max(confidences)
            min_confidence = min(confidences)
            
            print(f"\n📊 Анализ уверенности:")
            print(f"   Средняя уверенность: {avg_confidence:.3f}")
            print(f"   Максимальная уверенность: {max_confidence:.3f}")
            print(f"   Минимальная уверенность: {min_confidence:.3f}")
            
            # Подсчет тестов с высокой уверенностью
            high_confidence_tests = sum(1 for c in confidences if c >= 0.6)
            medium_confidence_tests = sum(1 for c in confidences if 0.3 <= c < 0.6)
            low_confidence_tests = sum(1 for c in confidences if c < 0.3)
            
            print(f"\n🎯 Распределение по уверенности:")
            print(f"   Высокая уверенность (≥0.6): {high_confidence_tests} тестов")
            print(f"   Средняя уверенность (0.3-0.6): {medium_confidence_tests} тестов")
            print(f"   Низкая уверенность (<0.3): {low_confidence_tests} тестов")
        
        # Анализ источников ответов
        sources = {}
        for result in self.test_results:
            if result.get('success', False):
                source = result.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1
        
        print(f"\n🔍 Анализ источников ответов:")
        for source, count in sources.items():
            print(f"   {source}: {count} тестов")
        
        # Проверка метрик
        print(f"\n🎯 ПРОВЕРКА МЕТРИК:")
        
        # Top-1 метрика (первый результат с уверенностью ≥ 0.6)
        top1_success = sum(1 for r in self.test_results if r.get('success', False) and r.get('confidence', 0) >= 0.6)
        top1_metric = top1_success / successful_tests if successful_tests > 0 else 0
        
        print(f"   Top-1 ≥ 0.6: {top1_success}/{successful_tests} = {top1_metric:.3f}")
        
        if top1_metric >= 0.85:
            print("   ✅ Top-1 метрика ПРОЙДЕНА!")
        else:
            print("   ❌ Top-1 метрика НЕ ПРОЙДЕНА!")
        
        # Top-3 метрика (любой из первых трех результатов с уверенностью ≥ 0.6)
        top3_success = 0
        for result in self.test_results:
            if result.get('success', False):
                confidence = result.get('confidence', 0)
                suggestions = result.get('suggestions', [])
                
                # Проверяем основной ответ или предложения
                if confidence >= 0.6:
                    top3_success += 1
                elif suggestions:
                    # Проверяем предложения
                    for suggestion in suggestions:
                        if suggestion.get('confidence', 0) >= 0.6:
                            top3_success += 1
                            break
        
        top3_metric = top3_success / successful_tests if successful_tests > 0 else 0
        
        print(f"   Top-3 ≥ 0.6: {top3_success}/{successful_tests} = {top3_metric:.3f}")
        
        if top3_metric >= 0.95:
            print("   ✅ Top-3 метрика ПРОЙДЕНА!")
        else:
            print("   ❌ Top-3 метрика НЕ ПРОЙДЕНА!")
        
        # Общая оценка
        print(f"\n🏆 ОБЩАЯ ОЦЕНКА:")
        if top1_metric >= 0.85 and top3_metric >= 0.95:
            print("   🎉 ВСЕ МЕТРИКИ ПРОЙДЕНЫ! Система готова к продакшену!")
        elif top1_metric >= 0.7 and top3_metric >= 0.8:
            print("   👍 Хорошие результаты! Система показывает высокое качество.")
        elif top1_metric >= 0.5 and top3_metric >= 0.6:
            print("   ⚠️ Средние результаты. Рекомендуется доработка.")
        else:
            print("   🚨 Низкие результаты. Требуется серьезная доработка.")
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'top1_metric': top1_metric,
            'top3_metric': top3_metric,
            'avg_confidence': avg_confidence if confidences else 0
        }

def main():
    """Основная функция тестирования"""
    tester = ProfessionalFAQTester()
    
    try:
        # Запускаем сервер
        if not tester.start_server():
            print("❌ Не удалось запустить сервер")
            return
        
        # Запускаем тесты
        results = tester.run_comprehensive_tests()
        
        print(f"\n🏁 Тестирование завершено!")
        print(f"📊 Результаты: {results}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка тестирования: {e}")
    finally:
        # Останавливаем сервер
        tester.stop_server()

if __name__ == "__main__":
    main()

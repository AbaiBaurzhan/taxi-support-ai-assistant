#!/usr/bin/env python3
"""
Комплексный тест системы APARU
Тестирует все аспекты улучшенной системы
"""

import requests
import json
import time
from typing import List, Dict

class APARUComprehensiveTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Инициализация комплексного теста"""
        self.base_url = base_url
        self.test_results = []
        
    def test_question(self, question: str, expected_keywords: List[str] = None) -> Dict:
        """Тестирует один вопрос"""
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={
                    "text": question,
                    "user_id": "test123",
                    "locale": "ru"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Анализируем ответ
                answer = data.get("response", "")
                source = data.get("source", "unknown")
                confidence = data.get("confidence", 0.0)
                
                # Проверяем качество ответа
                is_good_answer = self._evaluate_answer(answer, expected_keywords)
                
                result = {
                    "question": question,
                    "answer": answer,
                    "source": source,
                    "confidence": confidence,
                    "is_good": is_good_answer,
                    "status": "success"
                }
            else:
                result = {
                    "question": question,
                    "answer": "",
                    "source": "error",
                    "confidence": 0.0,
                    "is_good": False,
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            result = {
                "question": question,
                "answer": "",
                "source": "error",
                "confidence": 0.0,
                "is_good": False,
                "status": "error",
                "error": str(e)
            }
        
        self.test_results.append(result)
        return result
    
    def _evaluate_answer(self, answer: str, expected_keywords: List[str] = None) -> bool:
        """Оценивает качество ответа"""
        
        answer_lower = answer.lower()
        
        # Проверяем на плохие ответы
        bad_indicators = [
            "извините", "не уверен", "не нашел", "конкретный вопрос",
            "спасибо за обращение", "помогу найти ответ"
        ]
        
        for indicator in bad_indicators:
            if indicator in answer_lower:
                return False
        
        # Проверяем на хорошие ответы
        good_indicators = [
            "здравствуйте", "с уважением", "команда апару",
            "можно", "необходимо", "рекомендуем"
        ]
        
        good_count = sum(1 for indicator in good_indicators if indicator in answer_lower)
        
        # Проверяем ожидаемые ключевые слова
        if expected_keywords:
            keyword_count = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
            if keyword_count > 0:
                return True
        
        # Если есть хорошие индикаторы и ответ достаточно длинный
        return good_count > 0 and len(answer) > 50
    
    def run_comprehensive_test(self):
        """Запускает комплексный тест"""
        
        print("🧪 Запуск комплексного теста системы APARU...")
        print("=" * 60)
        
        # Тестовые вопросы с ожидаемыми ключевыми словами
        test_cases = [
            {
                "question": "Почему так дорого?",
                "keywords": ["наценка", "тариф", "спрос"]
            },
            {
                "question": "Как заплатить за поездку?",
                "keywords": ["пополнить", "баланс", "qiwi", "kaspi"]
            },
            {
                "question": "Можно ли заказать заранее?",
                "keywords": ["предварительный", "заранее", "свободные"]
            },
            {
                "question": "Как стать водителем?",
                "keywords": ["приложение", "регистрация", "водитель"]
            },
            {
                "question": "Приложение не открывается",
                "keywords": ["обновить", "google play", "app store"]
            },
            {
                "question": "Что означает наценка?",
                "keywords": ["наценка", "тариф", "спрос"]
            },
            {
                "question": "Где найти цену?",
                "keywords": ["расценка", "таксометр", "приложение"]
            },
            {
                "question": "Как доставить посылку?",
                "keywords": ["доставка", "приложение", "курьер"]
            },
            {
                "question": "Что такое комфорт?",
                "keywords": ["комфорт", "машина", "тариф"]
            },
            {
                "question": "Почему считают время?",
                "keywords": ["моточасы", "время", "поездка"]
            },
            {
                "question": "Как отменить заказ?",
                "keywords": ["отменить", "кнопка", "водитель"]
            },
            {
                "question": "Водитель не приехал",
                "keywords": ["позвонить", "поддержка", "водитель"]
            },
            {
                "question": "Как связаться с водителем?",
                "keywords": ["позвонить", "кнопка", "водитель"]
            },
            {
                "question": "Где находится водитель?",
                "keywords": ["отслеживать", "карта", "местоположение"]
            },
            {
                "question": "Что такое эконом?",
                "keywords": ["эконом", "базовый", "тариф"]
            },
            {
                "question": "Как работает универсал?",
                "keywords": ["универсал", "багаж", "груз"]
            },
            {
                "question": "Можно ли заказать грузовое?",
                "keywords": ["грузовое", "груз", "приложение"]
            },
            {
                "question": "Как заказать эвакуатор?",
                "keywords": ["эвакуатор", "приложение", "адрес"]
            },
            {
                "question": "Можно ли оплатить наличными?",
                "keywords": ["наличные", "баланс", "карта"]
            },
            {
                "question": "Как привязать карту?",
                "keywords": ["карта", "профиль", "привязать"]
            },
            {
                "question": "Забыл вещи в такси",
                "keywords": ["забыл", "вещи", "водитель"]
            },
            {
                "question": "Как оставить отзыв?",
                "keywords": ["отзыв", "оценить", "поездка"]
            },
            {
                "question": "Что такое промокод?",
                "keywords": ["промокод", "скидка", "код"]
            },
            {
                "question": "Можно ли заказать для мамы?",
                "keywords": ["другого", "человека", "адрес"]
            },
            {
                "question": "Как работает рейтинг?",
                "keywords": ["рейтинг", "оценка", "водитель"]
            },
            {
                "question": "Водитель ведет себя плохо",
                "keywords": ["жалоба", "поддержка", "водитель"]
            }
        ]
        
        # Запускаем тесты
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔍 Тест {i}/{len(test_cases)}: {test_case['question']}")
            
            result = self.test_question(
                test_case['question'], 
                test_case['keywords']
            )
            
            if result['status'] == 'success':
                if result['is_good']:
                    print(f"✅ Успех: {result['answer'][:80]}...")
                    print(f"   Источник: {result['source']}, Уверенность: {result['confidence']:.2f}")
                else:
                    print(f"❌ Плохой ответ: {result['answer'][:80]}...")
                    print(f"   Источник: {result['source']}, Уверенность: {result['confidence']:.2f}")
            else:
                print(f"💥 Ошибка: {result.get('error', 'Unknown error')}")
            
            time.sleep(0.5)  # Небольшая пауза между запросами
        
        # Анализируем результаты
        self._analyze_results()
    
    def _analyze_results(self):
        """Анализирует результаты тестирования"""
        
        print("\n" + "=" * 60)
        print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['status'] == 'success')
        good_answers = sum(1 for r in self.test_results if r['is_good'])
        
        print(f"📈 Общая статистика:")
        print(f"   Всего тестов: {total_tests}")
        print(f"   Успешных запросов: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"   Хороших ответов: {good_answers} ({good_answers/total_tests*100:.1f}%)")
        
        # Анализ по источникам
        sources = {}
        for result in self.test_results:
            source = result['source']
            if source not in sources:
                sources[source] = {'total': 0, 'good': 0}
            sources[source]['total'] += 1
            if result['is_good']:
                sources[source]['good'] += 1
        
        print(f"\n📊 Анализ по источникам:")
        for source, stats in sources.items():
            percentage = stats['good'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"   {source}: {stats['good']}/{stats['total']} ({percentage:.1f}%)")
        
        # Плохие ответы
        bad_results = [r for r in self.test_results if not r['is_good'] and r['status'] == 'success']
        if bad_results:
            print(f"\n❌ Плохие ответы ({len(bad_results)}):")
            for result in bad_results[:5]:  # Показываем первые 5
                print(f"   - {result['question']}: {result['answer'][:60]}...")
        
        # Ошибки
        error_results = [r for r in self.test_results if r['status'] == 'error']
        if error_results:
            print(f"\n💥 Ошибки ({len(error_results)}):")
            for result in error_results:
                print(f"   - {result['question']}: {result.get('error', 'Unknown error')}")
        
        print(f"\n🎯 Итоговая оценка: {good_answers/total_tests*100:.1f}% хороших ответов")
        
        if good_answers/total_tests >= 0.8:
            print("🎉 Отлично! Система работает хорошо!")
        elif good_answers/total_tests >= 0.6:
            print("👍 Хорошо! Система работает приемлемо.")
        else:
            print("⚠️ Требуются улучшения!")

if __name__ == "__main__":
    print("🚀 Комплексный тест системы APARU")
    print("Убедитесь, что сервер запущен на http://localhost:8000")
    
    # Запускаем тест
    tester = APARUComprehensiveTest()
    tester.run_comprehensive_test()

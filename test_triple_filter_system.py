#!/usr/bin/env python3
"""
🧪 КОМПЛЕКСНЫЙ ТЕСТ ТРЕХУРОВНЕВОЙ СИСТЕМЫ ПОИСКА

Тестирует все аспекты новой системы поиска:
- Filter 1: Question Variations (50% приоритет)
- Filter 2: Keywords (30% приоритет)  
- Filter 3: Answer Content (20% приоритет)
- Морфологический fallback
"""

import requests
import json
import time
from typing import Dict, List, Tuple

# Конфигурация тестов
API_BASE = "http://localhost:8000"
TEST_USER_ID = "test_user_triple_filter"
TEST_LOCALE = "ru"

class TripleFilterTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def wait_for_server(self, max_attempts=10):
        """Ждем запуска сервера"""
        print("🔄 Ожидание запуска сервера...")
        for i in range(max_attempts):
            try:
                response = requests.get(f"{API_BASE}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Сервер запущен и готов к тестированию")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
            print(f"   Попытка {i+1}/{max_attempts}...")
        
        print("❌ Сервер не запустился за отведенное время")
        return False
    
    def test_chat_endpoint(self, query: str, expected_keywords: List[str] = None, 
                          test_name: str = None) -> Dict:
        """Тестирует один запрос к API"""
        if not test_name:
            test_name = query
            
        print(f"\n🧪 Тест: {test_name}")
        print(f"📝 Запрос: '{query}'")
        
        try:
            response = requests.post(
                f"{API_BASE}/chat",
                json={
                    "text": query,
                    "user_id": TEST_USER_ID,
                    "locale": TEST_LOCALE
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    "test_name": test_name,
                    "query": query,
                    "success": True,
                    "response": data.get("response", ""),
                    "confidence": data.get("confidence", 0),
                    "source": data.get("source", ""),
                    "intent": data.get("intent", ""),
                    "expected_keywords": expected_keywords
                }
                
                # Проверяем наличие ожидаемых ключевых слов
                if expected_keywords:
                    response_text = data.get("response", "").lower()
                    found_keywords = [kw for kw in expected_keywords if kw.lower() in response_text]
                    result["found_keywords"] = found_keywords
                    result["keyword_match"] = len(found_keywords) > 0
                
                print(f"✅ Успешно")
                print(f"   📊 Уверенность: {data.get('confidence', 0):.2f}")
                print(f"   🔍 Источник: {data.get('source', '')}")
                print(f"   🎯 Intent: {data.get('intent', '')}")
                print(f"   💬 Ответ: {data.get('response', '')[:100]}...")
                
                if expected_keywords and result.get("keyword_match"):
                    print(f"   🔑 Найденные ключевые слова: {result['found_keywords']}")
                
                self.passed_tests += 1
                
            else:
                result = {
                    "test_name": test_name,
                    "query": query,
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                print(f"❌ Ошибка: HTTP {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            result = {
                "test_name": test_name,
                "query": query,
                "success": False,
                "error": str(e)
            }
            print(f"❌ Исключение: {e}")
            self.failed_tests += 1
        
        self.total_tests += 1
        self.results.append(result)
        return result
    
    def run_all_tests(self):
        """Запускает все тесты трехуровневой системы"""
        print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ ТРЕХУРОВНЕВОЙ СИСТЕМЫ ПОИСКА")
        print("=" * 80)
        
        # Ждем запуска сервера
        if not self.wait_for_server():
            return False
        
        # Группа 1: Тесты на различение похожих вопросов
        print("\n🎯 ГРУППА 1: ТЕСТЫ НА РАЗЛИЧЕНИЕ ПОХОЖИХ ВОПРОСОВ")
        print("-" * 60)
        
        self.test_chat_endpoint(
            "доставка",
            ["доставка", "курьер", "посылка"],
            "Короткий запрос 'доставка'"
        )
        
        self.test_chat_endpoint(
            "что такое доставка",
            ["доставка", "услуга", "курьер"],
            "Вопрос 'что такое доставка'"
        )
        
        self.test_chat_endpoint(
            "как работает доставка",
            ["работает", "следующим образом", "приложение"],
            "Вопрос 'как работает доставка'"
        )
        
        # Группа 2: Тесты трехуровневой системы поиска
        print("\n🔍 ГРУППА 2: ТЕСТЫ ТРЕХУРОВНЕВОЙ СИСТЕМЫ ПОИСКА")
        print("-" * 60)
        
        self.test_chat_endpoint(
            "как пополнить баланс",
            ["баланс", "пополнить", "платежные системы"],
            "Вопрос о пополнении баланса"
        )
        
        self.test_chat_endpoint(
            "сколько стоит поездка",
            ["цена", "стоимость", "тариф", "расчет"],
            "Вопрос о стоимости поездки"
        )
        
        self.test_chat_endpoint(
            "какие карты у меня есть",
            ["карта", "карты", "привязанные"],
            "Вопрос о картах"
        )
        
        # Группа 3: Тесты морфологического анализа
        print("\n🧠 ГРУППА 3: ТЕСТЫ МОРФОЛОГИЧЕСКОГО АНАЛИЗА")
        print("-" * 60)
        
        self.test_chat_endpoint(
            "доставки",
            ["доставка"],
            "Слово с окончанием 'доставки'"
        )
        
        self.test_chat_endpoint(
            "водитель",
            ["водитель", "шофер", "таксист"],
            "Слово 'водитель'"
        )
        
        self.test_chat_endpoint(
            "водители",
            ["водитель"],
            "Слово с окончанием 'водители'"
        )
        
        # Группа 4: Тесты сложных запросов
        print("\n🎪 ГРУППА 4: ТЕСТЫ СЛОЖНЫХ ЗАПРОСОВ")
        print("-" * 60)
        
        self.test_chat_endpoint(
            "как отменить заказ такси",
            ["отменить", "заказ"],
            "Сложный запрос об отмене заказа"
        )
        
        self.test_chat_endpoint(
            "где мой водитель сейчас",
            ["водитель", "статус", "поездка"],
            "Запрос о статусе поездки"
        )
        
        self.test_chat_endpoint(
            "пришлите мне чек за поездку",
            ["чек", "квитанция", "документ"],
            "Запрос чека"
        )
        
        # Группа 5: Тесты edge cases
        print("\n⚠️ ГРУППА 5: ТЕСТЫ EDGE CASES")
        print("-" * 60)
        
        self.test_chat_endpoint(
            "хелло",
            [],
            "Непонятный запрос"
        )
        
        self.test_chat_endpoint(
            "спасибо",
            [],
            "Благодарность"
        )
        
        self.test_chat_endpoint(
            "123456",
            [],
            "Числовой запрос"
        )
        
        return True
    
    def generate_report(self):
        """Генерирует отчет о тестировании"""
        print("\n" + "=" * 80)
        print("📊 ОТЧЕТ О ТЕСТИРОВАНИИ ТРЕХУРОВНЕВОЙ СИСТЕМЫ ПОИСКА")
        print("=" * 80)
        
        print(f"📈 Общая статистика:")
        print(f"   Всего тестов: {self.total_tests}")
        print(f"   ✅ Успешных: {self.passed_tests}")
        print(f"   ❌ Неудачных: {self.failed_tests}")
        print(f"   📊 Процент успеха: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        # Анализ по группам
        print(f"\n🎯 Анализ по источникам ответов:")
        sources = {}
        for result in self.results:
            if result.get("success"):
                source = result.get("source", "unknown")
                sources[source] = sources.get(source, 0) + 1
        
        for source, count in sources.items():
            percentage = (count / self.passed_tests * 100) if self.passed_tests > 0 else 0
            print(f"   {source}: {count} ({percentage:.1f}%)")
        
        # Анализ уверенности
        print(f"\n📊 Анализ уверенности:")
        confidences = [r.get("confidence", 0) for r in self.results if r.get("success")]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            min_confidence = min(confidences)
            max_confidence = max(confidences)
            print(f"   Средняя уверенность: {avg_confidence:.3f}")
            print(f"   Минимальная уверенность: {min_confidence:.3f}")
            print(f"   Максимальная уверенность: {max_confidence:.3f}")
        
        # Неудачные тесты
        failed_tests = [r for r in self.results if not r.get("success")]
        if failed_tests:
            print(f"\n❌ Неудачные тесты:")
            for test in failed_tests:
                print(f"   - {test['test_name']}: {test.get('error', 'Unknown error')}")
        
        # Успешные тесты с низкой уверенностью
        low_confidence_tests = [r for r in self.results 
                               if r.get("success") and r.get("confidence", 0) < 0.3]
        if low_confidence_tests:
            print(f"\n⚠️ Тесты с низкой уверенностью (< 0.3):")
            for test in low_confidence_tests:
                print(f"   - {test['test_name']}: {test.get('confidence', 0):.3f}")
        
        print("\n🎉 Тестирование завершено!")
        
        # Сохраняем результаты в файл
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0
            },
            "results": self.results
        }
        
        with open("triple_filter_test_results.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Подробные результаты сохранены в: triple_filter_test_results.json")

def main():
    """Основная функция тестирования"""
    tester = TripleFilterTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            tester.generate_report()
        else:
            print("❌ Тестирование не удалось запустить")
            
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🧪 КОМПЛЕКСНЫЙ ТЕСТ ПОКРЫТИЯ БАЗЫ ЗНАНИЙ

Проверяет каждое ключевое слово (keywords) и каждую вариацию вопросов (question_variations)
из kb.json на корректность ответов
"""

import requests
import json
import time
from typing import Dict, List, Tuple

# Конфигурация тестов
API_BASE = "http://localhost:8000"
TEST_USER_ID = "test_kb_coverage"
TEST_LOCALE = "ru"

class KnowledgeBaseCoverageTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.kb_data = None
        
    def load_kb_data(self):
        """Загружает данные базы знаний"""
        try:
            with open('backend/kb.json', 'r', encoding='utf-8') as f:
                self.kb_data = json.load(f)
            print(f"✅ Загружена база знаний: {len(self.kb_data.get('faq', []))} FAQ записей")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки kb.json: {e}")
            return False
    
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
    
    def test_query(self, query: str, expected_answer_snippet: str = None, test_type: str = "unknown") -> Dict:
        """Тестирует один запрос к API"""
        print(f"   🧪 Тестирую: '{query}'")
        
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
                    "query": query,
                    "test_type": test_type,
                    "success": True,
                    "response": data.get("response", ""),
                    "confidence": data.get("confidence", 0),
                    "source": data.get("source", ""),
                    "intent": data.get("intent", ""),
                    "expected_answer_snippet": expected_answer_snippet
                }
                
                # Проверяем соответствие ожидаемому ответу
                if expected_answer_snippet:
                    response_text = data.get("response", "").lower()
                    expected_snippet = expected_answer_snippet.lower()
                    if expected_snippet in response_text:
                        result["answer_match"] = True
                        print(f"      ✅ Ответ соответствует ожидаемому")
                    else:
                        result["answer_match"] = False
                        print(f"      ⚠️ Ответ не соответствует ожидаемому")
                        print(f"      📝 Ожидалось: {expected_answer_snippet[:50]}...")
                        print(f"      💬 Получено: {data.get('response', '')[:50]}...")
                
                print(f"      📊 Уверенность: {data.get('confidence', 0):.2f}")
                print(f"      🔍 Источник: {data.get('source', '')}")
                
                self.passed_tests += 1
                
            else:
                result = {
                    "query": query,
                    "test_type": test_type,
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                print(f"      ❌ HTTP {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            result = {
                "query": query,
                "test_type": test_type,
                "success": False,
                "error": str(e)
            }
            print(f"      ❌ Исключение: {e}")
            self.failed_tests += 1
        
        self.total_tests += 1
        self.results.append(result)
        return result
    
    def test_keywords_coverage(self):
        """Тестирует все ключевые слова из базы знаний"""
        print("\n🔑 ТЕСТИРОВАНИЕ КЛЮЧЕВЫХ СЛОВ (KEYWORDS)")
        print("=" * 60)
        
        if not self.kb_data:
            print("❌ База знаний не загружена")
            return
        
        faq_items = self.kb_data.get("faq", [])
        print(f"📊 Найдено {len(faq_items)} FAQ записей для тестирования")
        
        for i, item in enumerate(faq_items, 1):
            question = item.get("question", "")
            answer = item.get("answer", "")
            keywords = item.get("keywords", [])
            
            print(f"\n📋 FAQ {i}/{len(faq_items)}: {question}")
            print(f"🔑 Ключевых слов: {len(keywords)}")
            
            # Тестируем каждое ключевое слово
            for keyword in keywords:
                if keyword.strip():  # Пропускаем пустые ключевые слова
                    # Берем первые 30 символов ответа для проверки соответствия
                    answer_snippet = answer[:100] if answer else ""
                    self.test_query(
                        keyword, 
                        answer_snippet, 
                        f"keyword_for_{question[:30]}"
                    )
    
    def test_question_variations_coverage(self):
        """Тестирует все вариации вопросов из базы знаний"""
        print("\n📝 ТЕСТИРОВАНИЕ ВАРИАЦИЙ ВОПРОСОВ (QUESTION_VARIATIONS)")
        print("=" * 60)
        
        if not self.kb_data:
            print("❌ База знаний не загружена")
            return
        
        faq_items = self.kb_data.get("faq", [])
        print(f"📊 Найдено {len(faq_items)} FAQ записей для тестирования")
        
        for i, item in enumerate(faq_items, 1):
            question = item.get("question", "")
            answer = item.get("answer", "")
            variations = item.get("question_variations", [])
            
            print(f"\n📋 FAQ {i}/{len(faq_items)}: {question}")
            print(f"📝 Вариаций вопросов: {len(variations)}")
            
            # Тестируем каждую вариацию вопроса
            for variation in variations:
                if variation.strip():  # Пропускаем пустые вариации
                    # Берем первые 100 символов ответа для проверки соответствия
                    answer_snippet = answer[:100] if answer else ""
                    self.test_query(
                        variation, 
                        answer_snippet, 
                        f"variation_for_{question[:30]}"
                    )
    
    def run_comprehensive_test(self):
        """Запускает комплексное тестирование покрытия базы знаний"""
        print("🚀 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ПОКРЫТИЯ БАЗЫ ЗНАНИЙ")
        print("=" * 80)
        
        # Загружаем базу знаний
        if not self.load_kb_data():
            return False
        
        # Ждем запуска сервера
        if not self.wait_for_server():
            return False
        
        # Тестируем ключевые слова
        self.test_keywords_coverage()
        
        # Тестируем вариации вопросов
        self.test_question_variations_coverage()
        
        return True
    
    def generate_detailed_report(self):
        """Генерирует детальный отчет о тестировании"""
        print("\n" + "=" * 80)
        print("📊 ДЕТАЛЬНЫЙ ОТЧЕТ О ТЕСТИРОВАНИИ ПОКРЫТИЯ БАЗЫ ЗНАНИЙ")
        print("=" * 80)
        
        print(f"📈 Общая статистика:")
        print(f"   Всего тестов: {self.total_tests}")
        print(f"   ✅ Успешных: {self.passed_tests}")
        print(f"   ❌ Неудачных: {self.failed_tests}")
        print(f"   📊 Процент успеха: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        # Анализ по типам тестов
        print(f"\n🎯 Анализ по типам тестов:")
        test_types = {}
        for result in self.results:
            if result.get("success"):
                test_type = result.get("test_type", "unknown")
                test_types[test_type] = test_types.get(test_type, 0) + 1
        
        for test_type, count in test_types.items():
            percentage = (count / self.passed_tests * 100) if self.passed_tests > 0 else 0
            print(f"   {test_type}: {count} ({percentage:.1f}%)")
        
        # Анализ по источникам ответов
        print(f"\n🔍 Анализ по источникам ответов:")
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
        
        # Анализ соответствия ответов
        print(f"\n🎯 Анализ соответствия ответов:")
        answer_matches = [r.get("answer_match", False) for r in self.results if r.get("success")]
        if answer_matches:
            match_count = sum(answer_matches)
            match_percentage = (match_count / len(answer_matches) * 100) if answer_matches else 0
            print(f"   Соответствие ожидаемым ответам: {match_count}/{len(answer_matches)} ({match_percentage:.1f}%)")
        
        # Неудачные тесты
        failed_tests = [r for r in self.results if not r.get("success")]
        if failed_tests:
            print(f"\n❌ Неудачные тесты:")
            for test in failed_tests[:10]:  # Показываем первые 10
                print(f"   - {test['query'][:50]}...: {test.get('error', 'Unknown error')}")
            if len(failed_tests) > 10:
                print(f"   ... и еще {len(failed_tests) - 10} неудачных тестов")
        
        # Тесты с низкой уверенностью
        low_confidence_tests = [r for r in self.results 
                               if r.get("success") and r.get("confidence", 0) < 0.5]
        if low_confidence_tests:
            print(f"\n⚠️ Тесты с низкой уверенностью (< 0.5):")
            for test in low_confidence_tests[:10]:  # Показываем первые 10
                print(f"   - {test['query'][:50]}...: {test.get('confidence', 0):.3f}")
            if len(low_confidence_tests) > 10:
                print(f"   ... и еще {len(low_confidence_tests) - 10} тестов с низкой уверенностью")
        
        print("\n🎉 Комплексное тестирование покрытия базы знаний завершено!")
        
        # Сохраняем результаты в файл
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0
            },
            "kb_coverage": {
                "total_faq_items": len(self.kb_data.get("faq", [])) if self.kb_data else 0,
                "total_keywords_tested": len([r for r in self.results if "keyword" in r.get("test_type", "")]),
                "total_variations_tested": len([r for r in self.results if "variation" in r.get("test_type", "")])
            },
            "results": self.results
        }
        
        with open("kb_coverage_test_results.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Подробные результаты сохранены в: kb_coverage_test_results.json")

def main():
    """Основная функция тестирования"""
    tester = KnowledgeBaseCoverageTester()
    
    try:
        success = tester.run_comprehensive_test()
        if success:
            tester.generate_detailed_report()
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

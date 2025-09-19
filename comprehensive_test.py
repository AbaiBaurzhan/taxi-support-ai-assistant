#!/usr/bin/env python3
"""
🧪 Комплексное тестирование всех вариантов вопросов APARU AI
Тестирует морфологию, синонимы, перефразы и контекст
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Any

class ComprehensiveTester:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.test_results = []
        
    def test_question(self, question: str, expected_category: str = None) -> Dict[str, Any]:
        """Тестирует один вопрос"""
        try:
            payload = {
                "text": question,
                "user_id": f"test_{int(time.time())}",
                "locale": "ru"
            }
            
            start_time = time.time()
            response = requests.post(f"{self.api_url}/chat", json=payload, timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "question": question,
                    "answer": result.get("response", ""),
                    "intent": result.get("intent", ""),
                    "confidence": result.get("confidence", 0.0),
                    "source": result.get("source", ""),
                    "response_time": end_time - start_time,
                    "success": result.get("response", "") != "Нужна уточняющая информация",
                    "expected_category": expected_category
                }
            else:
                return {
                    "question": question,
                    "answer": f"ERROR: {response.status_code}",
                    "intent": "error",
                    "confidence": 0.0,
                    "source": "error",
                    "response_time": end_time - start_time,
                    "success": False,
                    "expected_category": expected_category
                }
        except Exception as e:
            return {
                "question": question,
                "answer": f"EXCEPTION: {str(e)}",
                "intent": "error",
                "confidence": 0.0,
                "source": "error",
                "response_time": 0.0,
                "success": False,
                "expected_category": expected_category
            }
    
    def run_comprehensive_test(self):
        """Запускает комплексное тестирование"""
        print("🧪 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ APARU AI")
        print("=" * 60)
        
        # Тестовые вопросы по категориям
        test_categories = {
            "НАЦЕНКА": [
                "Что такое наценка?",
                "Что такое наценки?",
                "Что такое наценку?",
                "Что такое наценкой?",
                "Почему так дорого?",
                "Откуда доплата?",
                "Откуда доплаты?",
                "Откуда доплату?",
                "Что за надбавка?",
                "Что за надбавки?",
                "Повышающий коэффициент?",
                "Повышающие коэффициенты?",
                "Дополнительная оплата?",
                "Дополнительные оплаты?",
                "Надбавка к цене?",
                "Надбавки к цене?",
                "Повышение стоимости?",
                "Повышения стоимости?",
                "Доплата в заказе?",
                "Доплаты в заказе?",
                "Коэффициент спроса?",
                "Коэффициенты спроса?"
            ],
            
            "ДОСТАВКА": [
                "Как заказать доставку?",
                "Как заказать доставки?",
                "Как заказать доставку?",
                "Как отправить посылку?",
                "Как отправить посылки?",
                "Как отправить посылку?",
                "Вызвать курьера?",
                "Вызвать курьера?",
                "Заказ доставки?",
                "Заказ доставку?",
                "Регистрировать доставку?",
                "Регистрировать доставки?",
                "Оформить доставку?",
                "Оформить доставки?",
                "Вызвать машину для доставки?",
                "Вызвать машину для доставку?",
                "Перевозка посылки?",
                "Перевозка посылку?"
            ],
            
            "БАЛАНС": [
                "Как пополнить баланс?",
                "Как пополнить баланса?",
                "Как пополнить балансу?",
                "Как пополнить балансом?",
                "Пополнить счет?",
                "Пополнить счета?",
                "Пополнить счету?",
                "Пополнить счетом?",
                "Пополнить кошелек?",
                "Пополнить кошелька?",
                "Пополнить кошельку?",
                "Пополнить кошельком?",
                "Управление балансом?",
                "Управление баланса?",
                "Пополнить через?",
                "Пополнение баланса?",
                "Пополнения баланса?"
            ],
            
            "КОМФОРТ": [
                "Что такое тариф комфорт?",
                "Что такое тариф комфорта?",
                "Что такое тариф комфорту?",
                "Что такое тариф комфортом?",
                "Комфорт класс?",
                "Комфорта класс?",
                "Комфорт тариф?",
                "Комфорта тариф?",
                "Комфорт класс машины?",
                "Комфорта класс машины?",
                "Комфорт автомобиль?",
                "Комфорта автомобиль?"
            ],
            
            "МОТОЧАСЫ": [
                "Что такое моточасы?",
                "Что такое моточасов?",
                "Что такое моточасам?",
                "Что такое моточасами?",
                "Время поездки?",
                "Времени поездки?",
                "Времени поездку?",
                "Оплата за время?",
                "Оплата за времени?",
                "Поминутная оплата?",
                "Поминутные оплаты?",
                "Время в тарифе?",
                "Времени в тарифе?",
                "Длительные заказы?",
                "Длительных заказов?"
            ],
            
            "ПРИЛОЖЕНИЕ": [
                "Приложение не работает?",
                "Приложения не работает?",
                "Приложению не работает?",
                "Приложением не работает?",
                "Приложение не запускается?",
                "Приложения не запускается?",
                "Обновление приложения?",
                "Обновления приложения?",
                "Настройка gps?",
                "Настройки gps?",
                "Приложение вылетает?",
                "Приложения вылетает?",
                "Приложение зависает?",
                "Приложения зависает?"
            ],
            
            "СИНОНИМЫ И ПЕРЕФРАЗЫ": [
                "Почему дорого?",
                "Откуда доплата?",
                "Что за надбавка?",
                "Как отправить посылку?",
                "Как вызвать курьера?",
                "Как пополнить счет?",
                "Как пополнить кошелек?",
                "Что такое комфорт класс?",
                "Что такое премиум тариф?",
                "Что такое время поездки?",
                "Что такое оплата за время?",
                "Приложение не запускается?",
                "Приложение вылетает?",
                "Приложение зависает?"
            ],
            
            "РАЗГОВОРНЫЕ ВАРИАНТЫ": [
                "А что с наценкой?",
                "А что с наценками?",
                "А что с доставкой?",
                "А что с доставками?",
                "А что с балансом?",
                "А что с балансами?",
                "А что с комфортом?",
                "А что с комфортами?",
                "А что с моточасами?",
                "А что с приложением?",
                "А что с приложениями?"
            ],
            
            "ВОПРОСЫ С ОПЕЧАТКАМИ": [
                "Что такое наценка?",  # наценка
                "Что такое наценка?",  # наценка
                "Что такое доставка?",  # доставка
                "Что такое баланс?",  # баланс
                "Что такое комфорт?",  # комфорт
                "Что такое моточасы?",  # моточасы
                "Приложение не работает?"  # приложение
            ]
        }
        
        total_questions = sum(len(questions) for questions in test_categories.values())
        print(f"📊 Всего вопросов для тестирования: {total_questions}")
        print()
        
        # Тестируем каждую категорию
        category_results = {}
        all_results = []
        
        for category, questions in test_categories.items():
            print(f"🔍 Тестируем категорию: {category}")
            print("-" * 40)
            
            category_success = 0
            category_total = len(questions)
            
            for question in questions:
                result = self.test_question(question, category)
                all_results.append(result)
                
                if result["success"]:
                    category_success += 1
                    print(f"✅ {question}")
                    print(f"   Ответ: {result['answer'][:80]}...")
                    print(f"   Уверенность: {result['confidence']:.2f}")
                else:
                    print(f"❌ {question}")
                    print(f"   Ответ: {result['answer']}")
                    print(f"   Уверенность: {result['confidence']:.2f}")
                
                print()
            
            category_results[category] = {
                "success": category_success,
                "total": category_total,
                "success_rate": category_success / category_total if category_total > 0 else 0
            }
            
            print(f"📈 {category}: {category_success}/{category_total} ({category_success/category_total*100:.1f}%)")
            print()
        
        # Общая статистика
        total_success = sum(result["success"] for result in all_results)
        total_questions = len(all_results)
        overall_success_rate = total_success / total_questions if total_questions > 0 else 0
        
        print("📊 ОБЩАЯ СТАТИСТИКА")
        print("=" * 60)
        print(f"Всего вопросов: {total_questions}")
        print(f"Успешных ответов: {total_success}")
        print(f"Общая успешность: {overall_success_rate:.1%}")
        print()
        
        # Статистика по категориям
        print("📈 СТАТИСТИКА ПО КАТЕГОРИЯМ:")
        for category, stats in category_results.items():
            print(f"   {category}: {stats['success']}/{stats['total']} ({stats['success_rate']:.1%})")
        print()
        
        # Время ответа
        avg_response_time = sum(result["response_time"] for result in all_results) / len(all_results)
        print(f"⏱️ Среднее время ответа: {avg_response_time:.3f}s")
        print()
        
        # Уверенность
        avg_confidence = sum(result["confidence"] for result in all_results) / len(all_results)
        print(f"🎯 Средняя уверенность: {avg_confidence:.2f}")
        print()
        
        # Проблемные вопросы
        failed_questions = [result for result in all_results if not result["success"]]
        if failed_questions:
            print("❌ ПРОБЛЕМНЫЕ ВОПРОСЫ:")
            for result in failed_questions:
                print(f"   - {result['question']}")
            print()
        
        # Сохраняем результаты
        self.test_results = all_results
        return all_results

def main():
    """Основная функция"""
    tester = ComprehensiveTester()
    results = tester.run_comprehensive_test()
    
    # Сохраняем результаты в файл
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comprehensive_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Результаты сохранены в файл: {filename}")

if __name__ == "__main__":
    main()
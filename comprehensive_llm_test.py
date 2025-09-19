#!/usr/bin/env python3
"""
🧪 КОМПЛЕКСНЫЙ ТЕСТ LLM МОДЕЛИ APARU
Тестирует все вопросы на правильные ответы
"""

import requests
import json
import time
from datetime import datetime

class LLMModelTester:
    def __init__(self):
        self.local_server_url = "http://172.20.10.5:8001"
        self.railway_url = "https://taxi-support-ai-assistant-production.up.railway.app"
        
        # Тестовые вопросы из базы знаний
        self.test_questions = [
            # Наценки и тарифы
            "Что такое наценка?",
            "Почему появилась наценка?",
            "Как рассчитывается наценка?",
            "Когда действует наценка?",
            "Можно ли отменить наценку?",
            
            # Доставка
            "Как заказать доставку?",
            "Сколько стоит доставка?",
            "Какие есть способы доставки?",
            "Можно ли отследить доставку?",
            "Что делать если доставка опоздала?",
            
            # Баланс и платежи
            "Как пополнить баланс?",
            "Какие способы оплаты есть?",
            "Почему не проходит платеж?",
            "Как проверить баланс?",
            "Можно ли вернуть деньги?",
            
            # Приложение
            "Приложение не работает",
            "Как обновить приложение?",
            "Почему приложение тормозит?",
            "Как войти в приложение?",
            "Забыл пароль от приложения",
            
            # Разные формулировки
            "наценки",
            "доставка",
            "баланс",
            "приложение",
            "тариф комфорта"
        ]
        
        # Ожидаемые категории ответов
        self.expected_categories = {
            "наценка": ["наценка", "тариф", "цена", "стоимость"],
            "доставка": ["доставка", "курьер", "заказ"],
            "баланс": ["баланс", "платеж", "оплата", "пополнить"],
            "приложение": ["приложение", "обновить", "войти", "пароль"]
        }
    
    def test_local_server(self):
        """Тестирует локальный сервер с LLM"""
        print("🧪 ТЕСТИРУЮ ЛОКАЛЬНЫЙ СЕРВЕР С LLM МОДЕЛЬЮ")
        print("=" * 60)
        
        results = []
        total_questions = len(self.test_questions)
        
        for i, question in enumerate(self.test_questions, 1):
            print(f"\n📝 Вопрос {i}/{total_questions}: {question}")
            
            try:
                start_time = time.time()
                
                payload = {
                    "text": question,
                    "user_id": f"test_{i}",
                    "locale": "ru"
                }
                
                response = requests.post(
                    f"{self.local_server_url}/chat",
                    json=payload,
                    timeout=180  # Увеличиваем таймаут для LLM
                )
                
                processing_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Анализируем ответ
                    answer = data.get("response", "")
                    category = data.get("intent", "unknown")
                    confidence = data.get("confidence", 0.0)
                    source = data.get("source", "unknown")
                    
                    # Проверяем качество ответа
                    quality_score = self._analyze_answer_quality(question, answer, category)
                    
                    result = {
                        "question": question,
                        "answer": answer[:100] + "..." if len(answer) > 100 else answer,
                        "category": category,
                        "confidence": confidence,
                        "source": source,
                        "processing_time": round(processing_time, 2),
                        "quality_score": quality_score,
                        "status": "success"
                    }
                    
                    print(f"✅ Ответ: {answer[:50]}...")
                    print(f"📊 Категория: {category}, Уверенность: {confidence:.2f}")
                    print(f"⏱️ Время: {processing_time:.2f}с, Качество: {quality_score:.2f}")
                    
                else:
                    result = {
                        "question": question,
                        "answer": f"Ошибка: {response.status_code}",
                        "category": "error",
                        "confidence": 0.0,
                        "source": "error",
                        "processing_time": processing_time,
                        "quality_score": 0.0,
                        "status": "error"
                    }
                    
                    print(f"❌ Ошибка: {response.status_code}")
                
                results.append(result)
                
            except Exception as e:
                result = {
                    "question": question,
                    "answer": f"Исключение: {str(e)}",
                    "category": "error",
                    "confidence": 0.0,
                    "source": "error",
                    "processing_time": 0.0,
                    "quality_score": 0.0,
                    "status": "exception"
                }
                
                print(f"❌ Исключение: {e}")
                results.append(result)
        
        return results
    
    def test_railway_server(self):
        """Тестирует Railway сервер"""
        print("\n🌐 ТЕСТИРУЮ RAILWAY СЕРВЕР")
        print("=" * 60)
        
        results = []
        total_questions = len(self.test_questions)
        
        for i, question in enumerate(self.test_questions, 1):
            print(f"\n📝 Вопрос {i}/{total_questions}: {question}")
            
            try:
                start_time = time.time()
                
                payload = {
                    "text": question,
                    "user_id": f"test_{i}",
                    "locale": "ru"
                }
                
                response = requests.post(
                    f"{self.railway_url}/chat",
                    json=payload,
                    timeout=60
                )
                
                processing_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    answer = data.get("response", "")
                    category = data.get("intent", "unknown")
                    confidence = data.get("confidence", 0.0)
                    source = data.get("source", "unknown")
                    
                    quality_score = self._analyze_answer_quality(question, answer, category)
                    
                    result = {
                        "question": question,
                        "answer": answer[:100] + "..." if len(answer) > 100 else answer,
                        "category": category,
                        "confidence": confidence,
                        "source": source,
                        "processing_time": round(processing_time, 2),
                        "quality_score": quality_score,
                        "status": "success"
                    }
                    
                    print(f"✅ Ответ: {answer[:50]}...")
                    print(f"📊 Категория: {category}, Уверенность: {confidence:.2f}")
                    print(f"⏱️ Время: {processing_time:.2f}с, Качество: {quality_score:.2f}")
                    
                else:
                    result = {
                        "question": question,
                        "answer": f"Ошибка: {response.status_code}",
                        "category": "error",
                        "confidence": 0.0,
                        "source": "error",
                        "processing_time": processing_time,
                        "quality_score": 0.0,
                        "status": "error"
                    }
                    
                    print(f"❌ Ошибка: {response.status_code}")
                
                results.append(result)
                
            except Exception as e:
                result = {
                    "question": question,
                    "answer": f"Исключение: {str(e)}",
                    "category": "error",
                    "confidence": 0.0,
                    "source": "error",
                    "processing_time": 0.0,
                    "quality_score": 0.0,
                    "status": "exception"
                }
                
                print(f"❌ Исключение: {e}")
                results.append(result)
        
        return results
    
    def _analyze_answer_quality(self, question, answer, category):
        """Анализирует качество ответа"""
        score = 0.0
        
        # Базовые проверки
        if answer and len(answer) > 10:
            score += 0.3
        
        if category != "unknown" and category != "error":
            score += 0.3
        
        # Проверяем релевантность по ключевым словам
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        if "наценка" in question_lower and "наценка" in answer_lower:
            score += 0.2
        elif "доставка" in question_lower and "доставка" in answer_lower:
            score += 0.2
        elif "баланс" in question_lower and "баланс" in answer_lower:
            score += 0.2
        elif "приложение" in question_lower and "приложение" in answer_lower:
            score += 0.2
        
        # Проверяем полноту ответа
        if len(answer) > 50:
            score += 0.2
        
        return min(score, 1.0)
    
    def generate_report(self, local_results, railway_results):
        """Генерирует отчет о тестировании"""
        print("\n📊 ОТЧЕТ О ТЕСТИРОВАНИИ LLM МОДЕЛИ")
        print("=" * 80)
        
        # Статистика локального сервера
        local_success = sum(1 for r in local_results if r["status"] == "success")
        local_avg_time = sum(r["processing_time"] for r in local_results) / len(local_results)
        local_avg_quality = sum(r["quality_score"] for r in local_results) / len(local_results)
        local_llm_count = sum(1 for r in local_results if r["source"] == "local_ollama")
        
        print(f"\n🏠 ЛОКАЛЬНЫЙ СЕРВЕР:")
        print(f"   ✅ Успешных ответов: {local_success}/{len(local_results)} ({local_success/len(local_results)*100:.1f}%)")
        print(f"   🧠 LLM ответов: {local_llm_count}/{len(local_results)} ({local_llm_count/len(local_results)*100:.1f}%)")
        print(f"   ⏱️ Среднее время: {local_avg_time:.2f}с")
        print(f"   📊 Среднее качество: {local_avg_quality:.2f}")
        
        # Статистика Railway сервера
        railway_success = sum(1 for r in railway_results if r["status"] == "success")
        railway_avg_time = sum(r["processing_time"] for r in railway_results) / len(railway_results)
        railway_avg_quality = sum(r["quality_score"] for r in railway_results) / len(railway_results)
        railway_llm_count = sum(1 for r in railway_results if r["source"] == "local_llm_server")
        
        print(f"\n🌐 RAILWAY СЕРВЕР:")
        print(f"   ✅ Успешных ответов: {railway_success}/{len(railway_results)} ({railway_success/len(railway_results)*100:.1f}%)")
        print(f"   🧠 LLM ответов: {railway_llm_count}/{len(railway_results)} ({railway_llm_count/len(railway_results)*100:.1f}%)")
        print(f"   ⏱️ Среднее время: {railway_avg_time:.2f}с")
        print(f"   📊 Среднее качество: {railway_avg_quality:.2f}")
        
        # Детальный анализ
        print(f"\n📋 ДЕТАЛЬНЫЙ АНАЛИЗ:")
        print(f"   🏠 Локальный сервер: {'✅ Работает' if local_success > 0 else '❌ Не работает'}")
        print(f"   🌐 Railway сервер: {'✅ Работает' if railway_success > 0 else '❌ Не работает'}")
        print(f"   🧠 LLM модель: {'✅ Активна' if local_llm_count > 0 or railway_llm_count > 0 else '❌ Не активна'}")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        if local_llm_count == 0 and railway_llm_count == 0:
            print("   ⚠️ LLM модель не работает! Проверьте Ollama и локальный сервер")
        elif local_avg_time > 60:
            print("   ⚠️ LLM модель работает медленно (>60с). Рассмотрите оптимизацию")
        elif local_avg_quality < 0.7:
            print("   ⚠️ Качество ответов низкое (<0.7). Улучшите базу знаний")
        else:
            print("   ✅ LLM модель работает хорошо!")
        
        return {
            "local": {
                "success_rate": local_success/len(local_results),
                "llm_rate": local_llm_count/len(local_results),
                "avg_time": local_avg_time,
                "avg_quality": local_avg_quality
            },
            "railway": {
                "success_rate": railway_success/len(railway_results),
                "llm_rate": railway_llm_count/len(railway_results),
                "avg_time": railway_avg_time,
                "avg_quality": railway_avg_quality
            }
        }

def main():
    """Основная функция тестирования"""
    print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТА LLM МОДЕЛИ APARU")
    print("=" * 80)
    
    tester = LLMModelTester()
    
    # Тестируем локальный сервер
    local_results = tester.test_local_server()
    
    # Тестируем Railway сервер
    railway_results = tester.test_railway_server()
    
    # Генерируем отчет
    report = tester.generate_report(local_results, railway_results)
    
    # Сохраняем результаты
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with open(f"llm_test_results_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "local_results": local_results,
            "railway_results": railway_results,
            "report": report
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: llm_test_results_{timestamp}.json")
    print("\n🎯 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🧪 КОМПЛЕКСНЫЙ ТЕСТ ПО ВСЕМ ВОПРОСАМ ИЗ БАЗЫ ЗНАНИЙ
Тестирует все вопросы, вариации, синонимы и морфологические формы
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveQuestionTester:
    def __init__(self):
        self.test_results = {
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'category_results': {},
            'detailed_results': [],
            'performance_metrics': {
                'avg_response_time': 0.0,
                'min_response_time': float('inf'),
                'max_response_time': 0.0
            }
        }
        
        # Загружаем базу знаний
        self.knowledge_base = self._load_knowledge_base()
        
        # Импортируем поисковую систему
        try:
            from enhanced_search_client import get_enhanced_answer
            self.search_function = get_enhanced_answer
            logger.info("✅ Используется enhanced_search_client")
        except ImportError:
            try:
                from morphological_search_client import get_enhanced_answer
                self.search_function = get_enhanced_answer
                logger.info("✅ Используется morphological_search_client")
            except ImportError:
                logger.error("❌ Не удалось импортировать поисковую систему")
                self.search_function = None
    
    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Загружает базу знаний из BZ.txt"""
        try:
            with open('BZ.txt', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            return []
    
    def generate_test_questions(self) -> List[Dict[str, Any]]:
        """Генерирует все возможные тестовые вопросы"""
        test_questions = []
        
        for idx, item in enumerate(self.knowledge_base):
            category = self._extract_category(item)
            
            # Основные вопросы из вариаций
            for variation in item.get('question_variations', []):
                test_questions.append({
                    'question': variation,
                    'category': category,
                    'type': 'original_variation',
                    'expected_answer': item.get('answer', ''),
                    'source': f'BZ.txt item {idx+1}'
                })
            
            # Ключевые слова как вопросы
            for keyword in item.get('keywords', []):
                test_questions.append({
                    'question': f"Что такое {keyword}?",
                    'category': category,
                    'type': 'keyword_question',
                    'expected_answer': item.get('answer', ''),
                    'source': f'BZ.txt item {idx+1} keyword'
                })
            
            # Морфологические варианты
            morph_variations = self._generate_morphological_variations(item)
            for morph_var in morph_variations:
                test_questions.append({
                    'question': morph_var,
                    'category': category,
                    'type': 'morphological',
                    'expected_answer': item.get('answer', ''),
                    'source': f'BZ.txt item {idx+1} morphological'
                })
            
            # Синонимические варианты
            synonym_variations = self._generate_synonym_variations(item)
            for syn_var in synonym_variations:
                test_questions.append({
                    'question': syn_var,
                    'category': category,
                    'type': 'synonym',
                    'expected_answer': item.get('answer', ''),
                    'source': f'BZ.txt item {idx+1} synonym'
                })
        
        return test_questions
    
    def _extract_category(self, item: Dict[str, Any]) -> str:
        """Извлекает категорию из элемента базы знаний"""
        keywords = item.get('keywords', [])
        
        if any(kw in ['наценка', 'коэффициент', 'доплата', 'надбавка'] for kw in keywords):
            return 'НАЦЕНКА'
        elif any(kw in ['доставка', 'курьер', 'посылка'] for kw in keywords):
            return 'ДОСТАВКА'
        elif any(kw in ['баланс', 'счет', 'пополнить'] for kw in keywords):
            return 'БАЛАНС'
        elif any(kw in ['приложение', 'обновление', 'работать'] for kw in keywords):
            return 'ПРИЛОЖЕНИЕ'
        elif any(kw in ['тариф', 'комфорт', 'класс'] for kw in keywords):
            return 'ТАРИФ'
        elif any(kw in ['моточасы', 'время', 'минуты'] for kw in keywords):
            return 'МОТОЧАСЫ'
        else:
            return 'ОБЩИЕ'
    
    def _generate_morphological_variations(self, item: Dict[str, Any]) -> List[str]:
        """Генерирует морфологические варианты вопросов"""
        variations = []
        
        # Базовые морфологические изменения
        morph_changes = {
            'наценка': ['наценки', 'наценку', 'наценкой', 'наценке'],
            'доставка': ['доставки', 'доставку', 'доставкой', 'доставке'],
            'баланс': ['баланса', 'балансу', 'балансом', 'балансе'],
            'приложение': ['приложения', 'приложению', 'приложением', 'приложении'],
            'тариф': ['тарифа', 'тарифу', 'тарифом', 'тарифе'],
            'комфорт': ['комфорта', 'комфорту', 'комфортом', 'комфорте']
        }
        
        for variation in item.get('question_variations', [])[:3]:  # Берем первые 3
            for base_word, morph_forms in morph_changes.items():
                if base_word in variation.lower():
                    for morph_form in morph_forms:
                        new_variation = variation.replace(base_word, morph_form)
                        variations.append(new_variation)
        
        return variations[:10]  # Ограничиваем количество
    
    def _generate_synonym_variations(self, item: Dict[str, Any]) -> List[str]:
        """Генерирует синонимические варианты вопросов"""
        variations = []
        
        # Синонимы для ключевых слов
        synonyms = {
            'наценка': ['дорого', 'подорожание', 'повышение'],
            'доставка': ['курьер', 'посылка', 'отправить'],
            'баланс': ['счет', 'кошелек', 'пополнить'],
            'приложение': ['программа', 'софт', 'работать'],
            'тариф': ['класс', 'стоимость', 'цена'],
            'комфорт': ['удобство', 'премиум', 'высший']
        }
        
        for variation in item.get('question_variations', [])[:2]:  # Берем первые 2
            for base_word, syn_forms in synonyms.items():
                if base_word in variation.lower():
                    for syn_form in syn_forms:
                        new_variation = variation.replace(base_word, syn_form)
                        variations.append(new_variation)
        
        return variations[:8]  # Ограничиваем количество
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Запускает комплексный тест"""
        if not self.search_function:
            logger.error("❌ Поисковая система не доступна")
            return self.test_results
        
        logger.info("🧪 Запуск комплексного теста по всем вопросам...")
        
        # Генерируем все тестовые вопросы
        test_questions = self.generate_test_questions()
        logger.info(f"📝 Сгенерировано {len(test_questions)} тестовых вопросов")
        
        # Запускаем тесты
        for i, test_case in enumerate(test_questions):
            logger.info(f"🔍 Тест {i+1}/{len(test_questions)}: {test_case['question'][:50]}...")
            
            start_time = time.time()
            
            try:
                # Получаем ответ от системы
                answer = self.search_function(test_case['question'])
                response_time = time.time() - start_time
                
                # Определяем успешность
                is_successful = answer != "Нужна уточняющая информация"
                
                # Обновляем метрики
                self.test_results['total_tests'] += 1
                if is_successful:
                    self.test_results['successful_tests'] += 1
                else:
                    self.test_results['failed_tests'] += 1
                
                # Обновляем метрики по категориям
                category = test_case['category']
                if category not in self.test_results['category_results']:
                    self.test_results['category_results'][category] = {
                        'total': 0, 'successful': 0, 'failed': 0
                    }
                
                self.test_results['category_results'][category]['total'] += 1
                if is_successful:
                    self.test_results['category_results'][category]['successful'] += 1
                else:
                    self.test_results['category_results'][category]['failed'] += 1
                
                # Обновляем метрики производительности
                self.test_results['performance_metrics']['avg_response_time'] = (
                    (self.test_results['performance_metrics']['avg_response_time'] * 
                     (self.test_results['total_tests'] - 1) + response_time) / 
                    self.test_results['total_tests']
                )
                
                self.test_results['performance_metrics']['min_response_time'] = min(
                    self.test_results['performance_metrics']['min_response_time'], response_time
                )
                
                self.test_results['performance_metrics']['max_response_time'] = max(
                    self.test_results['performance_metrics']['max_response_time'], response_time
                )
                
                # Сохраняем детальный результат
                self.test_results['detailed_results'].append({
                    'question': test_case['question'],
                    'category': test_case['category'],
                    'type': test_case['type'],
                    'answer': answer[:100] + "..." if len(answer) > 100 else answer,
                    'is_successful': is_successful,
                    'response_time': response_time,
                    'source': test_case['source']
                })
                
            except Exception as e:
                logger.error(f"❌ Ошибка в тесте {i+1}: {e}")
                self.test_results['total_tests'] += 1
                self.test_results['failed_tests'] += 1
        
        # Вычисляем финальные метрики
        self._calculate_final_metrics()
        
        return self.test_results
    
    def _calculate_final_metrics(self):
        """Вычисляет финальные метрики"""
        if self.test_results['total_tests'] > 0:
            self.test_results['success_rate'] = (
                self.test_results['successful_tests'] / self.test_results['total_tests']
            )
        
        # Вычисляем метрики по категориям
        for category, metrics in self.test_results['category_results'].items():
            if metrics['total'] > 0:
                metrics['success_rate'] = metrics['successful'] / metrics['total']
    
    def save_results(self, filename: str = None):
        """Сохраняет результаты теста"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Результаты сохранены в {filename}")
        return filename
    
    def print_summary(self):
        """Выводит сводку результатов"""
        print("\n" + "="*60)
        print("🧪 КОМПЛЕКСНЫЙ ТЕСТ ПО ВСЕМ ВОПРОСАМ - РЕЗУЛЬТАТЫ")
        print("="*60)
        
        print(f"\n📊 ОБЩИЕ МЕТРИКИ:")
        print(f"   Всего тестов: {self.test_results['total_tests']}")
        print(f"   Успешных: {self.test_results['successful_tests']}")
        print(f"   Неудачных: {self.test_results['failed_tests']}")
        print(f"   Успешность: {self.test_results.get('success_rate', 0):.1%}")
        
        print(f"\n⏱️ ПРОИЗВОДИТЕЛЬНОСТЬ:")
        print(f"   Среднее время ответа: {self.test_results['performance_metrics']['avg_response_time']:.3f}s")
        print(f"   Минимальное время: {self.test_results['performance_metrics']['min_response_time']:.3f}s")
        print(f"   Максимальное время: {self.test_results['performance_metrics']['max_response_time']:.3f}s")
        
        print(f"\n📈 РЕЗУЛЬТАТЫ ПО КАТЕГОРИЯМ:")
        for category, metrics in self.test_results['category_results'].items():
            success_rate = metrics.get('success_rate', 0)
            status = "✅" if success_rate >= 0.8 else "⚠️" if success_rate >= 0.6 else "❌"
            print(f"   {status} {category}: {success_rate:.1%} ({metrics['successful']}/{metrics['total']})")
        
        print(f"\n🔍 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        failed_questions = [r for r in self.test_results['detailed_results'] if not r['is_successful']]
        if failed_questions:
            print(f"   Неудачные вопросы ({len(failed_questions)}):")
            for result in failed_questions[:10]:  # Показываем первые 10
                print(f"     ❌ {result['question'][:60]}...")
        else:
            print("   ✅ Все вопросы обработаны успешно!")

def main():
    """Основная функция"""
    print("🧪 КОМПЛЕКСНЫЙ ТЕСТ ПО ВСЕМ ВОПРОСАМ ИЗ БАЗЫ ЗНАНИЙ")
    print("="*60)
    
    # Создаем тестер
    tester = ComprehensiveQuestionTester()
    
    # Запускаем тест
    results = tester.run_comprehensive_test()
    
    # Выводим результаты
    tester.print_summary()
    
    # Сохраняем результаты
    filename = tester.save_results()
    
    print(f"\n💾 Результаты сохранены в: {filename}")
    print("\n🎉 ТЕСТ ЗАВЕРШЕН!")

if __name__ == "__main__":
    main()

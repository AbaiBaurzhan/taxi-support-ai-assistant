#!/usr/bin/env python3
"""
📊 Улучшенный парсер базы знаний APARU
Парсит новую базу BZ.txt с вариациями вопросов и ключевыми словами
"""

import json
import logging
import re
from typing import Dict, List, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedBZParser:
    def __init__(self):
        self.parsed_data = []
        
    def parse_bz_file(self, file_path: str = "BZ.txt") -> List[Dict[str, Any]]:
        """Парсит файл BZ.txt с вариациями вопросов"""
        logger.info(f"📚 Парсим файл: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Разбиваем на блоки по разделителю
            blocks = content.split('\n\t\n')
            
            # Если разделитель не найден, пробуем другой подход
            if len(blocks) == 1:
                # Ищем блоки по паттерну "- question"
                blocks = re.split(r'\n(?=- question)', content)
                if len(blocks) > 1:
                    blocks[0] = blocks[0].replace('- question', '- question')  # Восстанавливаем первый блок
            
            for block in blocks:
                if block.strip():
                    parsed_item = self._parse_block(block.strip())
                    if parsed_item:
                        self.parsed_data.append(parsed_item)
            
            logger.info(f"✅ Парсинг завершен: {len(self.parsed_data)} записей")
            return self.parsed_data
            
        except FileNotFoundError:
            logger.error(f"❌ Файл не найден: {file_path}")
            return []
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга: {e}")
            return []
    
    def _parse_block(self, block: str) -> Dict[str, Any]:
        """Парсит один блок данных"""
        lines = block.split('\n')
        
        # Ищем основной вопрос
        main_question = None
        question_variations = []
        keywords = []
        answer = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('- question_variations:'):
                current_section = 'variations'
                continue
            elif line.startswith('- question:'):
                current_section = 'main_question'
                main_question = line.replace('- question:', '').strip()
                continue
            elif line.startswith('keywords:'):
                current_section = 'keywords'
                # Извлекаем ключевые слова из строки
                keywords_text = line.replace('keywords:', '').strip()
                if keywords_text.startswith('[') and keywords_text.endswith(']'):
                    keywords_text = keywords_text[1:-1]  # Убираем скобки
                    keywords = [kw.strip() for kw in keywords_text.split(',')]
                continue
            elif line.startswith('answer:'):
                current_section = 'answer'
                answer = line.replace('answer:', '').strip()
                continue
            elif line and current_section == 'variations':
                question_variations.append(line)
            elif line and current_section == 'answer':
                answer += " " + line
        
        # Если нет основного вопроса, берем первый из вариаций
        if not main_question and question_variations:
            main_question = question_variations[0]
        
        if main_question and answer:
            return {
                'question': main_question,
                'answer': answer.strip(),
                'variations': question_variations,
                'keywords': keywords,
                'category': self._categorize_question(main_question),
                'confidence': self._calculate_confidence(main_question, answer, keywords),
                'source': 'BZ.txt'
            }
        
        return None
    
    def _categorize_question(self, question: str) -> str:
        """Категоризирует вопрос"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['наценка', 'цена', 'стоимость', 'расценка', 'дорого', 'дешево']):
            return 'pricing'
        elif any(word in question_lower for word in ['заказ', 'поездка', 'такси', 'вызов', 'предварительный']):
            return 'booking'
        elif any(word in question_lower for word in ['баланс', 'пополнить', 'оплата', 'платеж', 'карта']):
            return 'payment'
        elif any(word in question_lower for word in ['приложение', 'таксометр', 'моточасы', 'gps', 'не работает']):
            return 'technical'
        elif any(word in question_lower for word in ['доставка', 'курьер', 'посылка']):
            return 'delivery'
        elif any(word in question_lower for word in ['водитель', 'контакты', 'связь', 'принимать заказы']):
            return 'driver'
        elif any(word in question_lower for word in ['отменить', 'отмена', 'отказ']):
            return 'cancellation'
        elif any(word in question_lower for word in ['жалоба', 'проблема', 'недоволен']):
            return 'complaint'
        else:
            return 'general'
    
    def _calculate_confidence(self, question: str, answer: str, keywords: List[str]) -> float:
        """Рассчитывает уровень уверенности"""
        confidence = 0.5  # Базовый уровень
        
        # Увеличиваем уверенность за структуру ответа
        if 'здравствуйте' in answer.lower():
            confidence += 0.1
        if 'команда апару' in answer.lower():
            confidence += 0.1
        if len(answer) > 100:
            confidence += 0.1
        if len(answer) > 200:
            confidence += 0.1
        
        # Увеличиваем уверенность за наличие вариаций
        if len(keywords) > 5:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def save_to_json(self, output_path: str = "enhanced_aparu_knowledge_base.json"):
        """Сохраняет парсированные данные в JSON"""
        logger.info(f"💾 Сохраняем в JSON: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.parsed_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ JSON сохранен: {len(self.parsed_data)} записей")
        return output_path
    
    def create_search_index(self, output_path: str = "enhanced_search_index.pkl"):
        """Создает индекс для быстрого поиска"""
        import pickle
        
        logger.info(f"🔍 Создаем поисковый индекс: {output_path}")
        
        # Создаем индекс по ключевым словам
        keyword_index = {}
        question_index = {}
        
        for i, item in enumerate(self.parsed_data):
            # Индекс по ключевым словам
            for keyword in item.get('keywords', []):
                if keyword not in keyword_index:
                    keyword_index[keyword] = []
                keyword_index[keyword].append(i)
            
            # Индекс по вопросам
            question_index[item['question'].lower()] = i
            
            # Индекс по вариациям
            for variation in item.get('variations', []):
                question_index[variation.lower()] = i
        
        index_data = {
            'keyword_index': keyword_index,
            'question_index': question_index,
            'data': self.parsed_data
        }
        
        with open(output_path, 'wb') as f:
            pickle.dump(index_data, f)
        
        logger.info(f"✅ Индекс создан: {len(keyword_index)} ключевых слов, {len(question_index)} вопросов")
        return output_path

if __name__ == "__main__":
    parser = EnhancedBZParser()
    
    # Парсим файл
    parsed_data = parser.parse_bz_file("BZ.txt")
    
    if parsed_data:
        # Сохраняем в JSON
        json_path = parser.save_to_json()
        
        # Создаем поисковый индекс
        index_path = parser.create_search_index()
        
        print(f"🎯 Парсинг завершен!")
        print(f"📁 JSON: {json_path}")
        print(f"🔍 Индекс: {index_path}")
        print(f"📊 Записей: {len(parsed_data)}")
        
        # Показываем статистику
        categories = {}
        for item in parsed_data:
            cat = item.get('category', 'general')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n📋 Статистика по категориям:")
        for cat, count in categories.items():
            print(f"   {cat}: {count} записей")
    else:
        print("❌ Ошибка парсинга!")

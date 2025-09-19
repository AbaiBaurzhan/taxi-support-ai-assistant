#!/usr/bin/env python3
"""
📊 Профессиональный парсер базы знаний APARU
Парсит полную базу BZ.txt с вариациями вопросов и ключевыми словами
"""

import json
import logging
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfessionalBZParser:
    def __init__(self):
        self.parsed_data = []
        
    def parse_full_bz_file(self, file_path: str = "BZ.txt") -> List[Dict[str, Any]]:
        """Парсит полный файл BZ.txt"""
        logger.info(f"📚 Парсим полный файл: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Разбиваем на блоки по паттерну "- question_variations:" или "- question:"
            blocks = re.split(r'\n(?=- question)', content)
            
            # Обрабатываем первый блок отдельно
            if blocks and not blocks[0].startswith('- question'):
                blocks[0] = '- question' + blocks[0]
            
            for block in blocks:
                if block.strip() and (block.strip().startswith('- question_variations:') or block.strip().startswith('- question:')):
                    parsed_item = self._parse_question_block(block.strip())
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
    
    def _parse_question_block(self, block: str) -> Dict[str, Any]:
        """Парсит блок с вопросом"""
        lines = block.split('\n')
        
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
                keywords_text = line.replace('keywords:', '').strip()
                if keywords_text.startswith('[') and keywords_text.endswith(']'):
                    keywords_text = keywords_text[1:-1]
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
                'source': 'BZ.txt',
                'id': len(self.parsed_data) + 1
            }
        
        return None
    
    def _categorize_question(self, question: str) -> str:
        """Профессиональная категоризация"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['наценка', 'цена', 'стоимость', 'расценка', 'дорого', 'дешево', 'тариф']):
            return 'pricing'
        elif any(word in question_lower for word in ['заказ', 'поездка', 'такси', 'вызов', 'предварительный', 'отменить']):
            return 'booking'
        elif any(word in question_lower for word in ['баланс', 'пополнить', 'оплата', 'платеж', 'карта', 'qiwi', 'kaspi']):
            return 'payment'
        elif any(word in question_lower for word in ['приложение', 'таксометр', 'моточасы', 'gps', 'не работает', 'обновить']):
            return 'technical'
        elif any(word in question_lower for word in ['доставка', 'курьер', 'посылка', 'отправить']):
            return 'delivery'
        elif any(word in question_lower for word in ['водитель', 'контакты', 'связь', 'принимать заказы', 'работать']):
            return 'driver'
        elif any(word in question_lower for word in ['отменить', 'отмена', 'отказ', 'прекратить']):
            return 'cancellation'
        elif any(word in question_lower for word in ['жалоба', 'проблема', 'недоволен', 'плохо']):
            return 'complaint'
        else:
            return 'general'
    
    def _calculate_confidence(self, question: str, answer: str, keywords: List[str]) -> float:
        """Рассчитывает базовую уверенность"""
        confidence = 0.7  # Базовый уровень для профессиональной системы
        
        # Увеличиваем уверенность за структуру ответа
        if 'здравствуйте' in answer.lower():
            confidence += 0.1
        if 'команда апару' in answer.lower():
            confidence += 0.1
        if len(answer) > 100:
            confidence += 0.05
        if len(answer) > 200:
            confidence += 0.05
        
        # Увеличиваем уверенность за наличие вариаций и ключевых слов
        if len(keywords) > 5:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def save_professional_knowledge_base(self, output_path: str = "professional_aparu_knowledge.json"):
        """Сохраняет профессиональную базу знаний"""
        logger.info(f"💾 Сохраняем профессиональную базу: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.parsed_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Профессиональная база сохранена: {len(self.parsed_data)} записей")
        return output_path

if __name__ == "__main__":
    parser = ProfessionalBZParser()
    
    # Парсим полный файл
    parsed_data = parser.parse_full_bz_file("BZ.txt")
    
    if parsed_data:
        # Сохраняем профессиональную базу
        json_path = parser.save_professional_knowledge_base()
        
        print(f"🎯 Профессиональный парсинг завершен!")
        print(f"📁 JSON: {json_path}")
        print(f"📊 Записей: {len(parsed_data)}")
        
        # Показываем статистику
        categories = {}
        total_variations = 0
        total_keywords = 0
        
        for item in parsed_data:
            cat = item.get('category', 'general')
            categories[cat] = categories.get(cat, 0) + 1
            total_variations += len(item.get('variations', []))
            total_keywords += len(item.get('keywords', []))
        
        print(f"\n📋 Статистика по категориям:")
        for cat, count in categories.items():
            print(f"   {cat}: {count} записей")
        
        print(f"\n📊 Общая статистика:")
        print(f"   Вариаций вопросов: {total_variations}")
        print(f"   Ключевых слов: {total_keywords}")
        print(f"   Среднее вариаций на запись: {total_variations / len(parsed_data):.1f}")
        print(f"   Среднее ключевых слов на запись: {total_keywords / len(parsed_data):.1f}")
    else:
        print("❌ Ошибка парсинга!")

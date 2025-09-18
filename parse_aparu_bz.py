#!/usr/bin/env python3
"""
📊 APARU BZ.txt Parser
Парсит базу знаний из файла BZ.txt и создает структурированные данные
"""

import json
import re
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class APARUBZParser:
    def __init__(self):
        self.knowledge_base = []
        
    def parse_bz_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Парсит файл BZ.txt и извлекает вопросы и ответы"""
        logger.info(f"Парсинг файла: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Разбиваем на блоки вопрос-ответ
            blocks = self._split_into_blocks(content)
            
            for i, block in enumerate(blocks):
                if block.strip():
                    qa_item = self._parse_qa_block(block, i)
                    if qa_item:
                        self.knowledge_base.append(qa_item)
            
            logger.info(f"Извлечено {len(self.knowledge_base)} вопросов-ответов")
            return self.knowledge_base
            
        except Exception as e:
            logger.error(f"Ошибка парсинга файла: {e}")
            raise
    
    def _split_into_blocks(self, content: str) -> List[str]:
        """Разбивает содержимое на блоки вопрос-ответ"""
        # Ищем паттерн "- question:" для разделения блоков
        pattern = r'- question:'
        blocks = re.split(pattern, content)
        
        # Убираем пустые блоки и добавляем обратно "- question:"
        result = []
        for i, block in enumerate(blocks):
            if block.strip():
                if i > 0:  # Не добавляем к первому блоку
                    block = "- question:" + block
                result.append(block)
        
        return result
    
    def _parse_qa_block(self, block: str, index: int) -> Dict[str, Any]:
        """Парсит отдельный блок вопрос-ответ"""
        try:
            lines = block.strip().split('\n')
            
            question = ""
            answer_lines = []
            in_answer = False
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('- question:'):
                    question = line.replace('- question:', '').strip()
                    in_answer = True
                elif in_answer and line.startswith('answer:'):
                    answer_lines.append(line.replace('answer:', '').strip())
                elif in_answer and line and not line.startswith('-'):
                    answer_lines.append(line)
            
            if question and answer_lines:
                answer = ' '.join(answer_lines).strip()
                
                # Очищаем ответ от лишних пробелов
                answer = re.sub(r'\s+', ' ', answer)
                
                # Извлекаем ключевые слова
                keywords = self._extract_keywords(question + " " + answer)
                
                # Определяем категорию
                category = self._determine_category(question, answer)
                
                return {
                    'id': f"aparu_{index}",
                    'question': question,
                    'answer': answer,
                    'category': category,
                    'keywords': keywords,
                    'source': 'BZ.txt',
                    'original_text': block.strip()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка парсинга блока: {e}")
            return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлекает ключевые слова из текста"""
        # Приводим к нижнему регистру
        text = text.lower()
        
        # Убираем знаки препинания
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Разбиваем на слова
        words = text.split()
        
        # Список стоп-слов на русском и казахском
        stop_words = {
            'и', 'в', 'на', 'с', 'по', 'для', 'от', 'до', 'как', 'что', 'где', 'когда', 'почему',
            'это', 'то', 'та', 'те', 'мой', 'моя', 'мое', 'мои', 'ваш', 'ваша', 'ваше', 'ваши',
            'наш', 'наша', 'наше', 'наши', 'его', 'её', 'их', 'он', 'она', 'оно', 'они', 'мы', 'вы',
            'меня', 'тебя', 'его', 'её', 'нас', 'вас', 'их', 'мне', 'тебе', 'ему', 'ей', 'нам', 'вам',
            'им', 'мной', 'тобой', 'им', 'ей', 'нами', 'вами', 'ими', 'здравствуйте', 'спасибо',
            'пожалуйста', 'извините', 'с', 'уважением', 'команда', 'апару'
        }
        
        # Фильтруем слова
        keywords = []
        for word in words:
            if len(word) > 2 and word not in stop_words:
                keywords.append(word)
        
        # Убираем дубликаты и ограничиваем количество
        unique_keywords = list(dict.fromkeys(keywords))[:15]
        
        return unique_keywords
    
    def _determine_category(self, question: str, answer: str) -> str:
        """Определяет категорию вопроса на основе содержимого"""
        text = (question + " " + answer).lower()
        
        # Категории APARU
        categories = {
            'pricing': ['наценка', 'тариф', 'комфорт', 'расценка', 'цена', 'стоимость', 'моточасы', 'таксометр'],
            'booking': ['заказ', 'предварительный', 'доставка', 'регистрировать'],
            'driver': ['водитель', 'принимать', 'заказы', 'баланс', 'пополнить'],
            'technical': ['приложение', 'работает', 'обновить', 'gps', 'настройка'],
            'general': ['что', 'как', 'почему', 'где', 'когда']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return 'general'
    
    def save_to_json(self, output_path: str):
        """Сохраняет базу знаний в JSON файл"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            
            logger.info(f"База знаний сохранена в {output_path}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
            raise
    
    def save_to_csv(self, output_path: str):
        """Сохраняет базу знаний в CSV файл"""
        try:
            import pandas as pd
            
            df = pd.DataFrame(self.knowledge_base)
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            logger.info(f"База знаний сохранена в {output_path}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения CSV: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику базы знаний"""
        if not self.knowledge_base:
            return {}
        
        categories = {}
        total_keywords = 0
        
        for item in self.knowledge_base:
            category = item['category']
            categories[category] = categories.get(category, 0) + 1
            total_keywords += len(item['keywords'])
        
        return {
            'total_questions': len(self.knowledge_base),
            'categories': categories,
            'avg_keywords_per_question': total_keywords / len(self.knowledge_base),
            'total_keywords': total_keywords,
            'source': 'BZ.txt'
        }
    
    def preview_data(self, limit: int = 5):
        """Показывает превью данных"""
        print("📊 Превью базы знаний APARU:")
        print("=" * 60)
        
        for i, item in enumerate(self.knowledge_base[:limit]):
            print(f"\n{i+1}. ID: {item['id']}")
            print(f"   Вопрос: {item['question']}")
            print(f"   Ответ: {item['answer'][:100]}...")
            print(f"   Категория: {item['category']}")
            print(f"   Ключевые слова: {', '.join(item['keywords'][:5])}")
            print("-" * 60)

def main():
    """Основная функция"""
    logging.basicConfig(level=logging.INFO)
    
    # Создаем парсер
    parser = APARUBZParser()
    
    # Парсим файл BZ.txt
    bz_file = "database_Aparu/BZ.txt"
    
    if not Path(bz_file).exists():
        print(f"❌ Файл {bz_file} не найден!")
        return
    
    try:
        # Парсим данные
        knowledge_base = parser.parse_bz_file(bz_file)
        
        # Показываем превью
        parser.preview_data(5)
        
        # Сохраняем в разные форматы
        parser.save_to_json("aparu_knowledge_base.json")
        parser.save_to_csv("aparu_knowledge_base.csv")
        
        # Показываем статистику
        stats = parser.get_statistics()
        print("\n📈 Статистика:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        print(f"\n✅ Обработка завершена!")
        print(f"📁 JSON: aparu_knowledge_base.json")
        print(f"📁 CSV: aparu_knowledge_base.csv")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()

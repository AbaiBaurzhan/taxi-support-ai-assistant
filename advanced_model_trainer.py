#!/usr/bin/env python3
"""
🚀 Продвинутый тренер модели APARU
Улучшает понимание контекста и предотвращает смешивание ответов
"""

import json
import logging
import re
from typing import Dict, List, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedModelTrainer:
    def __init__(self):
        self.knowledge_base = []
        self.context_patterns = {}
        self.answer_templates = {}
        
    def load_knowledge_base(self, file_path: str = "database_Aparu/BZ.txt"):
        """Загружает и парсит базу знаний"""
        logger.info("📚 Загружаем базу знаний...")
        
        parsed_data = []
        current_question = None
        current_answer = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('- question:'):
                        if current_question and current_answer:
                            parsed_data.append(self._process_qa_pair(current_question, "\n".join(current_answer)))
                        current_question = line.replace('- question:', '').strip()
                        current_answer = []
                    elif line.startswith('answer:'):
                        current_answer.append(line.replace('answer:', '').strip())
                    elif line and current_question:
                        current_answer.append(line)
            
            if current_question and current_answer:
                parsed_data.append(self._process_qa_pair(current_question, "\n".join(current_answer)))
            
            self.knowledge_base = parsed_data
            logger.info(f"✅ База знаний загружена: {len(parsed_data)} записей")
            return parsed_data
            
        except FileNotFoundError:
            logger.error(f"❌ Файл не найден: {file_path}")
            return []
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки: {e}")
            return []
    
    def _process_qa_pair(self, question: str, answer: str) -> Dict[str, Any]:
        """Обрабатывает пару вопрос-ответ"""
        return {
            'question': question,
            'answer': answer,
            'context_keywords': self._extract_context_keywords(question, answer),
            'answer_structure': self._analyze_answer_structure(answer),
            'variations': self._generate_contextual_variations(question),
            'category': self._categorize_question(question),
            'confidence_level': self._calculate_confidence_level(question, answer)
        }
    
    def _extract_context_keywords(self, question: str, answer: str) -> List[str]:
        """Извлекает ключевые слова для понимания контекста"""
        text = (question + " " + answer).lower()
        
        # Ключевые слова по категориям
        keywords = []
        
        # Тарифы и цены
        if any(word in text for word in ['тариф', 'цена', 'стоимость', 'расценка', 'наценка']):
            keywords.extend(['тариф', 'цена', 'стоимость', 'расценка', 'наценка'])
        
        # Заказы и поездки
        if any(word in text for word in ['заказ', 'поездка', 'такси', 'вызов']):
            keywords.extend(['заказ', 'поездка', 'такси', 'вызов'])
        
        # Баланс и оплата
        if any(word in text for word in ['баланс', 'пополнить', 'оплата', 'платеж']):
            keywords.extend(['баланс', 'пополнить', 'оплата', 'платеж'])
        
        # Технические вопросы
        if any(word in text for word in ['приложение', 'таксометр', 'моточасы', 'gps']):
            keywords.extend(['приложение', 'таксометр', 'моточасы', 'gps'])
        
        # Доставка
        if any(word in text for word in ['доставка', 'курьер', 'посылка']):
            keywords.extend(['доставка', 'курьер', 'посылка'])
        
        return list(set(keywords))
    
    def _analyze_answer_structure(self, answer: str) -> Dict[str, Any]:
        """Анализирует структуру ответа"""
        return {
            'has_greeting': 'здравствуйте' in answer.lower(),
            'has_signature': 'команда апару' in answer.lower(),
            'has_links': bool(re.search(r'https?://', answer)),
            'has_instructions': any(word in answer.lower() for word in ['нажмите', 'выберите', 'заполните']),
            'length': len(answer),
            'sentences': len(re.split(r'[.!?]+', answer))
        }
    
    def _generate_contextual_variations(self, question: str) -> List[str]:
        """Генерирует контекстные вариации вопроса"""
        variations = [question]
        question_lower = question.lower()
        
        # Синонимы и перефразирования
        synonyms = {
            'что такое': ['объясни', 'расскажи про', 'что означает'],
            'как': ['каким образом', 'как можно', 'как правильно'],
            'почему': ['из-за чего', 'по какой причине', 'отчего'],
            'где': ['в каком месте', 'в какой части', 'где найти'],
            'когда': ['в какое время', 'в какой момент', 'когда можно']
        }
        
        for original, alternatives in synonyms.items():
            if original in question_lower:
                for alt in alternatives:
                    variations.append(question_lower.replace(original, alt))
        
        # Контекстные вариации
        if 'наценка' in question_lower:
            variations.extend(['почему дорого', 'высокая цена', 'зачем доплата'])
        if 'баланс' in question_lower:
            variations.extend(['пополнить счет', 'как положить деньги', 'пополнение'])
        if 'заказ' in question_lower:
            variations.extend(['отменить поездку', 'отмена', 'как заказать'])
        if 'приложение' in question_lower:
            variations.extend(['аппару не работает', 'проблема с приложением', 'ошибка'])
        if 'водитель' in question_lower:
            variations.extend(['где таксист', 'связь с водителем', 'контакты'])
        if 'цена' in question_lower:
            variations.extend(['сколько стоит', 'расценки', 'тарифы'])
        if 'доставка' in question_lower:
            variations.extend(['как отправить посылку', 'заказать курьера', 'курьер'])
        if 'комфорт' in question_lower:
            variations.extend(['тариф комфорт', 'что за комфорт класс', 'комфорт класс'])
        if 'моточасы' in question_lower:
            variations.extend(['почему считают время', 'оплата за время', 'время поездки'])
        if 'такси' in question_lower:
            variations.extend(['как вызвать машину', 'заказать такси', 'вызов такси'])
        if 'эконом' in question_lower:
            variations.extend(['дешевое такси', 'самый дешевый тариф', 'эконом класс'])
        if 'универсал' in question_lower:
            variations.extend(['машина с большим багажником', 'универсал класс'])
        if 'грузовое' in question_lower:
            variations.extend(['грузоперевозки', 'заказать грузовик', 'грузовое такси'])
        if 'эвакуатор' in question_lower:
            variations.extend(['вызвать эвакуатор', 'эвакуатор услуга'])
        if 'списали' in question_lower:
            variations.extend(['двойное списание', 'неправильная сумма', 'ошибка оплаты'])
        if 'справка' in question_lower:
            variations.extend(['получить чек', 'нужен документ', 'документ'])
        if 'наличные' in question_lower:
            variations.extend(['оплата кэшем', 'можно ли платить наличкой', 'наличные деньги'])
        if 'карта' in question_lower:
            variations.extend(['привязать банковскую карту', 'как добавить карту', 'банковская карта'])
        if 'вещи' in question_lower:
            variations.extend(['забыл вещи', 'потерял в такси', 'забытые вещи'])
        if 'отзыв' in question_lower:
            variations.extend(['оставить комментарий', 'оценить поездку', 'оценка'])
        if 'промокод' in question_lower:
            variations.extend(['где взять промокод', 'скидка', 'промо код'])
        if 'мама' in question_lower or 'другому' in question_lower:
            variations.extend(['заказать для другого человека', 'заказ для другого'])
        if 'рейтинг' in question_lower:
            variations.extend(['как формируется рейтинг', 'оценка водителя', 'рейтинг водителя'])
        if 'плохо' in question_lower or 'грубо' in question_lower:
            variations.extend(['жалоба на водителя', 'недоволен водителем', 'плохое обслуживание'])
        
        return list(set(variations))
    
    def _categorize_question(self, question: str) -> str:
        """Категоризирует вопрос"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['тариф', 'цена', 'стоимость', 'расценка', 'наценка']):
            return 'pricing'
        elif any(word in question_lower for word in ['заказ', 'поездка', 'такси', 'вызов']):
            return 'booking'
        elif any(word in question_lower for word in ['баланс', 'пополнить', 'оплата', 'платеж']):
            return 'payment'
        elif any(word in question_lower for word in ['приложение', 'таксометр', 'моточасы', 'gps']):
            return 'technical'
        elif any(word in question_lower for word in ['доставка', 'курьер', 'посылка']):
            return 'delivery'
        elif any(word in question_lower for word in ['водитель', 'контакты', 'связь']):
            return 'driver'
        elif any(word in question_lower for word in ['отменить', 'отмена', 'отказ']):
            return 'cancellation'
        elif any(word in question_lower for word in ['жалоба', 'проблема', 'недоволен']):
            return 'complaint'
        else:
            return 'general'
    
    def _calculate_confidence_level(self, question: str, answer: str) -> float:
        """Рассчитывает уровень уверенности в ответе"""
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
        
        # Увеличиваем уверенность за конкретность
        if any(word in answer.lower() for word in ['тариф', 'цена', 'стоимость']):
            confidence += 0.1
        if any(word in answer.lower() for word in ['приложение', 'нажмите', 'выберите']):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def create_enhanced_modelfile(self, output_path: str = "EnhancedAPARU.modelfile"):
        """Создает улучшенный Modelfile для Ollama"""
        logger.info("🔧 Создаем улучшенный Modelfile...")
        
        modelfile_content = f"""FROM llama2:7b

# Системный промпт для APARU Support
SYSTEM \"\"\"
Ты - AI-ассистент службы поддержки такси APARU. Твоя задача - отвечать на вопросы клиентов точно, вежливо и по делу.

ПРАВИЛА ОТВЕТОВ:
1. Всегда начинай с "Здравствуйте!"
2. Отвечай ТОЛЬКО на основе предоставленной информации
3. НЕ смешивай ответы из разных вопросов
4. НЕ выдумывай информацию
5. Заканчивай подписью "С уважением, команда АПАРУ"
6. Если не знаешь ответа, честно скажи об этом

СТРУКТУРА ОТВЕТА:
- Приветствие
- Основной ответ
- Дополнительная информация (если есть)
- Подпись

КОНТЕКСТНЫЕ КАТЕГОРИИ:
- pricing: тарифы, цены, наценки
- booking: заказы, поездки, вызовы
- payment: баланс, оплата, платежи
- technical: приложение, таксометр, GPS
- delivery: доставка, курьеры
- driver: водители, контакты
- cancellation: отмены, отказы
- complaint: жалобы, проблемы
- general: общие вопросы

БАЗА ЗНАНИЙ:
"""
        
        # Добавляем базу знаний с контекстом
        for i, item in enumerate(self.knowledge_base, 1):
            modelfile_content += f"""
ВОПРОС {i}: {item['question']}
КАТЕГОРИЯ: {item['category']}
КЛЮЧЕВЫЕ СЛОВА: {', '.join(item['context_keywords'])}
ОТВЕТ: {item['answer']}
УВЕРЕННОСТЬ: {item['confidence_level']:.2f}
---
"""
        
        modelfile_content += """

ИНСТРУКЦИИ:
- Анализируй вопрос и определяй категорию
- Ищи ответ по ключевым словам и контексту
- Отвечай ТОЛЬКО на основе найденной информации
- НЕ смешивай ответы из разных записей
- Если вопрос не относится к APARU, вежливо перенаправь к поддержке
\"\"\"

# Параметры модели
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER stop "С уважением, команда АПАРУ"
PARAMETER stop "Здравствуйте!"
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
        
        logger.info(f"✅ Modelfile создан: {output_path}")
        return output_path
    
    def create_context_aware_search(self, output_path: str = "context_aware_search.py"):
        """Создает контекстно-осознанный поиск"""
        logger.info("🔍 Создаем контекстно-осознанный поиск...")
        
        search_code = f'''#!/usr/bin/env python3
"""
🔍 Контекстно-осознанный поиск для APARU
Предотвращает смешивание ответов и улучшает понимание контекста
"""

import json
import logging
from typing import Dict, List, Any, Tuple
from fuzzywuzzy import fuzz
import re

logger = logging.getLogger(__name__)

class ContextAwareSearch:
    def __init__(self, knowledge_base_path: str = "enhanced_aparu_knowledge.json"):
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.context_patterns = self._build_context_patterns()
        
    def _load_knowledge_base(self, path: str) -> List[Dict]:
        """Загружает улучшенную базу знаний"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"База знаний не найдена: {{path}}")
            return []
    
    def _build_context_patterns(self) -> Dict[str, List[str]]:
        """Строит паттерны контекста"""
        return {{
            'pricing': ['тариф', 'цена', 'стоимость', 'расценка', 'наценка', 'дорого', 'дешево'],
            'booking': ['заказ', 'поездка', 'такси', 'вызов', 'вызвать', 'заказать'],
            'payment': ['баланс', 'пополнить', 'оплата', 'платеж', 'карта', 'наличные'],
            'technical': ['приложение', 'таксометр', 'моточасы', 'gps', 'ошибка', 'не работает'],
            'delivery': ['доставка', 'курьер', 'посылка', 'отправить', 'передать'],
            'driver': ['водитель', 'таксист', 'контакты', 'связь', 'номер'],
            'cancellation': ['отменить', 'отмена', 'отказ', 'отменить заказ'],
            'complaint': ['жалоба', 'проблема', 'недоволен', 'плохо', 'грубо'],
            'general': ['что', 'как', 'где', 'когда', 'почему']
        }}
    
    def get_contextual_answer(self, question: str, threshold: float = 0.4) -> Dict[str, Any]:
        """
        Получает контекстный ответ на вопрос
        Предотвращает смешивание ответов из разных категорий
        """
        question_lower = question.lower()
        
        # Определяем категорию вопроса
        question_category = self._categorize_question(question_lower)
        
        # Ищем ответы только в соответствующей категории
        category_items = [item for item in self.knowledge_base if item.get('category') == question_category]
        
        if not category_items:
            # Если категория не найдена, ищем во всех
            category_items = self.knowledge_base
        
        best_match = None
        best_score = 0
        
        for item in category_items:
            # Проверяем основной вопрос
            score = fuzz.ratio(question_lower, item['question'].lower())
            if score > best_score:
                best_score = score
                best_match = item
            
            # Проверяем вариации
            for variation in item.get('variations', []):
                score = fuzz.ratio(question_lower, variation.lower())
                if score > best_score:
                    best_score = score
                    best_match = item
            
            # Проверяем ключевые слова
            for keyword in item.get('context_keywords', []):
                if keyword.lower() in question_lower:
                    score = fuzz.ratio(question_lower, keyword.lower()) + 20
                    if score > best_score:
                        best_score = score
                        best_match = item
        
        # Нормализуем score
        normalized_score = best_score / 100.0
        
        if normalized_score >= threshold and best_match:
            return {{
                'answer': best_match['answer'],
                'confidence': normalized_score,
                'source': 'knowledge_base',
                'category': question_category,
                'context_keywords': best_match.get('context_keywords', []),
                'prevented_mixing': True
            }}
        else:
            return {{
                'answer': "Извините, я не нашел подходящего ответа в базе знаний. Обратитесь к оператору поддержки.",
                'confidence': 0.0,
                'source': 'fallback',
                'category': question_category,
                'context_keywords': [],
                'prevented_mixing': True
            }}
    
    def _categorize_question(self, question: str) -> str:
        """Категоризирует вопрос по контексту"""
        for category, keywords in self.context_patterns.items():
            if any(keyword in question for keyword in keywords):
                return category
        return 'general'
    
    def validate_answer_consistency(self, question: str, answer: str) -> bool:
        """Проверяет консистентность ответа"""
        question_category = self._categorize_question(question.lower())
        
        # Проверяем, что ответ соответствует категории вопроса
        if question_category == 'pricing' and not any(word in answer.lower() for word in ['тариф', 'цена', 'стоимость']):
            return False
        elif question_category == 'booking' and not any(word in answer.lower() for word in ['заказ', 'поездка', 'такси']):
            return False
        elif question_category == 'payment' and not any(word in answer.lower() for word in ['баланс', 'оплата', 'платеж']):
            return False
        
        return True

# Глобальный экземпляр для использования в main.py
_context_aware_search = ContextAwareSearch()

def get_contextual_answer(question: str) -> str:
    """Получает контекстный ответ"""
    result = _context_aware_search.get_contextual_answer(question)
    return result['answer']
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(search_code)
        
        logger.info(f"✅ Контекстно-осознанный поиск создан: {output_path}")
        return output_path
    
    def save_enhanced_knowledge_base(self, output_path: str = "enhanced_aparu_knowledge.json"):
        """Сохраняет улучшенную базу знаний"""
        logger.info("💾 Сохраняем улучшенную базу знаний...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Улучшенная база знаний сохранена: {output_path}")
        return output_path
    
    def train_advanced_model(self):
        """Запускает полное обучение модели"""
        logger.info("🚀 Запускаем продвинутое обучение модели...")
        
        # 1. Загружаем базу знаний
        self.load_knowledge_base()
        
        # 2. Создаем улучшенный Modelfile
        modelfile_path = self.create_enhanced_modelfile()
        
        # 3. Создаем контекстно-осознанный поиск
        search_path = self.create_context_aware_search()
        
        # 4. Сохраняем улучшенную базу знаний
        kb_path = self.save_enhanced_knowledge_base()
        
        logger.info("✅ Продвинутое обучение завершено!")
        logger.info(f"📁 Созданные файлы:")
        logger.info(f"   - {modelfile_path}")
        logger.info(f"   - {search_path}")
        logger.info(f"   - {kb_path}")
        
        return {
            'modelfile': modelfile_path,
            'search': search_path,
            'knowledge_base': kb_path
        }

if __name__ == "__main__":
    trainer = AdvancedModelTrainer()
    results = trainer.train_advanced_model()
    print("🎯 Продвинутое обучение завершено!")
    print(f"📁 Результаты: {results}")

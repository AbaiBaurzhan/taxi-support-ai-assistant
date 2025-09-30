"""
Улучшенный морфологический анализатор для русского и казахского языков
Специально адаптирован для базы знаний BZ.txt
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

class EnhancedMorphologicalAnalyzer:
    """Улучшенный морфологический анализатор для BZ.txt"""
    
    def __init__(self):
        self.rules = self._load_morphological_rules()
        self.stop_words = self._load_stop_words()
        self.synonyms = self._load_synonyms()
        self.patterns = self._load_patterns()
        
    def _load_morphological_rules(self) -> Dict[str, Dict[str, List[str]]]:
        """Загружает морфологические правила для русского и казахского"""
        return {
            'ru': {
                'endings': {
                    'ия': ['ии', 'ию', 'ие', 'ий'],
                    'ция': ['ции', 'цию', 'ций'],
                    'ация': ['ации', 'ацию', 'аций'],
                    'ость': ['ости', 'остью'],
                    'ение': ['ения', 'ению', 'ением'],
                    'ание': ['ания', 'анию', 'анием'],
                    'ение': ['ения', 'ению', 'ением'],
                    'ость': ['ости', 'остью'],
                    'ка': ['ки', 'ку', 'кой', 'ке'],
                    'ик': ['ика', 'ику', 'иком', 'ике'],
                    'ник': ['ника', 'нику', 'ником', 'нике'],
                    'тель': ['теля', 'телю', 'телем', 'теле'],
                    'ость': ['ости', 'остью'],
                    'ство': ['ства', 'ству', 'ством', 'стве'],
                    'ение': ['ения', 'ению', 'ением'],
                    'ание': ['ания', 'анию', 'анием'],
                    'имость': ['имости', 'имостью'],
                    'ность': ['ности', 'ностью'],
                    'ель': ['еля', 'елю', 'елем', 'еле'],
                    'арь': ['аря', 'арю', 'арем', 'аре'],
                    'ер': ['ера', 'еру', 'ером', 'ере'],
                    'ор': ['ора', 'ору', 'ором', 'оре'],
                    'ец': ['ца', 'цу', 'цом', 'це'],
                    'ик': ['ика', 'ику', 'иком', 'ике'],
                    'ок': ['ка', 'ку', 'ком', 'ке'],
                    'ек': ['ка', 'ку', 'ком', 'ке'],
                    'ица': ['ицы', 'ице', 'ицей'],
                    'ица': ['ицы', 'ице', 'ицей'],
                    'а': ['ы', 'е', 'ой', 'у'],
                    'я': ['и', 'е', 'ей', 'ю'],
                    'ь': ['и', 'е', 'ью', 'ю'],
                    'й': ['я', 'ю', 'ем', 'е'],
                    'о': ['а', 'у', 'ом', 'е'],
                    'е': ['я', 'ю', 'ем', 'е'],
                    'ы': ['', 'е', 'ой', 'у'],
                    'и': ['ей', 'ям', 'ями', 'ях'],
                    'у': ['а', 'у', 'ом', 'е'],
                    'а': ['ы', 'е', 'ой', 'у']
                },
                'suffixes': {
                    'тель': ['тель', 'теля', 'телю', 'телем'],
                    'ник': ['ник', 'ника', 'нику', 'ником'],
                    'ик': ['ик', 'ика', 'ику', 'иком'],
                    'ок': ['ок', 'ка', 'ку', 'ком'],
                    'ек': ['ек', 'ка', 'ку', 'ком'],
                    'ица': ['ица', 'ицы', 'ице', 'ицей'],
                    'ость': ['ость', 'ости', 'остью'],
                    'ность': ['ность', 'ности', 'ностью'],
                    'имость': ['имость', 'имости', 'имостью'],
                    'ство': ['ство', 'ства', 'ству', 'ством'],
                    'ение': ['ение', 'ения', 'ению', 'ением'],
                    'ание': ['ание', 'ания', 'анию', 'анием']
                }
            },
            'kz': {
                'endings': {
                    'лар': ['лары', 'ларын', 'ларына', 'ларында'],
                    'лер': ['лері', 'лерін', 'леріне', 'лерінде'],
                    'дар': ['дары', 'дарын', 'дарына', 'дарында'],
                    'дер': ['дері', 'дерін', 'деріне', 'дерінде'],
                    'тар': ['тары', 'тарын', 'тарына', 'тарында'],
                    'тер': ['тері', 'терін', 'теріне', 'терінде'],
                    'а': ['аны', 'аға', 'ада', 'адан'],
                    'е': ['есі', 'еге', 'еде', 'еден'],
                    'ы': ['ыны', 'ыға', 'ыда', 'ыдан'],
                    'і': ['іні', 'іге', 'іде', 'іден'],
                    'о': ['оны', 'оға', 'ода', 'одан'],
                    'ө': ['өні', 'өге', 'өде', 'өден'],
                    'ұ': ['ұны', 'ұға', 'ұда', 'ұдан'],
                    'ү': ['үні', 'үге', 'үде', 'үден']
                }
            }
        }
    
    def _load_stop_words(self) -> Dict[str, set]:
        """Загружает стоп-слова для фильтрации"""
        return {
            'ru': {
                'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между'
            },
            'kz': {
                'және', 'мен', 'бен', 'пен', 'үшін', 'туралы', 'қарағанда', 'сияқты', 'деп', 'дейін', 'дейінгі', 'дейінде', 'дейіннен', 'дейінгінің', 'дейінгіге', 'дейінгіде', 'дейінгіден', 'дейінгімен', 'дейінгісін', 'дейінгісіне', 'дейінгісінде', 'дейінгісінен', 'дейінгісімен', 'дейінгісі', 'дейінгісін', 'дейінгісіне', 'дейінгісінде', 'дейінгісінен', 'дейінгісімен', 'дейінгісі', 'дейінгісін', 'дейінгісіне', 'дейінгісінде', 'дейінгісінен', 'дейінгісімен'
            }
        }
    
    def _load_synonyms(self) -> Dict[str, Dict[str, List[str]]]:
        """Загружает синонимы для улучшения поиска"""
        return {
            'ru': {
                'наценка': ['коэффициент', 'доплата', 'надбавка', 'повышение', 'подорожание'],
                'тариф': ['ставка', 'цена', 'стоимость', 'расценка'],
                'комфорт': ['удобство', 'премиум', 'люкс'],
                'доставка': ['перевозка', 'транспортировка', 'курьер'],
                'водитель': ['шофер', 'таксист', 'перевозчик'],
                'баланс': ['счет', 'средства', 'деньги'],
                'моточасы': ['время', 'минуты', 'длительность'],
                'таксометр': ['счетчик', 'измеритель'],
                'приложение': ['программа', 'софт', 'апп']
            },
            'kz': {
                'наценка': ['коэффициент', 'доплата', 'надбавка'],
                'тариф': ['баға', 'құн', 'ақы'],
                'комфорт': ['ыңғайлылық', 'премиум'],
                'доставка': ['жеткізу', 'тасымалдау'],
                'водитель': ['жүргізуші', 'таксист'],
                'баланс': ['теңгерім', 'ақша', 'қаражат'],
                'моточасы': ['уақыт', 'минут'],
                'таксометр': ['есептегіш'],
                'приложение': ['қосымша', 'бағдарлама']
            }
        }
    
    def _load_patterns(self) -> Dict[str, List[str]]:
        """Загружает паттерны для улучшенного распознавания"""
        return {
            'question_patterns': [
                r'как\s+(.+?)\?',
                r'что\s+(.+?)\?',
                r'где\s+(.+?)\?',
                r'почему\s+(.+?)\?',
                r'зачем\s+(.+?)\?',
                r'когда\s+(.+?)\?',
                r'сколько\s+(.+?)\?',
                r'можно\s+ли\s+(.+?)\?',
                r'есть\s+ли\s+(.+?)\?',
                r'что\s+такое\s+(.+?)\?',
                r'что\s+означает\s+(.+?)\?',
                r'что\s+значит\s+(.+?)\?',
                r'каким\s+образом\s+(.+?)\?',
                r'каким\s+способом\s+(.+?)\?',
                r'в\s+чем\s+разница\s+(.+?)\?',
                r'чем\s+отличается\s+(.+?)\?',
                r'какие\s+(.+?)\?',
                r'какой\s+(.+?)\?',
                r'какая\s+(.+?)\?',
                r'какое\s+(.+?)\?'
            ],
            'intent_patterns': {
                'наценка': [r'наценк', r'коэффициент', r'доплат', r'надбавк', r'подорожан', r'повышени'],
                'тариф': [r'тариф', r'комфорт', r'класс', r'машин', r'премиум'],
                'расценка': [r'расценк', r'стоимост', r'цен', r'таксометр', r'калькулятор'],
                'предзаказ': [r'предварительн', r'заране', r'предзаказ', r'зарезервир'],
                'доставка': [r'доставк', r'курьер', r'посылк', r'перевозк'],
                'водитель': [r'водител', r'регистрац', r'заказ', r'баланс'],
                'баланс': [r'баланс', r'пополнен', r'qiwi', r'kaspi', r'карт'],
                'моточасы': [r'моточас', r'минут', r'времен', r'длительн'],
                'таксометр': [r'таксометр', r'ожидани', r'поехал', r'останов'],
                'приложение': [r'приложени', r'не\s+работает', r'обновлен', r'gps']
            }
        }
    
    def normalize_text(self, text: str, language: str = 'ru') -> str:
        """Нормализует текст для анализа"""
        if not text:
            return ""
        
        # Приводим к нижнему регистру
        text = text.lower().strip()
        
        # Убираем пунктуацию, оставляем только буквы и пробелы
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Убираем стоп-слова
        words = text.split()
        filtered_words = [word for word in words if word not in self.stop_words.get(language, set())]
        
        return ' '.join(filtered_words)
    
    def get_word_stem(self, word: str, language: str = 'ru') -> str:
        """Получает основу слова"""
        if not word:
            return ""
        
        word = word.lower().strip()
        
        # Проверяем правила для данного языка
        if language not in self.rules:
            return word
        
        rules = self.rules[language]
        
        # Проверяем окончания
        for ending, variations in rules.get('endings', {}).items():
            if word.endswith(ending):
                # Убираем окончание
                stem = word[:-len(ending)]
                return stem
        
        # Проверяем суффиксы
        for suffix, variations in rules.get('suffixes', {}).items():
            if word.endswith(suffix):
                # Убираем суффикс
                stem = word[:-len(suffix)]
                return stem
        
        return word
    
    def expand_query(self, query: str, language: str = 'ru') -> List[str]:
        """Расширяет запрос с помощью синонимов и морфологии"""
        if not query:
            return []
        
        expanded = set()
        
        # Нормализуем исходный запрос
        normalized = self.normalize_text(query, language)
        expanded.add(normalized)
        
        # Добавляем слова с разными окончаниями
        words = normalized.split()
        for word in words:
            stem = self.get_word_stem(word, language)
            
            # Добавляем основу
            expanded.add(stem)
            
            # Добавляем варианты с разными окончаниями
            if language in self.rules:
                for ending in self.rules[language].get('endings', {}).keys():
                    if not word.endswith(ending):
                        expanded.add(stem + ending)
            
            # Добавляем синонимы
            if language in self.synonyms:
                for base_word, synonyms in self.synonyms[language].items():
                    if stem == base_word or word == base_word:
                        for synonym in synonyms:
                            expanded.add(synonym)
                            expanded.add(self.get_word_stem(synonym, language))
        
        return list(expanded)
    
    def extract_keywords(self, text: str, language: str = 'ru') -> List[str]:
        """Извлекает ключевые слова из текста"""
        if not text:
            return []
        
        normalized = self.normalize_text(text, language)
        words = normalized.split()
        
        keywords = []
        for word in words:
            stem = self.get_word_stem(word, language)
            keywords.append(stem)
            keywords.append(word)
        
        return list(set(keywords))
    
    def match_keywords(self, query_keywords: List[str], text_keywords: List[str]) -> float:
        """Вычисляет степень совпадения ключевых слов"""
        if not query_keywords or not text_keywords:
            return 0.0
        
        query_set = set(query_keywords)
        text_set = set(text_keywords)
        
        # Вычисляем пересечение
        intersection = query_set.intersection(text_set)
        
        # Возвращаем долю совпадений
        return len(intersection) / max(len(query_set), len(text_set))
    
    def detect_language(self, text: str) -> str:
        """Определяет язык текста"""
        if not text:
            return 'ru'
        
        # Простая эвристика по алфавиту
        kz_chars = set('әғқңөұүіһ')
        text_chars = set(text.lower())
        
        if kz_chars.intersection(text_chars):
            return 'kz'
        
        return 'ru'
    
    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """Анализирует намерение запроса"""
        if not query:
            return {'intent': 'unknown', 'confidence': 0.0, 'language': 'ru'}
        
        language = self.detect_language(query)
        normalized_query = self.normalize_text(query, language)
        
        # Проверяем паттерны намерений
        intent_scores = {}
        
        for intent, patterns in self.patterns['intent_patterns'].items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, normalized_query, re.IGNORECASE):
                    score += 1.0
            
            if score > 0:
                intent_scores[intent] = score / len(patterns)
        
        # Определяем лучшее намерение
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return {
                'intent': best_intent[0],
                'confidence': best_intent[1],
                'language': language,
                'all_scores': intent_scores
            }
        
        return {'intent': 'unknown', 'confidence': 0.0, 'language': language}

# Глобальный экземпляр анализатора
enhanced_analyzer = EnhancedMorphologicalAnalyzer()

def enhance_classification_with_morphology(query: str, kb_data: Dict[str, Any]) -> Dict[str, Any]:
    """Улучшенная классификация с морфологическим анализом"""
    if not query or not kb_data:
        return {'intent': 'unknown', 'confidence': 0.0, 'language': 'ru'}
    
    try:
        # Анализируем запрос
        analysis = enhanced_analyzer.analyze_intent(query)
        language = analysis['language']
        
        # Получаем FAQ элементы
        faq_items = kb_data.get('faq', [])
        if not faq_items:
            return analysis
        
        best_match = None
        best_score = 0.0
        
        # Извлекаем ключевые слова из запроса
        query_keywords = enhanced_analyzer.extract_keywords(query, language)
        
        # Ищем лучшее совпадение
        for item in faq_items:
            score = 0.0
            
            # Проверяем ключевые слова
            keywords = item.get('keywords', [])
            if keywords:
                keyword_score = enhanced_analyzer.match_keywords(query_keywords, keywords)
                score += keyword_score * 0.4
            
            # Проверяем вариации вопросов
            variations = item.get('question_variations', [])
            if variations:
                max_variation_score = 0.0
                for variation in variations:
                    variation_keywords = enhanced_analyzer.extract_keywords(variation, language)
                    variation_score = enhanced_analyzer.match_keywords(query_keywords, variation_keywords)
                    max_variation_score = max(max_variation_score, variation_score)
                score += max_variation_score * 0.4
            
            # Проверяем основной вопрос
            main_question = item.get('question', '')
            if main_question:
                main_keywords = enhanced_analyzer.extract_keywords(main_question, language)
                main_score = enhanced_analyzer.match_keywords(query_keywords, main_keywords)
                score += main_score * 0.2
            
            # Обновляем лучшее совпадение
            if score > best_score:
                best_score = score
                best_match = item
        
        # Возвращаем результат
        if best_match and best_score > 0.3:  # Порог для определения совпадения
            return {
                'intent': 'faq',
                'confidence': min(best_score, 1.0),
                'language': language,
                'matched_item': best_match,
                'match_score': best_score
            }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Ошибка в морфологическом анализе: {e}")
        return {'intent': 'unknown', 'confidence': 0.0, 'language': 'ru'}

__all__ = ['EnhancedMorphologicalAnalyzer', 'enhanced_analyzer', 'enhance_classification_with_morphology']

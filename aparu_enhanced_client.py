#!/usr/bin/env python3
"""
🔧 APARU Enhanced Integration
Интегрирует обученную модель APARU с основным приложением
"""

import json
import logging
import requests
import os
import pickle
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class APARUEnhancedClient:
    def __init__(self, model_name: str = "aparu-support", use_ollama: bool = True):
        self.use_ollama = use_ollama
        self.model_name = model_name
        self.knowledge_base = None
        
        if use_ollama:
            # Проверяем переменные окружения для внешнего LLM
            self.llm_url = os.getenv("LLM_URL", "http://localhost:11434")
            self.ollama_url = f"{self.llm_url}/api/generate"
            self.llm_enabled = os.getenv("LLM_ENABLED", "true").lower() == "true"
            
            # Проверяем доступность LLM
            if self.llm_enabled:
                try:
                    response = requests.get(f"{self.llm_url}/api/tags", timeout=5)
                    if response.status_code != 200:
                        logger.warning("LLM недоступен, используем fallback")
                        self.use_ollama = False
                except:
                    logger.warning("LLM недоступен, используем fallback")
                    self.use_ollama = False
            
            if not self.llm_enabled:
                logger.warning("LLM отключен через переменную окружения")
                self.use_ollama = False
        else:
            logger.warning("Heavy ML libraries not available, using fallback responses")
    
    def load_aparu_knowledge_base(self, index_path: str = "aparu_knowledge_index.pkl"):
        """Загружает обученную базу знаний APARU"""
        try:
            if not Path(index_path).exists():
                logger.warning(f"Файл {index_path} не найден, используем fallback")
                return False
            
            # Загружаем индекс
            with open(index_path, 'rb') as f:
                data = pickle.load(f)
            
            self.knowledge_base = data['knowledge_base']
            logger.info(f"✅ База знаний APARU загружена: {len(self.knowledge_base)} записей")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки базы знаний APARU: {e}")
            return False
    
    def generate_response(self, prompt: str, max_length: int = 200) -> str:
        """Генерирует ответ от обученной модели APARU"""
        try:
            if self.use_ollama:
                return self._generate_with_aparu_model(prompt, max_length)
            else:
                return self._generate_fallback(prompt)
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return "Извините, произошла ошибка при генерации ответа."
    
    def _generate_with_aparu_model(self, prompt: str, max_length: int) -> str:
        """Генерация с использованием обученной модели APARU"""
        try:
            # Если есть база знаний, ищем релевантную информацию
            if self.knowledge_base:
                # Извлекаем вопрос из промпта
                user_question = self._extract_question_from_prompt(prompt)
                
                # Ищем похожие записи в базе знаний APARU
                similar_items = self._search_aparu_knowledge(user_question)
                
                if similar_items:
                    # Используем информацию из базы знаний APARU
                    context = self._build_aparu_context(similar_items)
                    enhanced_prompt = self._enhance_prompt_with_aparu_context(prompt, context)
                else:
                    enhanced_prompt = prompt
            else:
                enhanced_prompt = prompt
            
            # Отправляем запрос к обученной модели APARU
            payload = {
                "model": self.model_name,
                "prompt": enhanced_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": max_length
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "Не удалось получить ответ от модели.")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Ollama: {e}")
            return self._generate_fallback(prompt)
    
    def _extract_question_from_prompt(self, prompt: str) -> str:
        """Извлекает вопрос пользователя из промпта"""
        # Ищем строку "Запрос пользователя:"
        if "Запрос пользователя:" in prompt:
            return prompt.split("Запрос пользователя:")[-1].strip()
        return prompt
    
    def _search_aparu_knowledge(self, question: str, top_k: int = 3) -> List[Dict]:
        """Умный поиск в базе знаний APARU с пониманием контекста"""
        if not self.knowledge_base:
            return []
        
        # Используем умную систему поиска
        try:
            from smart_context_search import SmartContextSearch
            
            # Создаем систему поиска (если еще не создана)
            if not hasattr(self, 'smart_search'):
                self.smart_search = SmartContextSearch()
                self.smart_search.load_knowledge_base()
            
            # Ищем похожие записи
            results = self.smart_search.search(question, top_k=top_k)
            
            # Преобразуем в нужный формат
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'question': result['question'],
                    'answer': result['answer'],
                    'similarity_score': result['similarity_score'],
                    'category': result.get('category', 'general'),
                    'contexts': result.get('contexts', [])
                })
            
            return formatted_results
            
        except ImportError:
            # Fallback к простому поиску
            return self._simple_search(question, top_k)
    
    def _simple_search(self, question: str, top_k: int = 3) -> List[Dict]:
        """Простой поиск по ключевым словам (fallback)"""
        question_lower = question.lower()
        results = []
        
        for item in self.knowledge_base:
            # Простой поиск по ключевым словам
            score = 0
            
            # Проверяем совпадения в вопросе
            for keyword in item.get('keywords', []):
                if keyword.lower() in question_lower:
                    score += 1
            
            # Проверяем совпадения в тексте вопроса
            if item['question'].lower() in question_lower:
                score += 2
            
            if score > 0:
                results.append({
                    **item,
                    'similarity_score': score / 10.0  # Нормализуем
                })
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]
    
    def _build_aparu_context(self, similar_items: List[Dict]) -> str:
        """Строит контекст из найденных записей базы знаний APARU"""
        context_parts = []
        
        for item in similar_items:
            context_parts.append(f"Вопрос: {item['question']}")
            context_parts.append(f"Ответ: {item['answer']}")
            if item.get('keywords'):
                context_parts.append(f"Ключевые слова: {', '.join(item['keywords'][:5])}")
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def _enhance_prompt_with_aparu_context(self, original_prompt: str, context: str) -> str:
        """Улучшает промпт с контекстом из базы знаний APARU"""
        enhanced_prompt = f"""Ты - ИИ-ассистент службы поддержки такси-сервиса APARU.

Используй следующую информацию из базы знаний APARU для ответа:

{context}

Правила ответа:
- Всегда начинай с "Здравствуйте"
- Отвечай вежливо и профессионально
- Заканчивай "С уважением, команда АПАРУ"
- Отвечай кратко и по делу
- Используй информацию из базы знаний APARU выше
- Если не знаешь ответа, предложи связаться с оператором
- Отвечай только на русском языке

{original_prompt}

Ответ:"""
        
        return enhanced_prompt
    
    def _generate_fallback(self, prompt: str) -> str:
        """Простой fallback с использованием базы знаний APARU"""
        prompt_lower = prompt.lower()
        
        # Если есть база знаний APARU, используем её для fallback
        if self.knowledge_base:
            user_question = self._extract_question_from_prompt(prompt)
            similar_items = self._search_aparu_knowledge(user_question, top_k=1)
            
            if similar_items and similar_items[0]['similarity_score'] > 0.3:
                return similar_items[0]['answer']
        
        # Стандартные fallback ответы в стиле APARU
        if "наценка" in prompt_lower:
            return "Здравствуйте. Наценка является частью тарифной системы Компании и ее наличие регулируется объем спроса, на рассматриваемый момент. С уважением, команда АПАРУ."
        elif "тариф" in prompt_lower or "цена" in prompt_lower:
            return "Здравствуйте. В виду множества преимуществ, в приложении APARU выбрана только одна форма ценообразования - таксометр. С уважением, команда АПАРУ."
        elif "баланс" in prompt_lower:
            return "Здравствуйте. Пополнить баланс можно через платежную систему QIWI, Cyberplat или Касса24, через электронные кошельки QIWI и Kaspi. С уважением, команда АПАРУ."
        elif "водитель" in prompt_lower:
            return "Здравствуйте. Установите приложение APARU бесплатно в Google Play/App store. Для регистрации достаточно ввести свой номер телефона и проверочный код. С уважением, команда АПАРУ."
        else:
            return "Здравствуйте. Спасибо за обращение! Если у вас есть конкретный вопрос, я помогу найти ответ. С уважением, команда АПАРУ."
    
    def create_aparu_context_prompt(self, user_message: str, intent: str, locale: str) -> str:
        """Создает контекстный промпт для такси-сервиса APARU с базой знаний"""
        
        # Если есть база знаний APARU, ищем релевантную информацию
        context_info = ""
        if self.knowledge_base:
            similar_items = self._search_aparu_knowledge(user_message, top_k=2)
            if similar_items and similar_items[0]['similarity_score'] > 0.2:
                context_info = f"\n\nРелевантная информация из базы знаний APARU:\n"
                for item in similar_items:
                    context_info += f"Вопрос: {item['question']}\n"
                    context_info += f"Ответ: {item['answer']}\n\n"
        
        system_prompt = f"""Ты - ИИ-ассистент службы поддержки такси-сервиса APARU. 
Отвечай на языке: {locale}
Тип запроса: {intent}
{context_info}
Правила ответа:
- Всегда начинай с "Здравствуйте"
- Отвечай вежливо и профессионально
- Заканчивай "С уважением, команда АПАРУ"
- Отвечай кратко и по делу
- Используй информацию из базы знаний APARU выше
- Если не знаешь ответа, предложи связаться с оператором
- Для жалоб всегда предлагай эскалацию к человеку
- Используй только русский, казахский или английский язык в зависимости от locale

Запрос пользователя: {user_message}

Ответ:"""

        return system_prompt
    
    def get_aparu_stats(self) -> Dict:
        """Возвращает статистику базы знаний APARU"""
        if self.knowledge_base:
            categories = {}
            for item in self.knowledge_base:
                category = item.get('category', 'general')
                categories[category] = categories.get(category, 0) + 1
            
            return {
                'total_questions': len(self.knowledge_base),
                'categories': categories,
                'source': 'APARU BZ.txt'
            }
        return {"error": "База знаний APARU не загружена"}

# Глобальный экземпляр клиента
aparu_enhanced_client = APARUEnhancedClient()

def main():
    """Тестирование APARU enhanced client"""
    logging.basicConfig(level=logging.INFO)
    
    # Загружаем базу знаний APARU
    if aparu_enhanced_client.load_aparu_knowledge_base():
        print("✅ База знаний APARU загружена")
        
        # Тестируем поиск
        test_questions = [
            "Что такое наценка?",
            "Как узнать расценку?",
            "Как пополнить баланс?",
            "Что такое моточасы?",
            "Как работает таксометр?"
        ]
        
        for question in test_questions:
            print(f"\n📝 Тест: {question}")
            
            # Создаем промпт
            prompt = aparu_enhanced_client.create_aparu_context_prompt(question, "faq", "RU")
            
            # Генерируем ответ
            response = aparu_enhanced_client.generate_response(prompt)
            print(f"✅ Ответ: {response[:150]}...")
            
            # Показываем статистику
            stats = aparu_enhanced_client.get_aparu_stats()
            print(f"📊 Статистика: {stats}")
    else:
        print("❌ Не удалось загрузить базу знаний APARU")

if __name__ == "__main__":
    main()

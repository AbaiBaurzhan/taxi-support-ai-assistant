#!/usr/bin/env python3
"""
🌐 Гибридная архитектура: Локальная модель + Railway API
Модель работает локально, Railway только пересылает запросы
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridAIClient:
    def __init__(self, local_model_url: str = "http://localhost:11434", railway_api_url: str = None):
        self.local_model_url = local_model_url
        self.railway_api_url = railway_api_url
        self.local_model_available = False
        self.railway_api_available = False
        
        # Проверяем доступность локальной модели
        self._check_local_model()
        
        # Проверяем доступность Railway API
        if railway_api_url:
            self._check_railway_api()
    
    def _check_local_model(self):
        """Проверяет доступность локальной модели Ollama"""
        try:
            response = requests.get(f"{self.local_model_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.local_model_available = True
                logger.info("✅ Локальная модель Ollama доступна")
            else:
                logger.warning("⚠️ Локальная модель Ollama недоступна")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к локальной модели: {e}")
    
    def _check_railway_api(self):
        """Проверяет доступность Railway API"""
        try:
            response = requests.get(f"{self.railway_api_url}/health", timeout=5)
            if response.status_code == 200:
                self.railway_api_available = True
                logger.info("✅ Railway API доступен")
            else:
                logger.warning("⚠️ Railway API недоступен")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к Railway API: {e}")
    
    def _query_local_model(self, question: str) -> Optional[str]:
        """Запрашивает ответ у локальной модели"""
        try:
            payload = {
                "model": "aparu-senior-ai",
                "prompt": f"Ответь на вопрос пользователя такси-агрегатора APARU: {question}",
                "stream": False
            }
            
            response = requests.post(
                f"{self.local_model_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"❌ Ошибка локальной модели: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка запроса к локальной модели: {e}")
            return None
    
    def _query_railway_api(self, question: str) -> Optional[str]:
        """Запрашивает ответ у Railway API"""
        try:
            payload = {
                "text": question,
                "user_id": "hybrid_client",
                "locale": "ru"
            }
            
            response = requests.post(
                f"{self.railway_api_url}/chat",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                logger.error(f"❌ Ошибка Railway API: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка запроса к Railway API: {e}")
            return None
    
    def get_answer(self, question: str) -> Dict[str, Any]:
        """Получает ответ с приоритетом локальной модели"""
        start_time = datetime.now()
        
        # 1. Пробуем локальную модель (максимальная точность)
        if self.local_model_available:
            logger.info("🧠 Запрашиваем ответ у локальной модели...")
            local_answer = self._query_local_model(question)
            
            if local_answer and local_answer.strip():
                response_time = (datetime.now() - start_time).total_seconds()
                return {
                    'answer': local_answer,
                    'source': 'local_model',
                    'confidence': 0.95,
                    'response_time': response_time,
                    'model': 'aparu-senior-ai'
                }
        
        # 2. Fallback к Railway API (оптимизированная версия)
        if self.railway_api_available:
            logger.info("☁️ Fallback к Railway API...")
            railway_answer = self._query_railway_api(question)
            
            if railway_answer and railway_answer.strip():
                response_time = (datetime.now() - start_time).total_seconds()
                return {
                    'answer': railway_answer,
                    'source': 'railway_api',
                    'confidence': 0.70,
                    'response_time': response_time,
                    'model': 'railway_optimized'
                }
        
        # 3. Если ничего не работает
        response_time = (datetime.now() - start_time).total_seconds()
        return {
            'answer': 'Извините, система временно недоступна',
            'source': 'error',
            'confidence': 0.0,
            'response_time': response_time,
            'model': 'none'
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Возвращает статус системы"""
        return {
            'local_model_available': self.local_model_available,
            'railway_api_available': self.railway_api_available,
            'local_model_url': self.local_model_url,
            'railway_api_url': self.railway_api_url,
            'hybrid_mode': True
        }

# Глобальный экземпляр
hybrid_client = HybridAIClient(
    local_model_url="http://localhost:11434",
    railway_api_url="https://taxi-support-ai-assistant-production.up.railway.app"
)

def get_enhanced_answer(question: str) -> str:
    """Основной API для интеграции"""
    result = hybrid_client.get_answer(question)
    return result['answer']

if __name__ == "__main__":
    # Тестируем гибридную систему
    print("🌐 Тестирование гибридной архитектуры:")
    print(f"   Локальная модель: {'✅' if hybrid_client.local_model_available else '❌'}")
    print(f"   Railway API: {'✅' if hybrid_client.railway_api_available else '❌'}")
    
    test_questions = [
        "Что такое наценка?",
        "Почему так дорого?",
        "Как заказать доставку?",
        "Что такое моточасы?"
    ]
    
    for question in test_questions:
        print(f"\n❓ {question}")
        result = hybrid_client.get_answer(question)
        print(f"✅ {result['answer'][:100]}...")
        print(f"   Источник: {result['source']}")
        print(f"   Уверенность: {result['confidence']:.2f}")
        print(f"   Время: {result['response_time']:.3f}s")

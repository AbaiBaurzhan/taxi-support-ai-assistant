#!/usr/bin/env python3
"""
🌐 Улучшенная гибридная архитектура
Локальная модель + Railway API с туннелированием
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import subprocess
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedHybridClient:
    def __init__(self):
        self.local_model_url = "http://localhost:11434"
        self.railway_api_url = "https://taxi-support-ai-assistant-production.up.railway.app"
        self.tunnel_url = None
        
        # Проверяем доступность
        self._check_services()
        
        # Настраиваем туннель если нужно
        self._setup_tunnel()
    
    def _check_services(self):
        """Проверяет доступность всех сервисов"""
        # Проверяем локальную модель
        try:
            response = requests.get(f"{self.local_model_url}/api/tags", timeout=5)
            self.local_model_available = response.status_code == 200
            if self.local_model_available:
                logger.info("✅ Локальная модель доступна")
        except:
            self.local_model_available = False
            logger.warning("⚠️ Локальная модель недоступна")
        
        # Проверяем Railway API
        try:
            response = requests.get(f"{self.railway_api_url}/health", timeout=5)
            self.railway_api_available = response.status_code == 200
            if self.railway_api_available:
                logger.info("✅ Railway API доступен")
        except:
            self.railway_api_available = False
            logger.warning("⚠️ Railway API недоступен")
    
    def _setup_tunnel(self):
        """Настраивает туннель для локальной модели"""
        if not self.local_model_available:
            logger.info("🔧 Настраиваем туннель для локальной модели...")
            
            # Проверяем ngrok
            try:
                result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("✅ ngrok найден")
                    
                    # Запускаем туннель
                    subprocess.Popen(['ngrok', 'http', '11434', '--log=stdout'], 
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # Ждем запуска
                    time.sleep(3)
                    
                    # Получаем URL туннеля
                    try:
                        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
                        if response.status_code == 200:
                            tunnels = response.json()
                            for tunnel in tunnels.get('tunnels', []):
                                if tunnel.get('proto') == 'https':
                                    self.tunnel_url = tunnel.get('public_url')
                                    logger.info(f"✅ Туннель настроен: {self.tunnel_url}")
                                    break
                    except:
                        logger.warning("⚠️ Не удалось получить URL туннеля")
                else:
                    logger.warning("⚠️ ngrok не найден")
            except:
                logger.warning("⚠️ ngrok не установлен")
    
    def _query_local_model(self, question: str) -> Optional[str]:
        """Запрашивает ответ у локальной модели"""
        model_url = self.tunnel_url or self.local_model_url
        
        try:
            payload = {
                "model": "aparu-senior-ai",
                "prompt": f"Ответь на вопрос пользователя такси-агрегатора APARU: {question}",
                "stream": False
            }
            
            response = requests.post(
                f"{model_url}/api/generate",
                json=payload,
                timeout=60  # Увеличиваем таймаут
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
                timeout=15
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
        if self.local_model_available or self.tunnel_url:
            logger.info("🧠 Запрашиваем ответ у локальной модели...")
            local_answer = self._query_local_model(question)
            
            if local_answer and local_answer.strip():
                response_time = (datetime.now() - start_time).total_seconds()
                return {
                    'answer': local_answer,
                    'source': 'local_model',
                    'confidence': 0.95,
                    'response_time': response_time,
                    'model': 'aparu-senior-ai',
                    'tunnel_used': self.tunnel_url is not None
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
            'tunnel_url': self.tunnel_url,
            'local_model_url': self.local_model_url,
            'railway_api_url': self.railway_api_url,
            'hybrid_mode': True,
            'advanced_tunnel': self.tunnel_url is not None
        }

# Глобальный экземпляр
advanced_hybrid_client = AdvancedHybridClient()

def get_enhanced_answer(question: str) -> str:
    """Основной API для интеграции"""
    result = advanced_hybrid_client.get_answer(question)
    return result['answer']

if __name__ == "__main__":
    # Тестируем улучшенную гибридную систему
    print("🌐 Тестирование улучшенной гибридной архитектуры:")
    status = advanced_hybrid_client.get_status()
    print(f"   Локальная модель: {'✅' if status['local_model_available'] else '❌'}")
    print(f"   Railway API: {'✅' if status['railway_api_available'] else '❌'}")
    print(f"   Туннель: {'✅' if status['tunnel_url'] else '❌'}")
    
    if status['tunnel_url']:
        print(f"   URL туннеля: {status['tunnel_url']}")
    
    test_questions = [
        "Что такое наценка?",
        "Почему так дорого?",
        "Как заказать доставку?"
    ]
    
    for question in test_questions:
        print(f"\n❓ {question}")
        result = advanced_hybrid_client.get_answer(question)
        print(f"✅ {result['answer'][:100]}...")
        print(f"   Источник: {result['source']}")
        print(f"   Уверенность: {result['confidence']:.2f}")
        print(f"   Время: {result['response_time']:.3f}s")
        if result.get('tunnel_used'):
            print(f"   Туннель: ✅")

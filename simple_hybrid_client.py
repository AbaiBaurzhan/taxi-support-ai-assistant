#!/usr/bin/env python3
"""
🚀 УПРОЩЕННАЯ ГИБРИДНАЯ АРХИТЕКТУРА
LLM модель на ноутбуке + Railway проксирует запросы
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleHybridClient:
    def __init__(self, ngrok_url: str = None):
        self.ngrok_url = ngrok_url
        self.ngrok_available = False
        
        # Проверяем доступность ngrok туннеля
        if ngrok_url:
            self._check_ngrok_tunnel()
    
    def _check_ngrok_tunnel(self):
        """Проверяет доступность ngrok туннеля"""
        try:
            response = requests.get(
                f"{self.ngrok_url}/api/tags", 
                timeout=5,
                headers={"ngrok-skip-browser-warning": "true"}
            )
            if response.status_code == 200:
                self.ngrok_available = True
                logger.info("✅ ngrok туннель доступен")
            else:
                logger.warning("⚠️ ngrok туннель недоступен")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось подключиться к ngrok туннелю: {e}")
    
    def get_answer(self, question: str) -> Dict[str, Any]:
        """Получает ответ от гибридной системы"""
        start_time = datetime.now()
        
        # Используем ngrok туннель
        if self.ngrok_available:
            try:
                logger.info("🌐 Запрашиваем ответ через ngrok туннель...")
                response = self._query_via_ngrok(question)
                if response and response.get('answer'):
                    response_time = (datetime.now() - start_time).total_seconds()
                    return {
                        'answer': response['answer'],
                        'source': 'ngrok_tunnel',
                        'confidence': 0.9,
                        'response_time': response_time,
                        'model': 'aparu-senior-ai'
                    }
            except Exception as e:
                logger.error(f"❌ Ошибка ngrok туннеля: {e}")
        
        # Fallback: Простой ответ
        response_time = (datetime.now() - start_time).total_seconds()
        return {
            'answer': 'Извините, система временно недоступна. Попробуйте позже.',
            'source': 'fallback',
            'confidence': 0.0,
            'response_time': response_time,
            'model': 'none'
        }
    
    def _query_via_ngrok(self, question: str) -> Optional[Dict[str, Any]]:
        """Запрашивает ответ через ngrok туннель"""
        try:
            payload = {
                "model": "aparu-senior-ai",
                "prompt": f"Ответь на вопрос о такси APARU: {question}",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 200
                }
            }
            
            response = requests.post(
                f"{self.ngrok_url}/api/generate",
                json=payload,
                timeout=20,  # Увеличенный таймаут
                headers={
                    "Content-Type": "application/json",
                    "ngrok-skip-browser-warning": "true"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'answer': data.get('response', '').strip(),
                    'confidence': 0.9
                }
            else:
                logger.error(f"❌ HTTP ошибка ngrok: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("⏱️ Таймаут ngrok запроса")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка ngrok запроса: {e}")
            return None

# Глобальный экземпляр клиента
simple_hybrid_client = SimpleHybridClient(
    ngrok_url="https://a58a3de709bd.ngrok-free.app"
)

def get_simple_hybrid_answer(question: str) -> str:
    """Получает ответ от упрощенной гибридной системы"""
    try:
        result = simple_hybrid_client.get_answer(question)
        return result['answer']
    except Exception as e:
        logger.error(f"❌ Ошибка гибридной системы: {e}")
        return "Извините, произошла ошибка при обработке вашего запроса."

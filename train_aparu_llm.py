#!/usr/bin/env python3
"""
🧠 APARU LLM Trainer
Обучает LLM модель на базе знаний APARU из BZ.txt
"""

import json
import logging
import subprocess
import time
import requests
from pathlib import Path
from parse_aparu_bz import APARUBZParser
from knowledge_base_trainer import TaxiKnowledgeBase

logger = logging.getLogger(__name__)

class APARULLMTrainer:
    def __init__(self):
        self.knowledge_base = None
        self.ollama_process = None
        
    def setup_training_environment(self):
        """Настраивает среду для обучения"""
        logger.info("Настройка среды обучения...")
        
        # Проверяем Ollama
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("✅ Ollama установлен")
            else:
                logger.error("❌ Ollama не найден")
                return False
        except:
            logger.error("❌ Ollama не установлен")
            return False
        
        return True
    
    def load_aparu_data(self, bz_file: str = "database_Aparu/BZ.txt"):
        """Загружает данные APARU из BZ.txt"""
        logger.info(f"Загружаю данные APARU из {bz_file}")
        
        if not Path(bz_file).exists():
            logger.error(f"Файл {bz_file} не найден!")
            return False
        
        try:
            # Парсим данные
            parser = APARUBZParser()
            knowledge_base = parser.parse_bz_file(bz_file)
            
            # Создаем объект базы знаний
            self.knowledge_base = TaxiKnowledgeBase()
            self.knowledge_base.knowledge_base = knowledge_base
            
            logger.info(f"✅ Загружено {len(knowledge_base)} вопросов-ответов")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            return False
    
    def build_knowledge_index(self):
        """Строит индекс для поиска по базе знаний"""
        logger.info("Строю индекс базы знаний...")
        
        try:
            self.knowledge_base.build_embeddings_index()
            self.knowledge_base.save_index("aparu_knowledge_index.pkl")
            logger.info("✅ Индекс построен и сохранен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка построения индекса: {e}")
            return False
    
    def generate_training_prompts(self, output_file: str = "aparu_training_prompts.json"):
        """Генерирует промпты для обучения LLM"""
        logger.info("Генерирую промпты для обучения...")
        
        try:
            training_prompts = []
            
            for item in self.knowledge_base.knowledge_base:
                # Создаем промпт в стиле APARU
                prompt = f"""Ты - ИИ-ассистент службы поддержки такси-сервиса APARU.

Правила ответа:
- Отвечай вежливо и профессионально
- Начинай с "Здравствуйте"
- Заканчивай "С уважением, команда АПАРУ"
- Отвечай кратко и по делу
- Используй информацию из базы знаний APARU
- Если не знаешь ответа, предложи связаться с оператором

Вопрос: {item['question']}
Ответ: {item['answer']}

Категория: {item['category']}
Ключевые слова: {', '.join(item['keywords'])}

Теперь отвечай на вопросы пользователей в том же стиле."""
                
                training_prompts.append({
                    'prompt': prompt,
                    'question': item['question'],
                    'answer': item['answer'],
                    'category': item['category'],
                    'keywords': item['keywords'],
                    'id': item['id']
                })
            
            # Сохраняем промпты
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(training_prompts, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Промпты сохранены в {output_file}")
            return training_prompts
            
        except Exception as e:
            logger.error(f"Ошибка генерации промптов: {e}")
            return []
    
    def create_aparu_modelfile(self, model_name: str = "aparu-support"):
        """Создает Modelfile для обучения модели APARU"""
        logger.info("Создаю Modelfile для APARU...")
        
        modelfile_content = f"""FROM llama2:7b

SYSTEM "Ты - ИИ-ассистент службы поддержки такси-сервиса APARU. 

Твоя задача - помогать пользователям с вопросами о:
- Тарифах и ценах (наценка, комфорт, моточасы, таксометр)
- Заказах и бронировании (предварительный заказ, доставка)
- Работе водителей (регистрация, баланс, пополнение)
- Технических вопросах (приложение, GPS, обновления)

Правила ответа:
- Всегда начинай с 'Здравствуйте'
- Отвечай вежливо и профессионально
- Заканчивай 'С уважением, команда АПАРУ'
- Отвечай кратко и по делу
- Используй информацию из базы знаний APARU
- Если не знаешь ответа, предложи связаться с оператором
- Отвечай только на русском языке"

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
"""
        
        try:
            with open("Modelfile", 'w', encoding='utf-8') as f:
                f.write(modelfile_content)
            
            logger.info("✅ Modelfile создан")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания Modelfile: {e}")
            return False
    
    def train_aparu_model(self, model_name: str = "aparu-support"):
        """Обучает модель APARU"""
        logger.info(f"Обучаю модель {model_name}...")
        
        try:
            # Создаем модель из Modelfile
            result = subprocess.run(
                ["ollama", "create", model_name, "-f", "Modelfile"],
                capture_output=True, text=True, timeout=300
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Модель {model_name} создана")
                return True
            else:
                logger.error(f"❌ Ошибка создания модели: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка обучения: {e}")
            return False
    
    def test_aparu_model(self, model_name: str = "aparu-support"):
        """Тестирует обученную модель APARU"""
        logger.info(f"Тестирую модель {model_name}...")
        
        test_questions = [
            "Что такое наценка?",
            "Как узнать расценку?",
            "Как пополнить баланс?",
            "Что такое моточасы?",
            "Как работает таксометр?"
        ]
        
        results = []
        
        for question in test_questions:
            logger.info(f"Тестирую: {question}")
            
            try:
                # Отправляем запрос к модели
                payload = {
                    "model": model_name,
                    "prompt": question,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 200
                    }
                }
                
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("response", "")
                    
                    results.append({
                        'question': question,
                        'answer': answer,
                        'status': 'success'
                    })
                    
                    logger.info(f"✅ Ответ: {answer[:100]}...")
                else:
                    results.append({
                        'question': question,
                        'answer': f"Ошибка: {response.status_code}",
                        'status': 'error'
                    })
                    
            except Exception as e:
                results.append({
                    'question': question,
                    'answer': f"Ошибка: {e}",
                    'status': 'error'
                })
        
        return results
    
    def save_test_results(self, results: list, output_file: str = "aparu_test_results.json"):
        """Сохраняет результаты тестирования"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Результаты тестирования сохранены в {output_file}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения результатов: {e}")
    
    def run_full_training(self, bz_file: str = "database_Aparu/BZ.txt", model_name: str = "aparu-support"):
        """Запускает полный процесс обучения"""
        logger.info("🚀 Запуск полного обучения APARU LLM")
        
        # 1. Настройка среды
        if not self.setup_training_environment():
            return False
        
        # 2. Загрузка данных
        if not self.load_aparu_data(bz_file):
            return False
        
        # 3. Построение индекса
        if not self.build_knowledge_index():
            return False
        
        # 4. Генерация промптов
        training_prompts = self.generate_training_prompts()
        if not training_prompts:
            return False
        
        # 5. Создание Modelfile
        if not self.create_aparu_modelfile(model_name):
            return False
        
        # 6. Обучение модели
        if not self.train_aparu_model(model_name):
            return False
        
        # 7. Тестирование
        test_results = self.test_aparu_model(model_name)
        self.save_test_results(test_results)
        
        logger.info("🎉 Обучение завершено!")
        return True

def main():
    """Основная функция"""
    logging.basicConfig(level=logging.INFO)
    
    trainer = APARULLMTrainer()
    
    print("🧠 APARU LLM Trainer")
    print("=" * 50)
    
    # Запускаем полное обучение
    success = trainer.run_full_training()
    
    if success:
        print("\n🎉 Обучение завершено успешно!")
        print("📁 Файлы:")
        print("  - aparu_knowledge_index.pkl (индекс базы знаний)")
        print("  - aparu_training_prompts.json (промпты для обучения)")
        print("  - aparu_test_results.json (результаты тестирования)")
        print("  - Modelfile (конфигурация модели)")
        print("\n🤖 Модель: aparu-support")
        print("🧪 Тестирование: ollama run aparu-support 'Что такое наценка?'")
    else:
        print("\n❌ Обучение завершилось с ошибками")

if __name__ == "__main__":
    main()

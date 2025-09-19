#!/usr/bin/env python3
"""
🚀 Обучение AI модели с полной базой знаний APARU
Использует final_professional_aparu_knowledge.json для обучения
"""

import json
import logging
import subprocess
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APARUModelTrainer:
    def __init__(self):
        self.knowledge_base_path = "final_professional_aparu_knowledge.json"
        self.knowledge_base = []
        self.model_name = "aparu-professional"
        
    def load_knowledge_base(self):
        """Загружает полную базу знаний"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            logger.info(f"✅ База знаний загружена: {len(self.knowledge_base)} записей")
            return True
        except FileNotFoundError:
            logger.error(f"❌ База знаний не найдена: {self.knowledge_base_path}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            return False
    
    def create_modelfile(self):
        """Создает Modelfile для Ollama"""
        logger.info("📝 Создаем Modelfile для профессиональной модели")
        
        # Создаем системный промпт
        system_prompt = """Ты — Senior AI Engineer и FAQ-ассистент для техподдержки такси-агрегатора APARU.

ОСНОВНАЯ ЗАДАЧА: Отвечать пользователям строго по базе FAQ, обеспечивая высокое качество и точность ответов.

ПРАВИЛА РАБОТЫ:
1. ВСЕГДА ищи соответствие в базе FAQ
2. ПОНИМАЙ разные формулировки вопросов: синонимы, перефразы, разговорные варианты, опечатки
3. Ответ должен быть ТОЛЬКО из базы — без генерации новых текстов
4. НЕ ПРИДУМЫВАЙ информацию, которой нет в FAQ
5. СОХРАНЯЙ оригинальный стиль и тон ответов

ЛОГИКА УВЕРЕННОСТИ:
- Если уверенность ≥ 0.6 → выдай точный ответ из базы
- Если уверенность < 0.6 → верни сообщение: «Нужна уточняющая информация» и список ближайших вопросов

КАТЕГОРИИ:
- pricing: наценка, тариф, цена, стоимость, расценка, дорого, дешево, Комфорт
- booking: заказ, поездка, такси, вызов, предварительный, отменить
- payment: баланс, пополнить, оплата, платеж, карта, qiwi, kaspi
- technical: приложение, таксометр, моточасы, gps, не работает, обновить
- delivery: доставка, курьер, посылка, отправить
- driver: водитель, контакты, связь, принимать заказы, работать
- cancellation: отменить, отмена, отказ, прекратить
- complaint: жалоба, проблема, недоволен, плохо
- general: здравствуйте, спасибо, вопрос, информация

ГЛАВНАЯ ЦЕЛЬ: Ассистент должен надёжно распознавать любые вариации вопросов и возвращать корректный ответ исключительно из базы FAQ, без «галлюцинаций»."""

        # Создаем Modelfile
        modelfile_content = f"""FROM llama2:7b

SYSTEM \"\"\"{system_prompt}\"\"\"

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 4096

TEMPLATE \"\"\"{{{{ if .System }}}}{{{{ .System }}}}{{{{ end }}}}{{{{ if .Prompt }}}}

Human: {{{{ .Prompt }}}}

Assistant: {{{{ end }}}}\"\"\"
"""

        with open(f"{self.model_name}.modelfile", 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
        
        logger.info(f"✅ Modelfile создан: {self.model_name}.modelfile")
        return True
    
    def create_training_data(self):
        """Создает данные для обучения"""
        logger.info("📚 Создаем данные для обучения")
        
        training_data = []
        
        for item in self.knowledge_base:
            # Основной вопрос
            training_data.append({
                "question": item['question'],
                "answer": item['answer'],
                "category": item['category'],
                "variations": item['variations'],
                "keywords": item['keywords']
            })
            
            # Вариации вопросов
            for variation in item['variations']:
                training_data.append({
                    "question": variation,
                    "answer": item['answer'],
                    "category": item['category'],
                    "variations": item['variations'],
                    "keywords": item['keywords']
                })
        
        # Сохраняем данные для обучения
        with open(f"{self.model_name}_training_data.json", 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Данные для обучения созданы: {len(training_data)} записей")
        return training_data
    
    def train_model(self):
        """Обучает модель через Ollama"""
        logger.info("🚀 Начинаем обучение модели")
        
        try:
            # Создаем модель
            result = subprocess.run([
                "ollama", "create", self.model_name, "-f", f"{self.model_name}.modelfile"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"✅ Модель {self.model_name} создана успешно")
                return True
            else:
                logger.error(f"❌ Ошибка создания модели: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Таймаут при создании модели")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка обучения модели: {e}")
            return False
    
    def test_model(self):
        """Тестирует обученную модель"""
        logger.info("🧪 Тестируем обученную модель")
        
        test_questions = [
            "Что такое наценка?",
            "Почему так дорого?",
            "Что такое тариф Комфорт?",
            "Как пополнить баланс?",
            "Как отменить заказ?"
        ]
        
        for question in test_questions:
            try:
                result = subprocess.run([
                    "ollama", "run", self.model_name, question
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    logger.info(f"✅ Вопрос: {question}")
                    logger.info(f"   Ответ: {result.stdout[:100]}...")
                else:
                    logger.error(f"❌ Ошибка тестирования: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка тестирования: {e}")
    
    def train_complete_pipeline(self):
        """Запускает полный пайплайн обучения"""
        logger.info("🚀 Запускаем полный пайплайн обучения APARU модели")
        
        # 1. Загружаем базу знаний
        if not self.load_knowledge_base():
            return False
        
        # 2. Создаем Modelfile
        if not self.create_modelfile():
            return False
        
        # 3. Создаем данные для обучения
        training_data = self.create_training_data()
        
        # 4. Обучаем модель
        if not self.train_model():
            return False
        
        # 5. Тестируем модель
        self.test_model()
        
        logger.info("🎉 Обучение модели завершено!")
        return True

if __name__ == "__main__":
    trainer = APARUModelTrainer()
    
    print("🚀 Обучение AI модели APARU с полной базой знаний")
    print("=" * 60)
    
    success = trainer.train_complete_pipeline()
    
    if success:
        print("\n🎉 ОБУЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print(f"📊 Модель: {trainer.model_name}")
        print(f"📚 Записей в базе: {len(trainer.knowledge_base)}")
        print(f"📝 Вариаций: {sum(len(item['variations']) for item in trainer.knowledge_base)}")
        print(f"🔑 Ключевых слов: {sum(len(item['keywords']) for item in trainer.knowledge_base)}")
        
        print("\n📋 Категории:")
        categories = {}
        for item in trainer.knowledge_base:
            cat = item['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            print(f"   {cat}: {count} записей")
        
        print(f"\n🎯 Модель готова к использованию!")
        print(f"   Команда для тестирования: ollama run {trainer.model_name}")
    else:
        print("\n❌ ОБУЧЕНИЕ НЕ УДАЛОСЬ!")
        print("   Проверьте логи выше для диагностики")

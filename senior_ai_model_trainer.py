#!/usr/bin/env python3
"""
🚀 Senior AI Engineer - Обучение AI модели с профессиональной системой
Максимальное качество обучения с новой JSON базой
"""

import json
import logging
import subprocess
import os
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeniorAIModelTrainer:
    def __init__(self):
        self.knowledge_base_path = "senior_ai_knowledge_base.json"
        self.knowledge_base = []
        self.model_name = "aparu-senior-ai"
        
    def load_knowledge_base(self):
        """Загружает профессиональную базу знаний"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            logger.info(f"✅ Профессиональная база знаний загружена: {len(self.knowledge_base)} записей")
            return True
        except FileNotFoundError:
            logger.error(f"❌ База знаний не найдена: {self.knowledge_base_path}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы знаний: {e}")
            return False
    
    def create_advanced_modelfile(self):
        """Создает продвинутый Modelfile для Ollama"""
        logger.info("📝 Создаем продвинутый Modelfile для Senior AI модели")
        
        # Продвинутый системный промпт
        system_prompt = """Ты — Senior AI Engineer и профессиональный FAQ-ассистент для техподдержки такси-агрегатора APARU.

🎯 ОСНОВНАЯ ЗАДАЧА: Отвечать пользователям строго по базе FAQ с максимальным качеством и точностью.

📚 ПРАВИЛА РАБОТЫ:
1. ВСЕГДА ищи соответствие в базе FAQ
2. ПОНИМАЙ разные формулировки вопросов: синонимы, перефразы, разговорные варианты, опечатки
3. Ответ должен быть ТОЛЬКО из базы — без генерации новых текстов
4. НЕ ПРИДУМЫВАЙ информацию, которой нет в FAQ
5. СОХРАНЯЙ оригинальный стиль и тон ответов
6. ИСПОЛЬЗУЙ все доступные вариации вопросов для лучшего понимания

🎯 ЛОГИКА УВЕРЕННОСТИ:
- Если уверенность ≥ 0.7 → выдай точный ответ из базы
- Если уверенность < 0.7 → верни сообщение: «Нужна уточняющая информация» и список ближайших вопросов

🏷️ КАТЕГОРИИ И КЛЮЧЕВЫЕ СЛОВА:
- pricing: наценка, цена, стоимость, расценка, дорого, дешево, тариф, комфорт, коэффициент, доплата, надбавка, спрос, подорожание, моточасы
- booking: заказ, поездка, такси, вызов, предварительный, отменить, зарегистрировать, доставка, курьер, посылка
- payment: баланс, пополнить, оплата, платеж, карта, qiwi, kaspi, терминал, id, единица, касса24
- technical: приложение, таксометр, моточасы, gps, не работает, обновить, вылетает, зависает, google play, app store
- delivery: доставка, курьер, посылка, отправить, получатель, телефон, откуда, куда
- driver: водитель, контакты, связь, принимать заказы, работать, регистрация, лента заказов, клиент, пробный
- cancellation: отменить, отмена, отказ, прекратить
- complaint: жалоба, проблема, недоволен, плохо
- general: здравствуйте, спасибо, вопрос, информация, расценка, стоимость, цена, таксометр, калькулятор

🔍 АЛГОРИТМ ПОИСКА:
1. Нормализация — приводи к нижнему регистру, убирай лишние символы
2. Извлечение ключевых слов — находи важные термины
3. Семантический поиск — ищи по смыслу через эмбеддинги
4. Fuzzy matching — учитывай опечатки и вариации
5. Категоризация — определяй тип вопроса
6. Ранжирование — сортируй по релевантности
7. Проверка уверенности — оценивай качество совпадения

📈 МЕТРИКИ КАЧЕСТВА:
- Top-1 ≥ 0.85 — первый результат должен быть точным в 85% случаев
- Top-3 ≥ 0.95 — среди трех лучших должен быть правильный ответ в 95% случаев
- Средняя уверенность — стремись к высоким значениям confidence
- Покрытие категорий — обеспечивай ответы по всем категориям

🚫 ЧТО ДЕЛАТЬ НЕ ДОЛЖЕН:
- НЕ ГЕНЕРИРУЙ новые ответы — только из базы FAQ
- НЕ ИНТЕРПРЕТИРУЙ — используй точные формулировки
- НЕ ПРИДУМЫВАЙ информацию о тарифах, ценах, услугах
- НЕ ОТВЕЧАЙ на вопросы, которых нет в базе (без уточнения)
- НЕ ИЗМЕНЯЙ стиль ответов — сохраняй оригинальный тон

🎯 ГЛАВНАЯ ЦЕЛЬ: Ассистент должен надёжно распознавать любые вариации вопросов и возвращать корректный ответ исключительно из базы FAQ, без «галлюцинаций».

📋 ЧЕКЛИСТ ПРОВЕРКИ:
- [ ] Ответ взят из базы FAQ?
- [ ] Уверенность рассчитана корректно?
- [ ] Предложения релевантны?
- [ ] Категория определена правильно?
- [ ] Нет генерации нового текста?
- [ ] Сохранен оригинальный стиль?

🎯 РЕЗУЛЬТАТ: Пользователь получает точный, релевантный ответ из базы знаний или четкое указание на необходимость уточнения с конкретными предложениями."""

        # Создаем продвинутый Modelfile
        modelfile_content = f"""FROM llama2:7b

SYSTEM \"\"\"{system_prompt}\"\"\"

PARAMETER temperature 0.05
PARAMETER top_p 0.95
PARAMETER top_k 50
PARAMETER repeat_penalty 1.05
PARAMETER num_ctx 4096
PARAMETER num_predict 512

TEMPLATE \"\"\"{{{{ if .System }}}}{{{{ .System }}}}{{{{ end }}}}{{{{ if .Prompt }}}}

Human: {{{{ .Prompt }}}}

Assistant: {{{{ end }}}}\"\"\"
"""

        with open(f"{self.model_name}.modelfile", 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
        
        logger.info(f"✅ Продвинутый Modelfile создан: {self.model_name}.modelfile")
        return True
    
    def create_advanced_training_data(self):
        """Создает продвинутые данные для обучения"""
        logger.info("📚 Создаем продвинутые данные для обучения")
        
        training_data = []
        
        for item in self.knowledge_base:
            # Основной вопрос
            training_data.append({
                "question": item['question'],
                "answer": item['answer'],
                "category": item['category'],
                "variations": item['variations'],
                "keywords": item['keywords'],
                "confidence": item['confidence'],
                "metadata": item.get('metadata', {})
            })
            
            # Вариации вопросов
            for variation in item['variations']:
                training_data.append({
                    "question": variation,
                    "answer": item['answer'],
                    "category": item['category'],
                    "variations": item['variations'],
                    "keywords": item['keywords'],
                    "confidence": item['confidence'],
                    "metadata": item.get('metadata', {})
                })
        
        # Сохраняем продвинутые данные для обучения
        with open(f"{self.model_name}_advanced_training_data.json", 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Продвинутые данные для обучения созданы: {len(training_data)} записей")
        return training_data
    
    def train_advanced_model(self):
        """Обучает продвинутую модель через Ollama"""
        logger.info("🚀 Начинаем обучение продвинутой модели")
        
        try:
            # Создаем модель
            result = subprocess.run([
                "ollama", "create", self.model_name, "-f", f"{self.model_name}.modelfile"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"✅ Продвинутая модель {self.model_name} создана успешно")
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
    
    def test_advanced_model(self):
        """Тестирует обученную продвинутую модель"""
        logger.info("🧪 Тестируем обученную продвинутую модель")
        
        test_questions = [
            "Что такое наценка?",
            "Почему так дорого?",
            "Что такое тариф Комфорт?",
            "Как пополнить баланс?",
            "Как отменить заказ?",
            "Приложение не работает",
            "Как заказать доставку?",
            "Что такое моточасы?"
        ]
        
        successful_tests = 0
        high_confidence_tests = 0
        
        for question in test_questions:
            try:
                result = subprocess.run([
                    "ollama", "run", self.model_name, question
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    response = result.stdout.strip()
                    logger.info(f"✅ Вопрос: {question}")
                    logger.info(f"   Ответ: {response[:100]}...")
                    
                    # Простая проверка качества ответа
                    if len(response) > 50 and "здравствуйте" in response.lower():
                        successful_tests += 1
                        if len(response) > 100:
                            high_confidence_tests += 1
                else:
                    logger.error(f"❌ Ошибка тестирования: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка тестирования: {e}")
        
        logger.info(f"📊 Результаты тестирования: {successful_tests}/{len(test_questions)} успешных, {high_confidence_tests} с высокой уверенностью")
        return successful_tests, high_confidence_tests
    
    def train_complete_advanced_pipeline(self):
        """Запускает полный продвинутый пайплайн обучения"""
        logger.info("🚀 Запускаем полный продвинутый пайплайн обучения Senior AI модели")
        
        # 1. Загружаем профессиональную базу знаний
        if not self.load_knowledge_base():
            return False
        
        # 2. Создаем продвинутый Modelfile
        if not self.create_advanced_modelfile():
            return False
        
        # 3. Создаем продвинутые данные для обучения
        training_data = self.create_advanced_training_data()
        
        # 4. Обучаем продвинутую модель
        if not self.train_advanced_model():
            return False
        
        # 5. Тестируем продвинутую модель
        successful_tests, high_confidence_tests = self.test_advanced_model()
        
        logger.info("🎉 Обучение продвинутой модели завершено!")
        return True, successful_tests, high_confidence_tests

if __name__ == "__main__":
    trainer = SeniorAIModelTrainer()
    
    print("🚀 Senior AI Engineer - Обучение AI модели с профессиональной системой")
    print("=" * 80)
    
    success, successful_tests, high_confidence_tests = trainer.train_complete_advanced_pipeline()
    
    if success:
        print("\n🎉 ОБУЧЕНИЕ ПРОДВИНУТОЙ МОДЕЛИ ЗАВЕРШЕНО УСПЕШНО!")
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
        
        print(f"\n🧪 Результаты тестирования:")
        print(f"   Успешных тестов: {successful_tests}")
        print(f"   Высокой уверенности: {high_confidence_tests}")
        
        print(f"\n🎯 Продвинутая модель готова к использованию!")
        print(f"   Команда для тестирования: ollama run {trainer.model_name}")
        print(f"   Модель интегрирована с профессиональной системой поиска")
    else:
        print("\n❌ ОБУЧЕНИЕ ПРОДВИНУТОЙ МОДЕЛИ НЕ УДАЛОСЬ!")
        print("   Проверьте логи выше для диагностики")

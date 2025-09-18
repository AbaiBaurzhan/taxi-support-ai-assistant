# 🧠 Обучение LLM на базе данных поддержки такси

## 🎯 Подходы к обучению

### 1. **RAG (Retrieval Augmented Generation) - Рекомендую!**
- Не требует переобучения модели
- Быстро внедряется
- Легко обновляется
- Работает с любой моделью

### 2. **Fine-tuning**
- Полное переобучение модели
- Требует много ресурсов
- Сложно обновлять
- Лучше для специфических задач

## 🚀 Быстрый старт с RAG

### 1. **Подготовка данных**

#### Из базы данных SQLite:
```python
from knowledge_base_trainer import TaxiKnowledgeBase

kb = TaxiKnowledgeBase()
kb.load_from_database('support_database.db')
kb.build_embeddings_index()
kb.save_index('taxi_knowledge_index.pkl')
```

#### Из CSV файла:
```python
kb = TaxiKnowledgeBase()
kb.load_from_csv('support_data.csv')
kb.build_embeddings_index()
kb.save_index('taxi_knowledge_index.pkl')
```

#### Из JSON файла:
```python
kb = TaxiKnowledgeBase()
kb.load_from_json('support_data.json')
kb.build_embeddings_index()
kb.save_index('taxi_knowledge_index.pkl')
```

### 2. **Структура данных**

#### Для CSV:
```csv
question,answer,category,keywords
"Где мой водитель?","Водитель едет к вам, ожидаемое время 5 минут","ride_status","водитель,статус,поездка"
"Как считается цена?","Цена рассчитывается по расстоянию и времени","pricing","цена,стоимость,тариф"
```

#### Для JSON:
```json
{
  "ride_status": [
    {
      "question": "Где мой водитель?",
      "answer": "Водитель едет к вам, ожидаемое время 5 минут",
      "keywords": ["водитель", "статус", "поездка"]
    }
  ],
  "pricing": [
    {
      "question": "Как считается цена?",
      "answer": "Цена рассчитывается по расстоянию и времени",
      "keywords": ["цена", "стоимость", "тариф"]
    }
  ]
}
```

### 3. **Интеграция с APARU**

#### Обновляем main.py:
```python
# Заменяем импорт
from enhanced_llm_client import enhanced_llm_client

# В функции chat() заменяем:
# prompt = llm_client.create_taxi_context_prompt(processed_text, intent, final_locale)
# response_text = llm_client.generate_response(prompt)

# На:
prompt = enhanced_llm_client.create_taxi_context_prompt(processed_text, intent, final_locale)
response_text = enhanced_llm_client.generate_response(prompt)
```

#### Загружаем базу знаний при запуске:
```python
# В начале main.py
if enhanced_llm_client.load_knowledge_base():
    logger.info("✅ База знаний загружена")
else:
    logger.warning("⚠️ База знаний не загружена, используется fallback")
```

## 🔧 Fine-tuning подход

### 1. **Подготовка данных для обучения**

```python
# Генерируем данные для обучения
kb.generate_training_data('training_data.json')
```

### 2. **Обучение с Ollama**

```bash
# Создаем Modelfile
cat > Modelfile << EOF
FROM llama2:7b

SYSTEM "Ты - ИИ-ассистент службы поддержки такси-сервиса. Отвечай кратко и по делу."

PARAMETER temperature 0.7
PARAMETER top_p 0.9
EOF

# Создаем модель
ollama create taxi-support -f Modelfile

# Тестируем
ollama run taxi-support "Где мой водитель?"
```

### 3. **Обучение с Transformers**

```python
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
import torch

# Загружаем модель
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Подготавливаем данные
def prepare_data(training_data):
    inputs = []
    for item in training_data:
        text = f"Вопрос: {item['question']}\nОтвет: {item['answer']}"
        inputs.append(text)
    return inputs

# Обучаем
training_args = TrainingArguments(
    output_dir='./taxi-support-model',
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=1000,
    save_total_limit=2,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=prepare_data(training_data),
)

trainer.train()
```

## 📊 Сравнение подходов

| Подход | Сложность | Ресурсы | Обновление | Качество |
|--------|------------|---------|------------|----------|
| RAG | Низкая | Низкие | Легко | Высокое |
| Fine-tuning | Высокая | Высокие | Сложно | Очень высокое |
| Prompt Engineering | Очень низкая | Очень низкие | Очень легко | Среднее |

## 🎯 Рекомендации

### **Для быстрого старта:**
1. Используйте RAG подход
2. Подготовьте данные в CSV/JSON
3. Запустите `knowledge_base_trainer.py`
4. Интегрируйте с `enhanced_llm_client.py`

### **Для продакшена:**
1. Начните с RAG
2. Соберите метрики качества
3. При необходимости переходите на Fine-tuning

## 🧪 Тестирование

### **Тест базы знаний:**
```python
python3 knowledge_base_trainer.py
```

### **Тест enhanced LLM:**
```python
python3 enhanced_llm_client.py
```

### **Тест интеграции:**
```python
python3 main.py
```

## 📈 Метрики качества

### **RAG метрики:**
- Точность поиска (precision@k)
- Время ответа
- Покрытие базы знаний

### **LLM метрики:**
- Качество ответов
- Релевантность
- Полезность для пользователей

## 🔄 Обновление базы знаний

### **Добавление новых записей:**
```python
# Загружаем существующую базу
kb = TaxiKnowledgeBase()
kb.load_index('taxi_knowledge_index.pkl')

# Добавляем новые данные
new_data = [
    {
        'question': 'Новый вопрос',
        'answer': 'Новый ответ',
        'category': 'new_category',
        'keywords': ['новый', 'вопрос']
    }
]

# Перестраиваем индекс
kb.knowledge_base.extend(new_data)
kb.build_embeddings_index()
kb.save_index('taxi_knowledge_index.pkl')
```

## 🚨 Важные моменты

### **Качество данных:**
- Проверяйте корректность ответов
- Убирайте дубликаты
- Структурируйте по категориям

### **Производительность:**
- Используйте легкие модели эмбеддингов
- Ограничивайте размер базы знаний
- Кэшируйте результаты поиска

### **Безопасность:**
- Не включайте чувствительные данные
- Проверяйте ответы перед публикацией
- Логируйте все запросы

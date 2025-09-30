"""
Конвертер BZ.txt в формат kb.json для системы поиска
"""

import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_bz_to_kb():
    """Конвертирует BZ.txt в kb.json"""
    
    # Путь к файлу BZ.txt
    bz_path = "BZ.txt"
    
    if not os.path.exists(bz_path):
        logger.error(f"Файл {bz_path} не найден!")
        return False
    
    try:
        # Читаем BZ.txt
        with open(bz_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим JSON
        bz_data = json.loads(content)
        
        # Конвертируем в формат kb.json
        kb_data = {
            "faq": []
        }
        
        for item in bz_data:
            # Извлекаем данные
            question_variations = item.get('question_variations', [])
            keywords = item.get('keywords', [])
            answer = item.get('answer', '')
            
            # Создаем основной вопрос из первой вариации
            main_question = question_variations[0] if question_variations else ""
            
            # Создаем FAQ элемент
            faq_item = {
                "question": main_question,
                "answer": answer,
                "keywords": keywords,
                "question_variations": question_variations
            }
            
            kb_data["faq"].append(faq_item)
        
        # Сохраняем в kb.json
        kb_path = "backend/kb.json"
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(kb_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Успешно конвертировано {len(kb_data['faq'])} FAQ элементов")
        logger.info(f"📁 Сохранено в {kb_path}")
        
        # Создаем также fixtures.json если его нет
        fixtures_path = "backend/fixtures.json"
        if not os.path.exists(fixtures_path):
            fixtures_data = {
                "rides": [
                    {
                        "id": "ride_001",
                        "user_id": "user_001",
                        "status": "completed",
                        "driver": "Иван Иванов",
                        "car": "Toyota Camry A123ABC",
                        "price": 850,
                        "distance": 5.2,
                        "duration": 15
                    }
                ],
                "receipts": [
                    {
                        "id": "receipt_001",
                        "user_id": "user_001",
                        "ride_id": "ride_001",
                        "amount": 850,
                        "date": "2024-01-15T10:30:00Z"
                    }
                ],
                "cards": [
                    {
                        "id": "card_001",
                        "user_id": "user_001",
                        "type": "Visa",
                        "last_four": "1234",
                        "is_primary": True
                    }
                ],
                "tickets": [
                    {
                        "id": "TKT_1001",
                        "user_id": "user_001",
                        "description": "Двойное списание средств",
                        "status": "open",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ]
            }
            
            with open(fixtures_path, 'w', encoding='utf-8') as f:
                json.dump(fixtures_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📁 Создан {fixtures_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка конвертации: {e}")
        return False

if __name__ == "__main__":
    success = convert_bz_to_kb()
    if success:
        print("🎉 Конвертация завершена успешно!")
    else:
        print("❌ Ошибка конвертации!")

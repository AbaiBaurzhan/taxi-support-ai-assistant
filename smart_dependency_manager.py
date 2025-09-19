#!/usr/bin/env python3
"""
🧠 Умная система выбора зависимостей
Автоматически выбирает между полной и облегченной версией
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartDependencyManager:
    def __init__(self):
        self.railway_mode = os.getenv("RAILWAY_MODE", "false").lower() == "true"
        self.force_lightweight = os.getenv("FORCE_LIGHTWEIGHT", "false").lower() == "true"
        self.force_full_ml = os.getenv("FORCE_FULL_ML", "false").lower() == "true"
        
    def detect_environment(self):
        """Определяет окружение и возможности"""
        environment_info = {
            'is_railway': self.railway_mode,
            'is_docker': self._is_docker(),
            'is_heroku': self._is_heroku(),
            'has_gpu': self._has_gpu(),
            'memory_gb': self._get_memory_gb(),
            'cpu_cores': self._get_cpu_cores()
        }
        
        logger.info(f"🔍 Обнаружено окружение: {environment_info}")
        return environment_info
    
    def _is_docker(self):
        """Проверяет, запущено ли в Docker"""
        return os.path.exists('/.dockerenv') or os.path.exists('/proc/1/cgroup')
    
    def _is_heroku(self):
        """Проверяет, запущено ли на Heroku"""
        return 'DYNO' in os.environ
    
    def _has_gpu(self):
        """Проверяет наличие GPU"""
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _get_memory_gb(self):
        """Получает объем памяти в GB"""
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        kb = int(line.split()[1])
                        return kb / (1024 * 1024)  # Convert to GB
        except:
            pass
        return 1.0  # Default
    
    def _get_cpu_cores(self):
        """Получает количество CPU ядер"""
        try:
            return os.cpu_count() or 1
        except:
            return 1
    
    def should_use_full_ml(self, environment_info):
        """Определяет, нужно ли использовать полные ML зависимости"""
        
        # Принудительные настройки
        if self.force_full_ml:
            logger.info("🔧 Принудительно включены полные ML зависимости")
            return True
        
        if self.force_lightweight:
            logger.info("🔧 Принудительно включена облегченная версия")
            return False
        
        # Автоматическое определение
        if environment_info['is_railway']:
            logger.info("☁️ Railway окружение - используем облегченную версию")
            return False
        
        if environment_info['is_docker'] and environment_info['memory_gb'] < 2:
            logger.info("🐳 Docker с ограниченной памятью - используем облегченную версию")
            return False
        
        if environment_info['memory_gb'] < 1:
            logger.info("💾 Мало памяти - используем облегченную версию")
            return False
        
        # Если есть GPU и достаточно памяти - используем полную версию
        if environment_info['has_gpu'] and environment_info['memory_gb'] >= 4:
            logger.info("🚀 GPU + много памяти - используем полные ML зависимости")
            return True
        
        # Если много памяти и CPU - используем полную версию
        if environment_info['memory_gb'] >= 4 and environment_info['cpu_cores'] >= 4:
            logger.info("💪 Мощное железо - используем полные ML зависимости")
            return True
        
        # По умолчанию - облегченная версия
        logger.info("⚖️ Стандартное окружение - используем облегченную версию")
        return False
    
    def setup_dependencies(self):
        """Настраивает зависимости в зависимости от окружения"""
        environment_info = self.detect_environment()
        use_full_ml = self.should_use_full_ml(environment_info)
        
        if use_full_ml:
            logger.info("🚀 Настраиваем полные ML зависимости...")
            self._setup_full_ml()
        else:
            logger.info("⚡ Настраиваем облегченные зависимости...")
            self._setup_lightweight()
        
        return use_full_ml
    
    def _setup_full_ml(self):
        """Настраивает полные ML зависимости"""
        # Копируем полный requirements.txt
        if Path("requirements_full_ml.txt").exists():
            subprocess.run(['cp', 'requirements_full_ml.txt', 'requirements.txt'])
            logger.info("✅ Скопирован requirements_full_ml.txt")
        else:
            logger.error("❌ Файл requirements_full_ml.txt не найден")
    
    def _setup_lightweight(self):
        """Настраивает облегченные зависимости"""
        # Копируем облегченный requirements.txt
        if Path("requirements_lightweight.txt").exists():
            subprocess.run(['cp', 'requirements_lightweight.txt', 'requirements.txt'])
            logger.info("✅ Скопирован requirements_lightweight.txt")
        else:
            logger.error("❌ Файл requirements_lightweight.txt не найден")

def main():
    """Основная функция"""
    print("🧠 Умная система выбора зависимостей")
    print("=" * 50)
    
    manager = SmartDependencyManager()
    use_full_ml = manager.setup_dependencies()
    
    print(f"\n📊 Результат:")
    print(f"   Полные ML зависимости: {'✅' if use_full_ml else '❌'}")
    print(f"   Облегченная версия: {'✅' if not use_full_ml else '❌'}")
    
    if use_full_ml:
        print(f"\n🚀 Установка полных зависимостей:")
        print(f"   pip install -r requirements.txt")
        print(f"   Время установки: 5-10 минут")
        print(f"   Размер: ~2-3 GB")
        print(f"   Точность: 80%")
    else:
        print(f"\n⚡ Установка облегченных зависимостей:")
        print(f"   pip install -r requirements.txt")
        print(f"   Время установки: 1-2 минуты")
        print(f"   Размер: ~100 MB")
        print(f"   Точность: 70%")
    
    print(f"\n🎯 Система готова к работе!")

if __name__ == "__main__":
    main()

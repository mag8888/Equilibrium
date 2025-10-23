#!/usr/bin/env python
"""
Автоматическая инициализация TRINARY MLM на Railway
"""
import os
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlm_system.settings')
    django.setup()
    
    print("🚀 Автоматическая инициализация TRINARY MLM...")
    
    try:
        # Применяем миграции
        print("🗄️ Применение миграций...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Автоматическая инициализация
        print("🔧 Инициализация базы данных...")
        execute_from_command_line(['manage.py', 'auto_init'])
        
        # Сбор статических файлов
        print("📦 Сбор статических файлов...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        print("✅ Автоматическая инициализация завершена!")
        print("🌐 Система TRINARY MLM готова к работе!")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {str(e)}")
        print("🔄 Попробуйте перезапустить сервис на Railway")

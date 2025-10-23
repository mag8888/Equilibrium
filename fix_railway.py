#!/usr/bin/env python
"""
Скрипт для исправления проблем на Railway
"""
import os
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlm_system.settings')
    django.setup()
    
    print("🔧 Исправление проблем на Railway...")
    
    # Применяем миграции
    print("📦 Применение миграций...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Создаем суперпользователя
    print("👤 Создание суперпользователя...")
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("✅ Создан суперпользователь: admin / admin123")
    else:
        print("✅ Суперпользователь уже существует")
    
    # Создаем настройки MLM
    print("⚙️ Создание настроек MLM...")
    from mlm.models import MLMSettings
    
    if not MLMSettings.objects.filter(is_active=True).exists():
        MLMSettings.objects.create(
            registration_fee=100.00,
            green_bonus_first=100.00,
            green_bonus_second=50.00,
            red_bonus=50.00,
            max_partners_per_level=3,
            is_active=True
        )
        print("✅ Созданы настройки MLM")
    else:
        print("✅ Настройки MLM уже существуют")
    
    # Собираем статические файлы
    print("📁 Сбор статических файлов...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    print("✅ Исправление завершено!")
    print("🌐 Система должна работать по адресу: https://web-production-48c0.up.railway.app/")
    print("👤 Админ-доступ: admin / admin123")

#!/usr/bin/env python
"""
Скрипт для проверки статуса системы TRINARY MLM
"""
import os
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlm_system.settings')
    django.setup()
    
    from django.contrib.auth import get_user_model
    from mlm.models import MLMSettings, MLMStructure, Payment, Bonus
    
    User = get_user_model()
    
    print("🔍 Проверка статуса системы TRINARY MLM")
    print("=" * 50)
    
    # Проверка пользователей
    total_users = User.objects.count()
    participants = User.objects.filter(status='participant').count()
    partners = User.objects.filter(status='partner').count()
    
    print(f"👥 Пользователи:")
    print(f"   Всего: {total_users}")
    print(f"   Участников: {participants}")
    print(f"   Партнеров: {partners}")
    
    # Проверка структуры
    structure_count = MLMStructure.objects.count()
    print(f"🌳 Структура MLM: {structure_count} записей")
    
    # Проверка платежей
    total_payments = Payment.objects.count()
    completed_payments = Payment.objects.filter(status='completed').count()
    print(f"💳 Платежи:")
    print(f"   Всего: {total_payments}")
    print(f"   Завершенных: {completed_payments}")
    
    # Проверка бонусов
    total_bonuses = Bonus.objects.count()
    total_bonus_amount = sum(bonus.amount for bonus in Bonus.objects.all())
    print(f"🎁 Бонусы:")
    print(f"   Всего: {total_bonuses}")
    print(f"   Общая сумма: ${total_bonus_amount}")
    
    # Проверка настроек
    mlm_settings = MLMSettings.objects.filter(is_active=True).first()
    if mlm_settings:
        print(f"⚙️ Настройки MLM:")
        print(f"   Регистрация: ${mlm_settings.registration_fee}")
        print(f"   Зеленый бонус 1: ${mlm_settings.green_bonus_first}")
        print(f"   Зеленый бонус 2: ${mlm_settings.green_bonus_second}")
        print(f"   Красный бонус: ${mlm_settings.red_bonus}")
    else:
        print("❌ Настройки MLM не найдены!")
    
    # Проверка суперпользователя
    admin_exists = User.objects.filter(username='admin').exists()
    if admin_exists:
        print("✅ Суперпользователь admin существует")
    else:
        print("❌ Суперпользователь admin не найден!")
    
    print("=" * 50)
    print("✅ Проверка завершена!")

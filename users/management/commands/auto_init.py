from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mlm.models import MLMSettings
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Автоматическая инициализация системы TRINARY MLM'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Автоматическая инициализация TRINARY MLM...")
        
        try:
            with transaction.atomic():
                # Создаем суперпользователя если его нет
                if not User.objects.filter(username='admin').exists():
                    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
                    self.stdout.write(
                        self.style.SUCCESS('✅ Создан суперпользователь: admin / admin123')
                    )
                else:
                    self.stdout.write('✅ Суперпользователь уже существует')

                # Создаем настройки MLM если их нет
                if not MLMSettings.objects.filter(is_active=True).exists():
                    MLMSettings.objects.create(
                        registration_fee=100.00,
                        green_bonus_first=100.00,
                        green_bonus_second=50.00,
                        red_bonus=50.00,
                        max_partners_per_level=3,
                        is_active=True
                    )
                    self.stdout.write(
                        self.style.SUCCESS('✅ Созданы настройки MLM')
                    )
                else:
                    self.stdout.write('✅ Настройки MLM уже существуют')

                self.stdout.write(
                    self.style.SUCCESS('✅ Автоматическая инициализация завершена!')
                )
                self.stdout.write("🌐 Система готова к работе!")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при инициализации: {str(e)}')
            )

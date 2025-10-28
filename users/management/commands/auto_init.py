from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mlm.models import MLMSettings, MLMPartner
from django.utils import timezone
import random
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

                # Создаем демо-пользователя, под которым хранится структура
                demo_user, created = User.objects.get_or_create(
                    username='mlm_demo',
                    defaults={'email': 'mlm_demo@example.com'}
                )
                if created:
                    demo_user.set_password('mlm_demo_password')
                    demo_user.save(update_fields=['password'])
                    self.stdout.write(self.style.SUCCESS('✅ Создан демо-пользователь mlm_demo'))
                else:
                    self.stdout.write('✅ Демо-пользователь mlm_demo уже существует')

                # Добавляем IVA как первого партнера Level 0* для demo пользователя
                if not MLMPartner.objects.filter(root_user=demo_user, human_name='IVA').exists():
                    uid = str(random.randint(1000000, 9999999))
                    MLMPartner.objects.create(
                        unique_id=uid,
                        human_name='IVA',
                        level=0,
                        position_x=0,
                        position_y=240,
                        parent=None,
                        root_user=demo_user,
                        created_at=timezone.now(),
                        is_active=True,
                    )
                    self.stdout.write(self.style.SUCCESS(f'👑 Добавлен первый партнер IVA (0*) c ID {uid}'))
                else:
                    self.stdout.write('👑 Партнер IVA уже существует — пропускаем')

                self.stdout.write(
                    self.style.SUCCESS('✅ Автоматическая инициализация завершена!')
                )
                self.stdout.write("🌐 Система готова к работе!")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при инициализации: {str(e)}')
            )

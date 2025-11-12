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
                # Создаем root admin как первого пользователя
                from mlm.models import MLMStructure
                
                root_admin, created = User.objects.get_or_create(
                    username='admin',
                    defaults={
                        'email': 'admin@example.com',
                        'is_superuser': True,
                        'is_staff': True,
                    }
                )
                if created:
                    root_admin.set_password('admin123')
                    root_admin.save()
                    self.stdout.write(
                        self.style.SUCCESS('✅ Создан root admin: admin / admin123')
                    )
                else:
                    # Убеждаемся, что admin - суперпользователь
                    if not root_admin.is_superuser:
                        root_admin.is_superuser = True
                        root_admin.is_staff = True
                        root_admin.save()
                        self.stdout.write(
                            self.style.SUCCESS('✅ Пользователь admin повышен до root admin')
                        )
                    else:
                        self.stdout.write('✅ Root admin уже существует')

                # Создаем MLM структуру для root admin
                mlm_structure, created = MLMStructure.objects.get_or_create(
                    user=root_admin,
                    defaults={
                        'parent': None,
                        'position': 0,
                        'level': 0,
                        'is_active': True,
                    }
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Создана MLM структура для root admin')
                    )
                else:
                    # Убеждаемся, что root admin - корень структуры
                    if mlm_structure.parent is not None or mlm_structure.level != 0:
                        mlm_structure.parent = None
                        mlm_structure.level = 0
                        mlm_structure.position = 0
                        mlm_structure.save()
                        self.stdout.write(
                            self.style.SUCCESS('✅ MLM структура root admin обновлена')
                        )

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

                # Добавляем root admin как первого партнера Level 0* в MLMPartner
                if not MLMPartner.objects.filter(root_user=root_admin, unique_id='0000001').exists():
                    MLMPartner.objects.create(
                        unique_id='0000001',
                        human_name='Admin',
                        level=0,
                        position_x=0,
                        position_y=240,
                        parent=None,
                        root_user=root_admin,
                        created_at=timezone.now(),
                        is_active=True,
                    )
                    self.stdout.write(self.style.SUCCESS('👑 Добавлен root admin как первый партнер (0*) с ID 0000001'))
                else:
                    self.stdout.write('👑 Root admin партнер уже существует — пропускаем')

                self.stdout.write(
                    self.style.SUCCESS('✅ Автоматическая инициализация завершена!')
                )
                self.stdout.write("🌐 Система готова к работе!")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при инициализации: {str(e)}')
            )

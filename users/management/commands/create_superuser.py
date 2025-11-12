from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from mlm.models import MLMStructure, MLMPartner
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает суперпользователя (root admin) для API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Имя пользователя (по умолчанию: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@trinary-mlm.com',
            help='Email адрес (по умолчанию: admin@trinary-mlm.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Пароль (по умолчанию: admin123)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Пересоздать суперпользователя, если он уже существует'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        force = options['force']
        
        with transaction.atomic():
            existing_user = User.objects.filter(username=username).first()
            
            if existing_user:
                if force:
                    # Обновляем существующего пользователя до суперпользователя
                    existing_user.is_superuser = True
                    existing_user.is_staff = True
                    existing_user.email = email
                    existing_user.set_password(password)
                    existing_user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Суперпользователь {username} обновлён!')
                    )
                    user = existing_user
                else:
                    if existing_user.is_superuser:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ Суперпользователь {username} уже существует')
                        )
                    else:
                        # Делаем существующего пользователя суперпользователем
                        existing_user.is_superuser = True
                        existing_user.is_staff = True
                        existing_user.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Пользователь {username} повышен до суперпользователя!')
                        )
                    user = existing_user
                
                # Создаем MLM структуру для существующего пользователя, если нужно
                try:
                    mlm_structure, created = MLMStructure.objects.get_or_create(
                        user=user,
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
                    
                    # Создаем MLMPartner для root admin, если его еще нет
                    mlm_partner, partner_created = MLMPartner.objects.get_or_create(
                        root_user=user,
                        unique_id='0000001',
                        defaults={
                            'human_name': 'Admin',
                            'level': 0,
                            'position_x': 0,
                            'position_y': 240,
                            'parent': None,
                            'created_at': timezone.now(),
                            'is_active': True,
                        }
                    )
                    if partner_created:
                        self.stdout.write(
                            self.style.SUCCESS('👑 Root admin добавлен как первый партнер (0*) с ID 0000001')
                        )
                    else:
                        self.stdout.write('👑 Root admin партнер уже существует')
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Не удалось создать MLM структуру: {str(e)}')
                    )
            else:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Суперпользователь {username} создан успешно!')
                )
                self.stdout.write(f'   Логин: {username}')
                self.stdout.write(f'   Пароль: {password}')
                self.stdout.write(f'   Email: {email}')
                
                # Создаем MLM структуру для root admin
                try:
                    mlm_structure, created = MLMStructure.objects.get_or_create(
                        user=user,
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
                    
                    # Создаем MLMPartner для root admin, если его еще нет
                    mlm_partner, partner_created = MLMPartner.objects.get_or_create(
                        root_user=user,
                        unique_id='0000001',
                        defaults={
                            'human_name': 'Admin',
                            'level': 0,
                            'position_x': 0,
                            'position_y': 240,
                            'parent': None,
                            'created_at': timezone.now(),
                            'is_active': True,
                        }
                    )
                    if partner_created:
                        self.stdout.write(
                            self.style.SUCCESS('👑 Root admin добавлен как первый партнер (0*) с ID 0000001')
                        )
                    else:
                        self.stdout.write('👑 Root admin партнер уже существует')
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Не удалось создать MLM структуру: {str(e)}')
                    )
                    import traceback
                    self.stdout.write(traceback.format_exc())

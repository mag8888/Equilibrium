from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

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
            else:
                User.objects.create_superuser(
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

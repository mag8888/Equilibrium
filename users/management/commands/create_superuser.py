from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает суперпользователя для API'

    def handle(self, *args, **options):
        with transaction.atomic():
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@trinary-mlm.com',
                    password='admin123'
                )
                self.stdout.write(
                    self.style.SUCCESS('Суперпользователь admin создан успешно!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Суперпользователь admin уже существует')
                )

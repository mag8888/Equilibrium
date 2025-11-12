from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Автоматическая инициализация системы Equilibrium MLM'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Автоматическая инициализация Equilibrium MLM...")
        
        try:
            with transaction.atomic():
                # Создаем root admin как первого пользователя
                from mlm.models import StructureNode, Tariff
                
                root_admin, created = User.objects.get_or_create(
                    username='admin',
                    defaults={
                        'email': 'admin@example.com',
                        'is_superuser': True,
                        'is_staff': True,
                        'status': User.Status.ADMIN,
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
                        root_admin.status = User.Status.ADMIN
                        root_admin.save()
                        self.stdout.write(
                            self.style.SUCCESS('✅ Пользователь admin повышен до root admin')
                        )
                    else:
                        self.stdout.write('✅ Root admin уже существует')

                # Создаем StructureNode для root admin
                structure_node, node_created = StructureNode.objects.get_or_create(
                    user=root_admin,
                    defaults={
                        'parent': None,
                        'position': 1,
                        'level': 0,
                    }
                )
                if node_created:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Создана MLM структура для root admin')
                    )
                else:
                    # Убеждаемся, что root admin - корень структуры
                    if structure_node.parent is not None or structure_node.level != 0:
                        structure_node.parent = None
                        structure_node.level = 0
                        structure_node.position = 1
                        structure_node.save()
                        self.stdout.write(
                            self.style.SUCCESS('✅ MLM структура root admin обновлена')
                        )

                # Создаем тарифы если их нет
                if not Tariff.objects.exists():
                    Tariff.objects.create(
                        code='starter',
                        name='Starter',
                        entry_amount=100.00,
                        green_bonus_percent=50.00,
                        yellow_bonus_percent=50.00,
                        is_active=True
                    )
                    self.stdout.write(
                        self.style.SUCCESS('✅ Созданы тарифы MLM')
                    )
                else:
                    self.stdout.write('✅ Тарифы MLM уже существуют')

                self.stdout.write(
                    self.style.SUCCESS('✅ Автоматическая инициализация завершена!')
                )
                self.stdout.write("🌐 Система готова к работе!")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при инициализации: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())


from django.db import transaction, models
from decimal import Decimal
from .models import User, PartnerStructure, Bonus


class MLMService:
    """Сервис для управления MLM логикой"""
    
    @staticmethod
    def register_user(username, email, first_name, last_name, referral_code=None):
        """Регистрация нового пользователя"""
        with transaction.atomic():
            # Находим пригласившего по реферальному коду
            inviter = None
            if referral_code:
                try:
                    inviter = User.objects.get(referral_code=referral_code)
                except User.DoesNotExist:
                    pass
            
            # Создаем пользователя
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                inviter=inviter,
                status='participant',
                rank=0
            )
            
            # Создаем структуру партнера
            PartnerStructure.objects.create(
                user=user,
                parent=inviter,
                level=inviter.structure.level + 1 if inviter else 0,
                position=0
            )
            
            return user
    
    @staticmethod
    def process_payment(user, amount):
        """Обработка платежа и изменение статуса"""
        with transaction.atomic():
            # Создаем платеж
            from payments.models import Payment
            payment = Payment.objects.create(
                user=user,
                amount=amount,
                status='completed'
            )
            
            # Обновляем статус пользователя
            user.status = 'partner'
            user.balance += amount
            user.total_purchases += amount
            user.save()
            
            # Распределяем партнера в структуру
            MLMService._distribute_partner(user)
            
            return payment
    
    @staticmethod
    def _distribute_partner(new_partner):
        """Распределение нового партнера в структуру"""
        with transaction.atomic():
            # Находим первого свободного места в структуре
            parent = MLMService._find_available_parent()
            
            if parent:
                # Обновляем структуру
                structure = new_partner.structure
                structure.parent = parent
                structure.level = parent.structure.level + 1
                structure.position = MLMService._get_next_position(parent)
                structure.save()
                
                # Обновляем статистику родителя
                parent.structure.children_count += 1
                parent.structure.total_children += 1
                parent.structure.save()
                
                # Обновляем статистику партнеров по уровням
                MLMService._update_partner_stats(parent)
                
                # Выплачиваем бонусы
                MLMService._pay_bonuses(new_partner, parent)
    
    @staticmethod
    def _find_available_parent():
        """Находит первого доступного родителя для нового партнера"""
        # Ищем пользователей с наименьшим количеством партнеров в первой линии
        users = User.objects.filter(
            status='partner',
            structure__children_count__lt=3
        ).order_by('structure__children_count', 'id')
        
        if users.exists():
            return users.first()
        return None
    
    @staticmethod
    def _get_next_position(parent):
        """Получает следующую позицию для партнера"""
        existing_children = PartnerStructure.objects.filter(
            parent=parent
        ).count()
        return existing_children
    
    @staticmethod
    def _update_partner_stats(user):
        """Обновляет статистику партнеров по уровням"""
        # Подсчитываем партнеров по уровням
        level_1 = PartnerStructure.objects.filter(parent=user).count()
        level_2 = PartnerStructure.objects.filter(
            parent__in=PartnerStructure.objects.filter(parent=user).values_list('user', flat=True)
        ).count()
        level_3 = PartnerStructure.objects.filter(
            parent__in=PartnerStructure.objects.filter(
                parent__in=PartnerStructure.objects.filter(parent=user).values_list('user', flat=True)
            ).values_list('user', flat=True)
        ).count()
        
        # Обновляем статистику
        user.partners_level_1 = level_1
        user.partners_level_2 = level_2
        user.partners_level_3 = level_3
        user.save()
        
        # Проверяем повышение ранга
        if level_1 >= 3 and user.rank == 0:
            MLMService._promote_user(user)
    
    @staticmethod
    def _promote_user(user):
        """Повышает ранг пользователя"""
        user.rank += 1
        user.save()
        
        # Создаем бонус за повышение ранга
        Bonus.objects.create(
            user=user,
            bonus_type='level_up',
            amount=Decimal('100.00'),
            description=f'Повышение до ранга {user.rank}'
        )
    
    @staticmethod
    def _pay_bonuses(new_partner, parent):
        """Выплачивает бонусы за привлечение партнера"""
        # Зеленый бонус наставнику (100$ за первого, 50$ за второго, 0$ за третьего)
        children_count = parent.structure.children_count
        if children_count == 1:
            green_bonus = Decimal('100.00')
        elif children_count == 2:
            green_bonus = Decimal('50.00')
        else:
            green_bonus = Decimal('0.00')
        
        if green_bonus > 0:
            Bonus.objects.create(
                user=parent,
                bonus_type='green',
                amount=green_bonus,
                from_user=new_partner,
                description=f'Зеленый бонус за {children_count}-го партнера'
            )
            parent.balance += green_bonus
            parent.total_rewards += green_bonus
            parent.save()
        
        # Красный бонус участнику (50$ за второго, 100$ за третьего)
        if children_count == 2:
            red_bonus = Decimal('50.00')
        elif children_count == 3:
            red_bonus = Decimal('100.00')
        else:
            red_bonus = Decimal('0.00')
        
        if red_bonus > 0:
            Bonus.objects.create(
                user=new_partner,
                bonus_type='red',
                amount=red_bonus,
                from_user=parent,
                description=f'Красный бонус за {children_count}-го партнера'
            )
            new_partner.balance += red_bonus
            new_partner.total_rewards += red_bonus
            new_partner.save()
    
    @staticmethod
    def get_user_stats():
        """Получает общую статистику системы"""
        total_users = User.objects.count()
        users_with_balance = User.objects.filter(balance__gt=0).count()
        partners = User.objects.filter(status='partner').count()
        total_balance = User.objects.aggregate(
            total=models.Sum('balance')
        )['total'] or Decimal('0.00')
        total_purchases = User.objects.aggregate(
            total=models.Sum('total_purchases')
        )['total'] or Decimal('0.00')
        
        return {
            'total_users': total_users,
            'users_with_balance': users_with_balance,
            'partners': partners,
            'total_balance': total_balance,
            'total_purchases': total_purchases
        }

from django.db import transaction
from django.utils import timezone
from .models import MLMStructure, Bonus, MLMSettings, RankUpgrade
from users.models import User


def place_user_in_structure(new_user, inviter):
    """Размещение нового пользователя в структуре"""
    
    with transaction.atomic():
        # Поиск места для размещения
        placement_user = find_placement_position(inviter)
        
        if placement_user:
            # Создание записи в структуре
            mlm_structure = MLMStructure.objects.create(
                user=new_user,
                parent=placement_user,
                position=get_next_position(placement_user),
                level=placement_user.mlm_structure.level + 1 if hasattr(placement_user, 'mlm_structure') else 1
            )
            
            return mlm_structure
        else:
            # Если не найден подходящий родитель, размещаем под пригласившим
            mlm_structure = MLMStructure.objects.create(
                user=new_user,
                parent=inviter,
                position=get_next_position(inviter),
                level=inviter.mlm_structure.level + 1 if hasattr(inviter, 'mlm_structure') else 1
            )
            
            return mlm_structure


def find_placement_position(start_user):
    """Поиск позиции для размещения нового пользователя"""
    
    # Алгоритм: ищем пользователя с наименьшим количеством партнеров
    # При равном количестве выбираем того, кто раньше зарегистрировался
    
    current_user = start_user
    visited_users = set()
    
    while current_user and current_user.id not in visited_users:
        visited_users.add(current_user.id)
        
        # Получаем количество партнеров у текущего пользователя
        partners_count = MLMStructure.objects.filter(parent=current_user).count()
        
        # Если у пользователя меньше 3 партнеров, размещаем под ним
        if partners_count < 3:
            return current_user
        
        # Ищем среди партнеров того, у кого меньше всего партнеров
        children = MLMStructure.objects.filter(parent=current_user).order_by('position')
        
        if children.exists():
            # Находим партнера с наименьшим количеством партнеров
            min_partners = float('inf')
            best_child = None
            
            for child in children:
                child_partners_count = MLMStructure.objects.filter(parent=child.user).count()
                if child_partners_count < min_partners:
                    min_partners = child_partners_count
                    best_child = child.user
            
            current_user = best_child
        else:
            break
    
    return current_user


def get_next_position(parent_user):
    """Получение следующей позиции для размещения"""
    existing_positions = MLMStructure.objects.filter(parent=parent_user).values_list('position', flat=True)
    
    for position in range(1, 4):  # Позиции 1, 2, 3
        if position not in existing_positions:
            return position
    
    return 1  # Если все позиции заняты, возвращаем 1


def calculate_bonuses(user, payment):
    """Расчет и начисление бонусов"""
    
    try:
        mlm_settings = MLMSettings.objects.filter(is_active=True).first()
        if not mlm_settings:
            return
        
        # Получаем структуру пользователя
        try:
            mlm_structure = user.mlm_structure
            parent = mlm_structure.parent
        except MLMStructure.DoesNotExist:
            return
        
        if not parent:
            return
        
        # Получаем количество партнеров у родителя
        parent_partners_count = MLMStructure.objects.filter(parent=parent).count()
        
        # Зеленые бонусы
        if parent_partners_count == 1:
            # Первый партнер - зеленый бонус 100$
            green_bonus = Bonus.objects.create(
                user=parent,
                amount=mlm_settings.green_bonus_first,
                bonus_type='green',
                description=f'Зеленый бонус за первого партнера - {user.username}',
                from_user=user,
                level=mlm_structure.level
            )
            
            # Обновляем баланс родителя
            parent.balance += mlm_settings.green_bonus_first
            parent.total_earned += mlm_settings.green_bonus_first
            parent.save()
            
        elif parent_partners_count == 2:
            # Второй партнер - зеленый бонус 50$
            green_bonus = Bonus.objects.create(
                user=parent,
                amount=mlm_settings.green_bonus_second,
                bonus_type='green',
                description=f'Зеленый бонус за второго партнера - {user.username}',
                from_user=user,
                level=mlm_structure.level
            )
            
            # Обновляем баланс родителя
            parent.balance += mlm_settings.green_bonus_second
            parent.total_earned += mlm_settings.green_bonus_second
            parent.save()
        
        # Красный бонус (для 2-го и 3-го партнера)
        if parent_partners_count >= 2:
            # Находим первого партнера для красного бонуса
            first_partner = MLMStructure.objects.filter(parent=parent, position=1).first()
            if first_partner:
                red_bonus = Bonus.objects.create(
                    user=first_partner.user,
                    amount=mlm_settings.red_bonus,
                    bonus_type='red',
                    description=f'Красный бонус за {parent_partners_count}-го партнера - {user.username}',
                    from_user=user,
                    level=mlm_structure.level
                )
                
                # Обновляем баланс первого партнера
                first_partner.user.balance += mlm_settings.red_bonus
                first_partner.user.total_earned += mlm_settings.red_bonus
                first_partner.user.save()
        
        # Проверяем, может ли родитель повысить ранг
        if parent.can_upgrade_rank():
            upgrade_user_rank(parent)
            
    except Exception as e:
        print(f"Ошибка при расчете бонусов: {str(e)}")


def upgrade_user_rank(user):
    """Повышение ранга пользователя"""
    
    with transaction.atomic():
        old_rank = user.rank
        new_rank = old_rank + 1
        
        # Обновляем ранг
        user.rank = new_rank
        user.save()
        
        # Создаем запись о повышении ранга
        RankUpgrade.objects.create(
            user=user,
            from_rank=old_rank,
            to_rank=new_rank,
            upgrade_date=timezone.now()
        )


def get_structure_statistics(user):
    """Получение статистики структуры пользователя"""
    
    def count_users_recursive(current_user, level=0, max_level=5):
        if level >= max_level:
            return 0
        
        children = MLMStructure.objects.filter(parent=current_user)
        count = children.count()
        
        for child in children:
            count += count_users_recursive(child.user, level + 1, max_level)
        
        return count
    
    stats = {
        'direct_referrals': MLMStructure.objects.filter(parent=user).count(),
        'total_structure': count_users_recursive(user),
        'active_partners': MLMStructure.objects.filter(parent=user, user__status='partner').count(),
        'participants': MLMStructure.objects.filter(parent=user, user__status='participant').count(),
    }
    
    return stats


def get_bonus_summary(user):
    """Получение сводки по бонусам пользователя"""
    
    bonuses = Bonus.objects.filter(user=user)
    
    summary = {
        'total_bonuses': bonuses.count(),
        'total_amount': sum(bonus.amount for bonus in bonuses),
        'green_bonuses': bonuses.filter(bonus_type='green').count(),
        'green_amount': sum(bonus.amount for bonus in bonuses.filter(bonus_type='green')),
        'red_bonuses': bonuses.filter(bonus_type='red').count(),
        'red_amount': sum(bonus.amount for bonus in bonuses.filter(bonus_type='red')),
        'unpaid_bonuses': bonuses.filter(is_paid=False).count(),
        'unpaid_amount': sum(bonus.amount for bonus in bonuses.filter(is_paid=False)),
    }
    
    return summary

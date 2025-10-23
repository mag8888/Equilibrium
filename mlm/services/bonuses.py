from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.utils import timezone

from mlm.models import Bonus, MLMSettings, MLMStructure, RankUpgrade
from users.models import User


def _get_active_settings() -> MLMSettings:
    """
    Возвращает активные настройки MLM либо создает значения по умолчанию.
    """
    settings = MLMSettings.objects.filter(is_active=True).first()
    if not settings:
        settings = MLMSettings.objects.create(
            registration_fee=Decimal("100.00"),
            green_bonus_first=Decimal("100.00"),
            green_bonus_second=Decimal("50.00"),
            red_bonus_second_partner=Decimal("50.00"),
            red_bonus_third_partner=Decimal("100.00"),
            max_partners_per_level=3,
            is_active=True,
        )
    return settings


def _credit_user(user: User, amount: Decimal) -> None:
    """
    Пополняет баланс пользователя и обновляет суммарный доход.
    """
    user.balance = (user.balance or Decimal("0.00")) + amount
    user.total_earned = (user.total_earned or Decimal("0.00")) + amount
    user.save(update_fields=["balance", "total_earned"])


def _create_bonus(
    recipient: User,
    amount: Decimal,
    bonus_type: str,
    description: str,
    from_user: Optional[User],
    level: int,
) -> Bonus:
    """
    Создает запись о бонусе и возвращает её.
    """
    return Bonus.objects.create(
        user=recipient,
        amount=amount,
        bonus_type=bonus_type,
        description=description,
        from_user=from_user,
        level=level,
    )


def calculate_bonuses(user: User, payment) -> None:
    """
    Начисляет бонусы пригласителю и их структуре в момент оплаты.
    """
    settings = _get_active_settings()

    try:
        mlm_structure = user.mlm_structure
        parent = mlm_structure.parent
    except MLMStructure.DoesNotExist:
        return

    if not parent:
        return

    children_qs = (
        MLMStructure.objects.filter(parent=parent)
        .select_related("user")
        .order_by("position", "created_at")
    )
    partners_count = children_qs.count()

    level = mlm_structure.level

    if partners_count == 1:
        _create_bonus(
            parent,
            settings.green_bonus_first,
            "green",
            f"Зеленый бонус за первого партнера: {user.username}",
            user,
            level,
        )
        _credit_user(parent, settings.green_bonus_first)

    elif partners_count == 2:
        _create_bonus(
            parent,
            settings.green_bonus_second,
            "green",
            f"Зеленый бонус за второго партнера: {user.username}",
            user,
            level,
        )
        _credit_user(parent, settings.green_bonus_second)

        first_partner = children_qs.first()
        if first_partner:
            _create_bonus(
                first_partner.user,
                settings.red_bonus_second_partner,
                "red",
                f"Красный бонус от партнера {user.username}",
                user,
                level,
            )
            _credit_user(first_partner.user, settings.red_bonus_second_partner)

    elif partners_count == 3:
        first_partner = children_qs.first()
        if first_partner:
            _create_bonus(
                first_partner.user,
                settings.red_bonus_third_partner,
                "red",
                f"Красный бонус за третьего партнера: {user.username}",
                user,
                level,
            )
            _credit_user(first_partner.user, settings.red_bonus_third_partner)

    if parent.can_upgrade_rank():
        upgrade_user_rank(parent)


def upgrade_user_rank(user: User) -> None:
    """
    Повышает ранг пользователя и фиксирует изменение.
    """
    with transaction.atomic():
        old_rank = user.rank
        new_rank = old_rank + 1
        user.rank = new_rank
        user.save(update_fields=["rank"])

        RankUpgrade.objects.create(
            user=user,
            from_rank=old_rank,
            to_rank=new_rank,
            upgrade_date=timezone.now(),
        )

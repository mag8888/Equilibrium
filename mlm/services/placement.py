from collections import deque
from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.utils import timezone

from mlm.models import MLMSettings, MLMStructure
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


def find_placement_parent(start_user: User) -> Optional[User]:
    """
    Поиск лучшего родителя для нового пользователя.
    Стратегия: обходим структуру в ширину, выбираем кандидата с минимальным
    количеством партнеров, сохраняя очередность слева направо.
    """
    settings = _get_active_settings()
    max_partners = settings.max_partners_per_level or 3

    # Если у пригласителя ещё нет структуры — он становится корнем.
    if not hasattr(start_user, "mlm_structure"):
        return start_user

    visited = set()
    queue = deque([start_user])
    best_candidate = None
    best_children_count = None

    while queue:
        current_user = queue.popleft()
        if current_user.id in visited:
            continue
        visited.add(current_user.id)

        # Получаем структуру текущего пользователя, пропускаем если её нет.
        try:
            current_structure = current_user.mlm_structure
        except MLMStructure.DoesNotExist:
            continue

        children_qs = (
            MLMStructure.objects.filter(parent=current_user)
            .select_related("user")
            .order_by("position", "created_at")
        )
        children_count = children_qs.count()

        if children_count < max_partners:
            if (
                best_candidate is None
                or children_count < best_children_count
                or (
                    children_count == best_children_count
                    and current_structure.created_at < best_candidate.mlm_structure.created_at
                )
            ):
                best_candidate = current_user
                best_children_count = children_count

        # Добавляем детей в очередь для обхода следующего уровня.
        for child_structure in children_qs:
            queue.append(child_structure.user)

    return best_candidate or start_user


# Обратная совместимость со старым названием.
find_placement_position = find_placement_parent


def get_next_position(parent_user: User) -> int:
    """
    Возвращает следующую позицию (1..max_partners) для дочернего элемента.
    """
    settings = _get_active_settings()
    max_partners = settings.max_partners_per_level or 3
    existing_positions = set(
        MLMStructure.objects.filter(parent=parent_user).values_list("position", flat=True)
    )

    for position in range(1, max_partners + 1):
        if position not in existing_positions:
            return position

    return max(1, max_partners)


def place_user_in_structure(new_user: User, inviter: Optional[User]) -> MLMStructure:
    """
    Размещает нового пользователя в структуре согласно правилам spillover.
    """
    if not inviter:
        raise ValueError("Inviter is required for structure placement")

    with transaction.atomic():
        parent_user = find_placement_parent(inviter) or inviter

        try:
            parent_structure = parent_user.mlm_structure
        except MLMStructure.DoesNotExist:
            parent_structure = None

        level = (parent_structure.level + 1) if parent_structure else 1

        placement = MLMStructure.objects.create(
            user=new_user,
            parent=parent_user,
            position=get_next_position(parent_user),
            level=level,
            created_at=timezone.now(),
        )

        return placement

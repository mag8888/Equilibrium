from collections import deque
from decimal import Decimal
from typing import Optional

from django.conf import settings
from django.db import transaction

from core.models import User
from mlm.models import StructureNode, Tariff


def get_active_tariff(code: str | None = None) -> Tariff:
    qs = Tariff.objects.filter(is_active=True).order_by('entry_amount')
    if code:
        return qs.get(code=code)
    return qs.first()


def get_next_position(parent: User, max_partners: int = 3) -> int:
    occupied = (
        StructureNode.objects.filter(parent=parent)
        .values_list('position', flat=True)
    )
    for idx in range(1, max_partners + 1):
        if idx not in occupied:
            return idx
    return max_partners


def find_parent_for_new_partner(inviter: User, max_partners: int = 3) -> User:
    queue = deque([inviter])
    visited: set[int] = set()
    while queue:
        candidate = queue.popleft()
        if candidate.id in visited:
            continue
        visited.add(candidate.id)

        children_count = StructureNode.objects.filter(parent=candidate).count()
        if children_count < max_partners:
            return candidate

        descendants = (
            StructureNode.objects.filter(parent=candidate)
            .select_related('user')
            .order_by('created_at')
        )
        for node in descendants:
            queue.append(node.user)
    return inviter


def place_user(inviter: User, new_user: User, tariff: Tariff, max_partners: int = 3) -> StructureNode:
    with transaction.atomic():
        parent_user = find_parent_for_new_partner(inviter, max_partners=max_partners)
        parent_node = StructureNode.objects.filter(user=parent_user).first()
        level = (parent_node.level + 1) if parent_node else 0
        position = get_next_position(parent_user, max_partners)
        node, _ = StructureNode.objects.update_or_create(
            user=new_user,
            defaults={
                'parent': parent_user,
                'position': position,
                'level': level,
                'tariff': tariff,
            }
        )
        return node

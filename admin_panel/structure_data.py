from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from django.utils import timezone

from users.models import User
from mlm.models import MLMStructure


@dataclass
class StructureDataset:
    cards: List[Dict]
    child_map: List[Tuple[str, List[str]]]
    uid_counter: int


@dataclass
class StructureStats:
    root: Optional[Dict]
    levels: List[Dict]
    totals: Dict
    generated_at: str


def _resolve_root_user(structures: List[MLMStructure]) -> Optional[User]:
    """Выбор корневого пользователя для визуализации."""
    for node in structures:
        if node.parent_id is None:
            return node.user
    return (
        User.objects.filter(is_superuser=True).first()
        or User.objects.filter(is_staff=True).first()
        or User.objects.first()
    )


def _build_children_map(structures: List[MLMStructure]) -> Dict[int, List[int]]:
    children: Dict[int, List[int]] = defaultdict(list)
    for node in structures:
        if node.parent_id:
            children[node.parent_id].append(node.user_id)
    return children


def _build_descendants_counter(children_map: Dict[int, List[int]]):
    cache: Dict[int, int] = {}

    def _count(user_id: int) -> int:
        if user_id in cache:
            return cache[user_id]
        total = 0
        for child_id in children_map.get(user_id, []):
            total += 1 + _count(child_id)
        cache[user_id] = total
        return total

    return _count, cache


def _build_level_calculator(children_map: Dict[int, List[int]]):
    cache: Dict[int, int] = {}

    def _calculate(user_id: int) -> int:
        if user_id in cache:
            return cache[user_id]

        child_ids = children_map.get(user_id, [])
        if len(child_ids) < 3:
            cache[user_id] = 0
            return 0

        child_levels = [_calculate(child_id) for child_id in child_ids]

        level = 0
        while sum(1 for child_level in child_levels if child_level >= level) >= 3:
            level += 1

        cache[user_id] = level
        return level

    return _calculate, cache


def build_structure_dataset(
    root_user: Optional[User] = None,
) -> Tuple[StructureDataset, StructureStats]:
    """
    Собирает данные структуры и статистику на основе MLMStructure.
    """

    structures = list(
        MLMStructure.objects.select_related("user", "parent").order_by(
            "level", "position", "created_at"
        )
    )

    if not root_user:
        root_user = _resolve_root_user(structures)

    children_map = _build_children_map(structures)
    count_descendants, descendants_cache = _build_descendants_counter(children_map)
    calculate_level, levels_cache = _build_level_calculator(children_map)

    # Посчитаем для всех пользователей, чтобы кэши были заполнены
    for node in structures:
        count_descendants(node.user_id)
        calculate_level(node.user_id)
    if root_user:
        count_descendants(root_user.id)
        calculate_level(root_user.id)

    user_card_ids: Dict[int, str] = {}
    if root_user:
        user_card_ids[root_user.id] = "root"

    cards: List[Dict] = []
    child_map_for_front: Dict[str, List[str]] = defaultdict(list)
    level_offsets: Dict[int, int] = defaultdict(int)
    statuses: Dict[int, str] = {}

    def _card_id(user_id: int) -> str:
        if user_id in user_card_ids:
            return user_card_ids[user_id]
        if root_user and user_id == root_user.id:
            user_card_ids[user_id] = "root"
        else:
            user_card_ids[user_id] = f"user-{user_id}"
        return user_card_ids[user_id]

    for node in structures:
        statuses[node.user_id] = node.user.status
        card_id = _card_id(node.user_id)
        parent_id = _card_id(node.parent_id) if node.parent_id else None
        idx = level_offsets[node.level]
        level_offsets[node.level] += 1

        direct_referrals = len(children_map.get(node.user_id, []))
        total_referrals = descendants_cache.get(node.user_id, 0)
        computed_level = levels_cache.get(node.user_id, node.level or 0)

        cards.append(
            {
                "id": card_id,
                "parent": parent_id,
                "name": (node.user.get_full_name() or "").strip()
                or node.user.username,
                "uid": node.user.referral_code
                or f"{node.user.id:07d}",
                "username": node.user.username,
                "level": computed_level,
                "displayLevel": computed_level,
                "left": 400 + node.level * 320,
                "top": 200 + idx * 200,
                "status": node.user.status,
                "rank": node.user.rank,
                "directReferrals": direct_referrals,
                "totalReferrals": total_referrals,
                "directInvites": direct_referrals,
            }
        )
        if parent_id:
            child_map_for_front[parent_id].append(card_id)

    if root_user and all(card["id"] != "root" for card in cards):
        root_level = levels_cache.get(root_user.id, 0)
        root_direct = len(children_map.get(root_user.id, []))
        root_total = descendants_cache.get(root_user.id, 0)
        cards.insert(
            0,
            {
                "id": "root",
                "parent": None,
                "name": (root_user.get_full_name() or "").strip()
                or root_user.username,
                "uid": root_user.referral_code
                or f"{root_user.id:07d}",
                "username": root_user.username,
                "level": root_level,
                "displayLevel": root_level,
                "left": 2400,
                "top": 200,
                "status": root_user.status,
                "rank": root_user.rank,
                "directReferrals": root_direct,
                "totalReferrals": root_total,
                "directInvites": root_direct,
            },
        )

    dataset = StructureDataset(
        cards=cards,
        child_map=[
            (parent, children) for parent, children in child_map_for_front.items()
        ],
        uid_counter=len(cards) + 5,
    )

    level_stats: Dict[int, Dict[str, int]] = defaultdict(
        lambda: {"total": 0, "partners": 0, "participants": 0}
    )
    total_partners = 0
    total_participants = 0
    for node in structures:
        computed_level = levels_cache.get(node.user_id, node.level or 0)
        level_entry = level_stats[computed_level]
        level_entry["total"] += 1
        if node.user.status == "partner":
            level_entry["partners"] += 1
            total_partners += 1
        elif node.user.status == "participant":
            level_entry["participants"] += 1
            total_participants += 1

    formatted_levels = [
        {"level": level, **stats}
        for level, stats in sorted(level_stats.items(), key=lambda item: item[0])
    ]

    root_stats = None
    if root_user:
        root_stats = {
            "name": (root_user.get_full_name() or "").strip() or root_user.username,
            "username": root_user.username,
            "rank": root_user.rank,
            "level": levels_cache.get(root_user.id, 0),
            "direct_referrals": len(children_map.get(root_user.id, [])),
            "partners_on_first_line": sum(
                1
                for child_id in children_map.get(root_user.id, [])
                if statuses.get(child_id) == "partner"
            ),
            "participants_on_first_line": sum(
                1
                for child_id in children_map.get(root_user.id, [])
                if statuses.get(child_id) == "participant"
            ),
            "total_descendants": descendants_cache.get(root_user.id, 0),
        }

    stats = StructureStats(
        root=root_stats,
        levels=formatted_levels,
        totals={
            "nodes": len(structures),
            "partners": total_partners,
            "participants": total_participants,
            "max_depth": max(
                (levels_cache.get(node.user_id, node.level or 0) for node in structures),
                default=0,
            ),
        },
        generated_at=timezone.now().isoformat(),
    )

    return dataset, stats

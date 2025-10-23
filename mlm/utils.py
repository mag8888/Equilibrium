"""
Legacy helpers retained for backwards compatibility.
Реализации перенесены в модуль services.
"""

from mlm.services import (  # noqa: F401
    calculate_bonuses,
    find_placement_parent,
    find_placement_position,
    get_bonus_summary,
    get_next_position,
    get_structure_statistics,
    place_user_in_structure,
    upgrade_user_rank,
)

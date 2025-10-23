from decimal import Decimal

from mlm.models import Bonus, MLMStructure


def get_structure_statistics(user):
    """
    Возвращает статистику структуры пользователя.
    """

    def _count_recursive(current_user, level=0, max_depth=5):
        if level >= max_depth:
            return 0

        children = MLMStructure.objects.filter(parent=current_user)
        count = children.count()

        for child in children:
            count += _count_recursive(child.user, level + 1, max_depth)

        return count

    return {
        "direct_referrals": MLMStructure.objects.filter(parent=user).count(),
        "total_structure": _count_recursive(user),
        "active_partners": MLMStructure.objects.filter(
            parent=user, user__status="partner"
        ).count(),
        "participants": MLMStructure.objects.filter(
            parent=user, user__status="participant"
        ).count(),
    }


def get_bonus_summary(user):
    """
    Возвращает агрегированные данные по бонусам пользователя.
    """
    bonuses = Bonus.objects.filter(user=user)

    def _sum(queryset):
        total = Decimal("0.00")
        for bonus in queryset:
            total += bonus.amount
        return total

    green_bonuses = bonuses.filter(bonus_type="green")
    red_bonuses = bonuses.filter(bonus_type="red")
    unpaid_bonuses = bonuses.filter(is_paid=False)

    return {
        "total_bonuses": bonuses.count(),
        "total_amount": _sum(bonuses),
        "green_bonuses": green_bonuses.count(),
        "green_amount": _sum(green_bonuses),
        "red_bonuses": red_bonuses.count(),
        "red_amount": _sum(red_bonuses),
        "unpaid_bonuses": unpaid_bonuses.count(),
        "unpaid_amount": _sum(unpaid_bonuses),
    }

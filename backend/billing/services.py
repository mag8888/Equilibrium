from decimal import Decimal
from typing import Tuple

from django.db import transaction

from core.models import User
from billing.models import Payment, Bonus
from mlm.models import StructureNode, Tariff


def calculate_bonus_amounts(tariff: Tariff) -> Tuple[Decimal, Decimal]:
    green = tariff.entry_amount * (Decimal(tariff.green_bonus_percent) / Decimal(100))
    yellow = tariff.entry_amount * (Decimal(tariff.yellow_bonus_percent) / Decimal(100))
    return green.quantize(Decimal('0.01')), yellow.quantize(Decimal('0.01'))


@transaction.atomic
def apply_signup_bonuses(payment: Payment, placement: StructureNode) -> None:
    user = payment.user
    inviter = user.invited_by
    tariff = placement.tariff or payment.tariff
    green_amount, yellow_amount = calculate_bonus_amounts(tariff)

    if inviter and green_amount > 0:
        Bonus.objects.create(
            user=inviter,
            source_user=user,
            payment=payment,
            bonus_type=Bonus.Type.GREEN,
            amount=green_amount,
            description=f"Invite bonus from {user.username}",
        )

    parent_owner = placement.parent
    if parent_owner and yellow_amount > 0:
        Bonus.objects.create(
            user=parent_owner,
            source_user=user,
            payment=payment,
            bonus_type=Bonus.Type.YELLOW,
            amount=yellow_amount,
            description=f"Transition bonus from {user.username}",
        )

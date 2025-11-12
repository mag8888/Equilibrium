import secrets
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


def generate_referral_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class User(AbstractUser):
    class Status(models.TextChoices):
        PARTICIPANT = "participant", _("Participant")
        PARTNER = "partner", _("Partner")
        ADMIN = "admin", _("Administrator")

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PARTICIPANT,
    )
    referral_code = models.CharField(max_length=16, unique=True, blank=True)
    invited_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="invited_partners",
    )
    is_active_mlm = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            # Ensure uniqueness by regenerating until unused.
            code = generate_referral_code()
            while User.objects.filter(referral_code=code).exists():
                code = generate_referral_code()
            self.referral_code = code
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.username} ({self.status})"

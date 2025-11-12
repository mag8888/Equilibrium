from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Tariff(models.Model):
    code = models.SlugField(max_length=32, unique=True)
    name = models.CharField(max_length=100)
    entry_amount = models.DecimalField(max_digits=10, decimal_places=2)
    green_bonus_percent = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    yellow_bonus_percent = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["entry_amount"]

    def __str__(self) -> str:
        return f"{self.name} (${self.entry_amount})"


class StructureNode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="structure_node")
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="children_nodes")
    position = models.PositiveSmallIntegerField(default=1)
    level = models.PositiveIntegerField(default=0)
    tariff = models.ForeignKey(Tariff, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["level", "created_at"]
        unique_together = (
            ("parent", "position"),
        )

    def __str__(self) -> str:
        return f"{self.user} (lvl {self.level})"

    @property
    def children(self):
        return type(self).objects.filter(parent=self.user).order_by("position")

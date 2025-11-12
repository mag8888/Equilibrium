from django.contrib import admin

from billing.models import Payment, Bonus


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tariff", "amount", "status", "created_at", "completed_at")
    list_filter = ("status", "tariff")
    search_fields = ("user__username", "external_id")


@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "bonus_type", "amount", "source_user", "created_at")
    list_filter = ("bonus_type",)
    search_fields = ("user__username", "source_user__username")

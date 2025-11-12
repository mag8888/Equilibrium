from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from core.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('MLM data', {'fields': ('status', 'referral_code', 'invited_by', 'is_active_mlm')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('MLM data', {'fields': ('status', 'invited_by', 'is_active_mlm')}),
    )
    list_display = ('username', 'email', 'status', 'referral_code', 'invited_by')
    list_filter = ('status', 'is_active_mlm')
    search_fields = ('username', 'email', 'referral_code')

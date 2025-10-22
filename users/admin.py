from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, PartnerStructure, Bonus


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'checkbox_column', 'balance_display', 'orders_display', 'inviter_display',
        'user_display', 'partners_level_1', 'partners_level_2', 'partners_level_3',
        'total_purchases', 'total_rewards', 'total_payouts', 'remaining_payout', 'user_actions'
    ]
    list_filter = ['status', 'rank', 'is_active', 'created_at']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'referral_code']
    readonly_fields = ['referral_code', 'created_at', 'updated_at', 'last_login']
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'is_active')
        }),
        ('MLM статус', {
            'fields': ('status', 'rank', 'balance')
        }),
        ('Реферальная система', {
            'fields': ('inviter', 'referral_code')
        }),
        ('Статистика партнеров', {
            'fields': ('partners_level_1', 'partners_level_2', 'partners_level_3')
        }),
        ('Финансовая статистика', {
            'fields': ('total_purchases', 'total_rewards', 'total_payouts', 'remaining_payout')
        }),
        ('Метаданные', {
            'fields': ('date_joined', 'last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def checkbox_column(self, obj):
        return format_html(
            '<input type="checkbox" name="selected_users" value="{}" />',
            obj.id
        )
    checkbox_column.short_description = ''
    checkbox_column.allow_tags = True
    
    def balance_display(self, obj):
        color = 'green' if obj.balance > 0 else 'black'
        return format_html(
            '<span style="color: {};">{:.2f} PZ</span>',
            color, obj.balance
        )
    balance_display.short_description = 'Баланс'
    
    def orders_display(self, obj):
        return format_html(
            '{:.2f} PZ {} шт',
            obj.total_purchases, obj.partners_level_1 + obj.partners_level_2 + obj.partners_level_3
        )
    orders_display.short_description = 'Заказы'
    
    def inviter_display(self, obj):
        if obj.inviter:
            return f"@{obj.inviter.username}"
        return "-"
    inviter_display.short_description = 'Пригласитель'
    
    def user_display(self, obj):
        avatar = obj.first_name[0].upper() if obj.first_name else obj.username[0].upper()
        return format_html(
            '<div style="display: flex; align-items: center;">'
            '<div style="width: 30px; height: 30px; border-radius: 50%; background-color: #007bff; '
            'color: white; display: flex; align-items: center; justify-content: center; margin-right: 10px; '
            'font-weight: bold;">{}</div>'
            '{} @{}',
            avatar, obj.get_full_name(), obj.username
        )
    user_display.short_description = 'Пользователь'
    
    def user_actions(self, obj):
        return format_html(
            '<a href="{}" class="button" style="background: green; color: white; padding: 5px 10px; '
            'text-decoration: none; border-radius: 3px; margin-right: 5px;">📄</a>'
            '<a href="{}" class="button" style="background: blue; color: white; padding: 5px 10px; '
            'text-decoration: none; border-radius: 3px; margin-right: 5px;">👁</a>'
            '<a href="{}" class="button" style="background: blue; color: white; padding: 5px 10px; '
            'text-decoration: none; border-radius: 3px;">🔄</a>',
            reverse('admin:users_user_change', args=[obj.id]),
            reverse('admin:users_user_change', args=[obj.id]),
            reverse('admin:users_user_change', args=[obj.id])
        )
    user_actions.short_description = 'Действия'
    user_actions.allow_tags = True


@admin.register(PartnerStructure)
class PartnerStructureAdmin(admin.ModelAdmin):
    list_display = ['user', 'parent', 'level', 'position', 'children_count', 'total_children']
    list_filter = ['level']
    search_fields = ['user__username', 'parent__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = ['user', 'bonus_type', 'amount', 'is_paid', 'created_at']
    list_filter = ['bonus_type', 'is_paid', 'created_at']
    search_fields = ['user__username', 'from_user__username']
    readonly_fields = ['created_at']


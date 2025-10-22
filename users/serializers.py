from rest_framework import serializers
from .models import User, Bonus
from payments.models import Payment


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'status', 'rank', 'balance', 'inviter', 'referral_code',
            'partners_level_1', 'partners_level_2', 'partners_level_3',
            'total_purchases', 'total_rewards', 'total_payouts', 'remaining_payout',
            'is_active', 'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'referral_code', 'partners_level_1', 'partners_level_2', 'partners_level_3',
            'total_purchases', 'total_rewards', 'total_payouts', 'remaining_payout',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]


class BonusSerializer(serializers.ModelSerializer):
    """Сериализатор для бонусов"""
    
    from_user_username = serializers.CharField(source='from_user.username', read_only=True)
    bonus_type_display = serializers.CharField(source='get_bonus_type_display', read_only=True)
    
    class Meta:
        model = Bonus
        fields = [
            'id', 'user', 'bonus_type', 'bonus_type_display', 'amount', 'description',
            'from_user', 'from_user_username', 'is_paid', 'paid_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'amount', 'status', 'status_display', 'payment_method',
            'transaction_id', 'description', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']

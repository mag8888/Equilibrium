from rest_framework import serializers
from users.models import User, UserProfile
from mlm.models import MLMStructure, Payment, Bonus, Withdrawal, MLMSettings


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'status', 'rank', 'total_earned', 'balance', 'is_partner', 'referral_code']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined']


class MLMStructureSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    parent_name = serializers.CharField(source='parent.user.username', read_only=True)
    
    class Meta:
        model = MLMStructure
        fields = ['id', 'user', 'user_name', 'parent', 'parent_name', 'level', 'position', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_name', 'amount', 'status', 'payment_method', 'created_at', 'processed_at']


class BonusSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    from_user_name = serializers.CharField(source='from_user.username', read_only=True)
    
    class Meta:
        model = Bonus
        fields = ['id', 'user', 'user_name', 'from_user', 'from_user_name', 'amount', 'type', 'description', 'created_at']


class WithdrawalSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Withdrawal
        fields = ['id', 'user', 'user_name', 'amount', 'status', 'payment_method', 'created_at', 'processed_at']


class MLMSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLMSettings
        fields = ['partner_upgrade_amount', 'green_bonus_percent', 'red_bonus_percent', 'max_levels']

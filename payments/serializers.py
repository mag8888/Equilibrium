from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_username', 'amount', 'status', 'status_display',
            'payment_method', 'transaction_id', 'description', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']

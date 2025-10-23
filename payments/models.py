from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class PaymentMethod(models.Model):
    """Модель для способов оплаты"""
    
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    commission_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Настройки для разных способов оплаты
    settings = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Способ оплаты'
        verbose_name_plural = 'Способы оплаты'


class PaymentGateway(models.Model):
    """Модель для платежных шлюзов"""
    
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    api_url = models.URLField()
    api_key = models.CharField(max_length=200)
    secret_key = models.CharField(max_length=200)
    
    # Настройки
    settings = models.JSONField(default=dict, blank=True)
    webhook_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Платежный шлюз'
        verbose_name_plural = 'Платежные шлюзы'
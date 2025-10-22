from django.db import models
from users.models import User


class Payment(models.Model):
    """Модель для отслеживания платежей"""
    
    PAYMENT_STATUS = [
        ('pending', 'Ожидает'),
        ('completed', 'Завершен'),
        ('failed', 'Неудачный'),
        ('refunded', 'Возвращен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Детали платежа
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Метаданные
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.get_status_display()}"
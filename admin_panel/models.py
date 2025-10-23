from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AdminAction(models.Model):
    """Модель для отслеживания действий администратора"""
    
    ACTION_TYPES = [
        ('user_create', 'Создание пользователя'),
        ('user_edit', 'Редактирование пользователя'),
        ('user_delete', 'Удаление пользователя'),
        ('payment_approve', 'Одобрение платежа'),
        ('payment_reject', 'Отклонение платежа'),
        ('bonus_create', 'Создание бонуса'),
        ('structure_edit', 'Изменение структуры'),
        ('withdrawal_process', 'Обработка вывода'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='admin_actions_target')
    description = models.TextField()
    details = models.JSONField(default=dict, blank=True)  # Дополнительные детали действия
    
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.get_action_type_display()}"
    
    class Meta:
        verbose_name = 'Действие администратора'
        verbose_name_plural = 'Действия администраторов'
        ordering = ['-created_at']


class SystemNotification(models.Model):
    """Модель для системных уведомлений"""
    
    NOTIFICATION_TYPES = [
        ('info', 'Информация'),
        ('warning', 'Предупреждение'),
        ('error', 'Ошибка'),
        ('success', 'Успех'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    
    # Целевая аудитория
    target_users = models.ManyToManyField(User, blank=True, related_name='notifications')
    is_global = models.BooleanField(default=False)  # Для всех пользователей
    
    # Статус
    is_active = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_notification_type_display()})"
    
    class Meta:
        verbose_name = 'Системное уведомление'
        verbose_name_plural = 'Системные уведомления'
        ordering = ['-created_at']


class SystemStats(models.Model):
    """Модель для хранения статистики системы"""
    
    date = models.DateField(default=timezone.now)
    
    # Статистика пользователей
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    new_registrations = models.IntegerField(default=0)
    
    # Статистика платежей
    total_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    completed_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    pending_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Статистика бонусов
    total_bonuses_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    green_bonuses = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    red_bonuses = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Статистика выводов
    total_withdrawals = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    pending_withdrawals = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Статистика за {self.date}"
    
    class Meta:
        verbose_name = 'Статистика системы'
        verbose_name_plural = 'Статистика системы'
        ordering = ['-date']
        unique_together = ['date']


class AdminSettings(models.Model):
    """Настройки админ-панели"""
    
    # Настройки отображения
    items_per_page = models.IntegerField(default=25)
    show_inactive_users = models.BooleanField(default=False)
    auto_refresh_interval = models.IntegerField(default=30)  # секунды
    
    # Настройки уведомлений
    email_notifications = models.BooleanField(default=True)
    new_user_notification = models.BooleanField(default=True)
    payment_notification = models.BooleanField(default=True)
    withdrawal_notification = models.BooleanField(default=True)
    
    # Настройки безопасности
    session_timeout = models.IntegerField(default=3600)  # секунды
    require_2fa = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Настройки админ-панели"
    
    class Meta:
        verbose_name = 'Настройка админ-панели'
        verbose_name_plural = 'Настройки админ-панели'
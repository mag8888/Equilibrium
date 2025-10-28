from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class MLMStructure(models.Model):
    """Модель для хранения MLM структуры"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mlm_structure')
    parent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    position = models.IntegerField(default=0)  # Позиция в структуре (1, 2, 3)
    level = models.IntegerField(default=0)  # Уровень в структуре
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - Уровень {self.level}, Позиция {self.position}"
    
    class Meta:
        verbose_name = 'MLM структура'
        verbose_name_plural = 'MLM структуры'
        ordering = ['level', 'position']


class Payment(models.Model):
    """Модель для платежей"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('completed', 'Завершен'),
        ('failed', 'Неудачный'),
        ('cancelled', 'Отменен'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('registration', 'Регистрация'),
        ('upgrade', 'Повышение ранга'),
        ('bonus', 'Бонус'),
        ('withdrawal', 'Вывод средств'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    
    # Платежные данные
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Даты
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']


class Bonus(models.Model):
    """Модель для бонусов"""
    
    BONUS_TYPE_CHOICES = [
        ('green', 'Зеленый бонус'),
        ('red', 'Красный бонус'),
        ('spillover', 'Спилловер'),
        ('matching', 'Матчинг бонус'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonuses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_type = models.CharField(max_length=20, choices=BONUS_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Связанные данные
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='bonuses_given')
    level = models.IntegerField(default=0)
    
    # Статус
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.get_bonus_type_display()})"
    
    class Meta:
        verbose_name = 'Бонус'
        verbose_name_plural = 'Бонусы'
        ordering = ['-created_at']


class RankUpgrade(models.Model):
    """Модель для отслеживания повышений ранга"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rank_upgrades')
    from_rank = models.IntegerField()
    to_rank = models.IntegerField()
    upgrade_date = models.DateTimeField(default=timezone.now)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.from_rank} -> {self.to_rank}"
    
    class Meta:
        verbose_name = 'Повышение ранга'
        verbose_name_plural = 'Повышения рангов'
        ordering = ['-upgrade_date']


class MLMSettings(models.Model):
    """Настройки MLM системы"""
    
    # Стоимости уровней
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    
    # Бонусы
    green_bonus_first = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    green_bonus_second = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    red_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    red_bonus_second_partner = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    red_bonus_third_partner = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    
    # Настройки системы
    max_partners_per_level = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"MLM Настройки (активны: {self.is_active})"
    
    class Meta:
        verbose_name = 'Настройка MLM'
        verbose_name_plural = 'Настройки MLM'


class MLMPartner(models.Model):
    """Модель для хранения партнеров в MLM структуре"""
    
    # Основные поля
    unique_id = models.CharField(max_length=7, unique=True, help_text="7-значный уникальный ID")
    human_name = models.CharField(max_length=100, help_text="Человеко-читаемое имя")
    level = models.IntegerField(default=0, help_text="Уровень партнера (0-7)")
    position_x = models.IntegerField(default=0, help_text="X координата на карте")
    position_y = models.IntegerField(default=0, help_text="Y координата на карте")
    
    # Связи
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    root_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mlm_partners')
    
    # Метаданные
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.human_name} ({self.level}*) - ID: {self.unique_id}"
    
    class Meta:
        verbose_name = 'MLM Партнер'
        verbose_name_plural = 'MLM Партнеры'
        ordering = ['level', 'created_at']


class Withdrawal(models.Model):
    """Модель для выводов средств"""
    
    WITHDRAWAL_STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('processing', 'Обрабатывается'),
        ('completed', 'Завершен'),
        ('rejected', 'Отклонен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=WITHDRAWAL_STATUS_CHOICES, default='pending')
    
    # Данные для вывода
    payment_method = models.CharField(max_length=50)
    payment_details = models.TextField()  # JSON с деталями платежа
    
    # Административные поля
    admin_notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_withdrawals')
    
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = 'Вывод средств'
        verbose_name_plural = 'Выводы средств'
        ordering = ['-created_at']

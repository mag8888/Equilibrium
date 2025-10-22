from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Модель пользователя с расширенными полями для MLM системы"""
    
    STATUS_CHOICES = [
        ('participant', 'Участник'),
        ('partner', 'Партнер'),
    ]
    
    RANK_CHOICES = [
        (0, 'Ранг 0'),
        (1, 'ПУ1'),
        (2, 'ПУ2'),
        (3, 'ПУ3'),
        (4, 'ПУ4'),
        (5, 'ПУ5'),
        (6, 'ПУ6'),
        (7, 'ПУ7'),
        (8, 'ПУ8'),
        (9, 'ПУ9'),
        (10, 'ПУ10'),
    ]
    
    # Основные поля
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    
    # MLM поля
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='participant')
    rank = models.IntegerField(choices=RANK_CHOICES, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Реферальная система
    inviter = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    
    # Статистика партнеров
    partners_level_1 = models.IntegerField(default=0)
    partners_level_2 = models.IntegerField(default=0)
    partners_level_3 = models.IntegerField(default=0)
    
    # Финансовая статистика
    total_purchases = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_rewards = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_payouts = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Метаданные
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    
    # Поля для админки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)
    
    def generate_referral_code(self):
        """Генерирует уникальный реферальный код"""
        while True:
            code = str(uuid.uuid4())[:8].upper()
            if not User.objects.filter(referral_code=code).exists():
                return code
    
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_display_name(self):
        """Возвращает отображаемое имя для админки"""
        return f"{self.get_full_name()} @{self.username}"
    
    def __str__(self):
        return self.get_display_name()


class PartnerStructure(models.Model):
    """Модель для отслеживания структуры партнеров"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='structure')
    parent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    level = models.IntegerField(default=0)  # Уровень в структуре (0 = корень)
    position = models.IntegerField(default=0)  # Позиция среди братьев (0, 1, 2)
    
    # Статистика по уровням
    children_count = models.IntegerField(default=0)
    total_children = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Структура партнера'
        verbose_name_plural = 'Структуры партнеров'
        ordering = ['level', 'position']
    
    def __str__(self):
        return f"{self.user.username} - Уровень {self.level}, Позиция {self.position}"


class Bonus(models.Model):
    """Модель для отслеживания бонусов"""
    
    BONUS_TYPES = [
        ('green', 'Зеленый бонус (наставнику)'),
        ('red', 'Красный бонус (участнику)'),
        ('level_up', 'Бонус за повышение ранга'),
        ('referral', 'Реферальный бонус'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonuses')
    bonus_type = models.CharField(max_length=20, choices=BONUS_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    
    # Связанные пользователи
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bonuses_given')
    
    # Статус
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Бонус'
        verbose_name_plural = 'Бонусы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_bonus_type_display()} - {self.amount}"


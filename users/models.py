from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Расширенная модель пользователя для MLM системы"""
    
    STATUS_CHOICES = [
        ('participant', 'Участник'),
        ('partner', 'Партнер'),
        ('inactive', 'Неактивный'),
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
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)
    
    # MLM поля
    referral_code = models.CharField(max_length=10, unique=True, blank=True)
    invited_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='participant')
    rank = models.IntegerField(choices=RANK_CHOICES, default=0)
    
    # Финансовые поля
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Даты
    date_joined = models.DateTimeField(default=timezone.now)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    
    # Административные поля
    is_verified = models.BooleanField(default=False)
    is_active_mlm = models.BooleanField(default=True)
    
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
    
    def get_referral_link(self):
        """Возвращает реферальную ссылку"""
        return f"/register/?ref={self.referral_code}"
    
    def get_partners_count(self):
        """Возвращает количество партнеров в первой линии"""
        return self.referrals.filter(status='partner').count()
    
    def can_upgrade_rank(self):
        """Проверяет, может ли пользователь повысить ранг"""
        return self.get_partners_count() >= 3 and self.status == 'partner'
    
    def __str__(self):
        return f"{self.username} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class UserProfile(models.Model):
    """Дополнительный профиль пользователя"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Дополнительные поля для MLM
    preferred_language = models.CharField(max_length=10, default='ru')
    timezone = models.CharField(max_length=50, default='UTC')
    
    def __str__(self):
        return f"Профиль {self.user.username}"
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
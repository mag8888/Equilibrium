from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from .models import Bonus, Withdrawal, MLMSettings, RankUpgrade
from mlm.services import get_bonus_summary, get_structure_statistics, upgrade_user_rank
from users.models import User


@login_required
def upgrade_rank(request):
    """Повышение ранга пользователя"""
    user = request.user
    
    if not user.can_upgrade_rank():
        messages.error(request, 'У вас недостаточно партнеров для повышения ранга')
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Повышаем ранг
                upgrade_user_rank(user)
                
                messages.success(request, f'Поздравляем! Ваш ранг повышен до {user.get_rank_display()}')
                return redirect('users:dashboard')
                
        except Exception as e:
            messages.error(request, f'Ошибка при повышении ранга: {str(e)}')
    
    return render(request, 'mlm/upgrade_rank.html', {'user': user})


@login_required
def bonuses(request):
    """Страница бонусов пользователя"""
    user = request.user
    
    # Получение всех бонусов
    bonuses_list = Bonus.objects.filter(user=user).order_by('-created_at')
    
    # Сводка по бонусам
    bonus_summary = get_bonus_summary(user)
    
    # Фильтрация
    bonus_type = request.GET.get('type', '')
    if bonus_type:
        bonuses_list = bonuses_list.filter(bonus_type=bonus_type)
    
    context = {
        'bonuses': bonuses_list,
        'summary': bonus_summary,
        'bonus_type': bonus_type,
    }
    
    return render(request, 'mlm/bonuses.html', context)


@login_required
def withdraw(request):
    """Запрос на вывод средств"""
    user = request.user
    
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        payment_method = request.POST.get('payment_method', '')
        payment_details = request.POST.get('payment_details', '')
        
        # Валидация
        if amount <= 0:
            messages.error(request, 'Сумма должна быть больше 0')
            return render(request, 'mlm/withdraw.html')
        
        if amount > user.balance:
            messages.error(request, 'Недостаточно средств на балансе')
            return render(request, 'mlm/withdraw.html')
        
        if not payment_method or not payment_details:
            messages.error(request, 'Заполните все поля')
            return render(request, 'mlm/withdraw.html')
        
        try:
            with transaction.atomic():
                # Создание запроса на вывод
                withdrawal = Withdrawal.objects.create(
                    user=user,
                    amount=amount,
                    payment_method=payment_method,
                    payment_details=payment_details,
                    status='pending'
                )
                
                # Резервируем средства (уменьшаем баланс)
                user.balance -= amount
                user.save()
                
                messages.success(request, f'Запрос на вывод {amount}$ создан и отправлен на рассмотрение')
                return redirect('mlm:withdraw')
                
        except Exception as e:
            messages.error(request, f'Ошибка при создании запроса на вывод: {str(e)}')
    
    # Получение истории выводов
    withdrawals = Withdrawal.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'withdrawals': withdrawals,
    }
    
    return render(request, 'mlm/withdraw.html', context)


@login_required
def payment_history(request):
    """История платежей"""
    user = request.user
    
    # Получение всех платежей пользователя
    payments = user.payments.all().order_by('-created_at')
    
    # Фильтрация
    payment_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    
    if payment_type:
        payments = payments.filter(payment_type=payment_type)
    
    if status:
        payments = payments.filter(status=status)
    
    context = {
        'payments': payments,
        'payment_type': payment_type,
        'status': status,
    }
    
    return render(request, 'mlm/payment_history.html', context)


@login_required
def structure_stats(request):
    """Статистика структуры (API endpoint)"""
    user = request.user
    
    stats = get_structure_statistics(user)
    
    return JsonResponse(stats)


@login_required
def bonus_stats(request):
    """Статистика бонусов (API endpoint)"""
    user = request.user
    
    stats = get_bonus_summary(user)
    
    return JsonResponse(stats)

"""
Демо-версия админ-панели без требования аутентификации
Используется для демонстрации функционала
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum


def admin_demo_dashboard(request):
    """Демо-версия главной страницы админ-панели"""
    
    try:
        from users.models import User
        from mlm.models import Payment, Bonus, Withdrawal
        
        # Общая статистика
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active_mlm=True).count(),
            'participants': User.objects.filter(status='participant').count(),
            'partners': User.objects.filter(status='partner').count(),
            'total_payments': Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
            'pending_payments': Payment.objects.filter(status='pending').count(),
            'total_bonuses': Bonus.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
            'pending_withdrawals': Withdrawal.objects.filter(status='pending').count(),
        }
        
        # Последние действия
        recent_users = User.objects.order_by('-date_joined')[:10]
        recent_payments = Payment.objects.order_by('-created_at')[:10]
        recent_withdrawals = Withdrawal.objects.order_by('-created_at')[:5]
        
    except Exception as e:
        # Если БД недоступна, показываем демо-данные
        stats = {
            'total_users': 42,
            'active_users': 38,
            'participants': 25,
            'partners': 17,
            'total_payments': 4250.00,
            'pending_payments': 3,
            'total_bonuses': 1520.50,
            'pending_withdrawals': 2,
        }
        recent_users = []
        recent_payments = []
        recent_withdrawals = []
    
    context = {
        'stats': stats,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        'recent_withdrawals': recent_withdrawals,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/demo_dashboard.html', context)


def admin_demo_users(request):
    """Демо-версия списка пользователей"""
    
    try:
        from users.models import User
        users = User.objects.all().order_by('-date_joined')[:50]
        total_users = User.objects.count()
        active_partners = User.objects.filter(status='partner').count()
    except Exception as e:
        users = []
        total_users = 42
        active_partners = 17
    
    context = {
        'users': users,
        'total_users': total_users,
        'active_partners': active_partners,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/demo_users.html', context)


def admin_demo_structure(request):
    """Демо-версия структуры"""
    
    try:
        from users.models import User
        # Получаем корневых пользователей
        root_users = User.objects.filter(invited_by__isnull=True).order_by('-date_joined')[:20]
    except Exception as e:
        root_users = []
    
    context = {
        'root_users': root_users,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/demo_structure.html', context)

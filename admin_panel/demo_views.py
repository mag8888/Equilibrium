"""
Демо-версия админ-панели без требования аутентификации
Используется для демонстрации функционала
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse


def admin_demo_dashboard(request):
    """Демо-версия главной страницы админ-панели"""
    
    # Демо-данные (не подключаемся к БД)
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
    
    try:
        from users.models import User
        from mlm.models import Payment, Bonus, Withdrawal
        
        # Пытаемся получить реальные данные
        stats['total_users'] = User.objects.count()
        stats['active_users'] = User.objects.filter(is_active_mlm=True).count()
        stats['participants'] = User.objects.filter(status='participant').count()
        stats['partners'] = User.objects.filter(status='partner').count()
        stats['total_payments'] = Payment.objects.filter(status='completed').aggregate(Sum=__import__('django.db.models', fromlist=['Sum']).Sum('amount'))['Sum'] or 0
        stats['pending_payments'] = Payment.objects.filter(status='pending').count()
        stats['total_bonuses'] = Bonus.objects.aggregate(Sum=__import__('django.db.models', fromlist=['Sum']).Sum('amount'))['Sum'] or 0
        stats['pending_withdrawals'] = Withdrawal.objects.filter(status='pending').count()
        
        recent_users = User.objects.order_by('-date_joined')[:10]
        recent_payments = Payment.objects.order_by('-created_at')[:10]
        recent_withdrawals = Withdrawal.objects.order_by('-created_at')[:5]
    except:
        pass  # Если БД недоступна, используем демо-данные
    
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
    
    users = []
    total_users = 42
    active_partners = 17
    
    try:
        from users.models import User
        users = list(User.objects.all().order_by('-date_joined')[:50])
        total_users = User.objects.count()
        active_partners = User.objects.filter(status='partner').count()
    except:
        pass
    
    context = {
        'users': users,
        'total_users': total_users,
        'active_partners': active_partners,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/demo_users.html', context)


def admin_demo_structure(request):
    """Демо-версия структуры - СИММЕТРИЧНАЯ МАЙНД-КАРТА"""
    
    root_users = []
    
    try:
        from users.models import User
        root_users = list(User.objects.filter(invited_by__isnull=True).order_by('-date_joined')[:20])
    except:
        pass
    
    context = {
        'root_users': root_users,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/mindmap_symmetric_v3.html', context)


def admin_demo_structure_old(request):
    """Демо-версия структуры - СТАРАЯ ВЕРСИЯ"""
    
    root_users = []
    
    try:
        from users.models import User
        root_users = list(User.objects.filter(invited_by__isnull=True).order_by('-date_joined')[:20])
    except:
        pass
    
    context = {
        'root_users': root_users,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/demo_structure.html', context)


def admin_demo_structure_new(request):
    """Демо-версия структуры - НОВАЯ ГОРИЗОНТАЛЬНАЯ МАЙНД-КАРТА"""
    
    root_users = []
    
    try:
        from users.models import User
        root_users = list(User.objects.filter(invited_by__isnull=True).order_by('-date_joined')[:20])
    except:
        pass
    
    context = {
        'root_users': root_users,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/mindmap_final.html', context)


def structure_viewer(request):
    """Интерактивная визуализация структуры пользователей"""
    
    try:
        from users.models import User
        from mlm.models import MLMStructure
        
        # Получаем корневого пользователя (без инвайтера)
        root_user = User.objects.filter(invited_by__isnull=True).first()
        
        if root_user:
            structure_data = build_structure_tree(root_user)
        else:
            structure_data = None
            
    except Exception as e:
        # Демо-данные если БД недоступна
        structure_data = {
            'id': 1,
            'username': 'demo_admin',
            'name': 'Admin Demo',
            'level': 0,
            'status': 'root',
            'partners': [
                {
                    'id': 2,
                    'username': 'partner1',
                    'name': 'Partner 1',
                    'level': 1,
                    'status': 'partner',
                    'partners': []
                }
            ]
        }
    
    context = {
        'structure_data': structure_data,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/mindmap_final.html', context)


def admin_demo_structure_v6(request):
    """Демо-версия структуры MLM с горизонтальной майнд-картой v6"""
    context = {
        'title': 'MLM Структура - Горизонтальная Майнд-карта v6',
        'description': 'Горизонтальный вид с изогнутыми синими линиями как в примере'
    }
    return render(request, 'admin_panel/mindmap_final.html', context)


def build_structure_tree(user, level=0):
    """Рекурсивно строит дерево структуры"""
    
    # Получаем партнеров текущего пользователя
    partners = user.invited_by.filter(status='partner').order_by('date_joined')[:3]
    
    return {
        'id': user.id,
        'username': user.username,
        'name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'level': level,
        'status': 'root' if level == 0 else 'partner',
        'partners': [build_structure_tree(partner, level + 1) for partner in partners]
    }

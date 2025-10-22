from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.db import models
from users.models import User, Bonus
from payments.models import Payment
from users.services import MLMService


@staff_member_required
def admin_dashboard(request):
    """Главная страница админ панели"""
    stats = MLMService.get_user_stats()
    
    # Получаем последних пользователей
    recent_users = User.objects.select_related('inviter').order_by('-created_at')[:10]
    
    # Получаем статистику бонусов
    bonus_stats = Bonus.objects.aggregate(
        total_green=Sum('amount', filter=models.Q(bonus_type='green')),
        total_red=Sum('amount', filter=models.Q(bonus_type='red')),
        total_paid=Sum('amount', filter=models.Q(is_paid=True)),
        total_unpaid=Sum('amount', filter=models.Q(is_paid=False))
    )
    
    context = {
        'stats': stats,
        'recent_users': recent_users,
        'bonus_stats': bonus_stats,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


@staff_member_required
def users_table(request):
    """Таблица пользователей для админки"""
    users = User.objects.select_related('inviter').order_by('-created_at')
    
    # Фильтрация
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            models.Q(username__icontains=search) |
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(email__icontains=search)
        )
    
    status = request.GET.get('status', '')
    if status:
        users = users.filter(status=status)
    
    rank = request.GET.get('rank', '')
    if rank:
        users = users.filter(rank=rank)
    
    context = {
        'users': users,
        'search': search,
        'status': status,
        'rank': rank,
    }
    
    return render(request, 'admin_panel/users_table.html', context)


@staff_member_required
def user_detail(request, user_id):
    """Детальная информация о пользователе"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)
    
    # Получаем структуру партнеров
    structure = user.structure
    children = PartnerStructure.objects.filter(parent=user).select_related('user')
    
    # Получаем бонусы
    bonuses = Bonus.objects.filter(user=user).order_by('-created_at')[:10]
    
    # Получаем платежи
    payments = Payment.objects.filter(user=user).order_by('-created_at')[:10]
    
    context = {
        'user': user,
        'structure': structure,
        'children': children,
        'bonuses': bonuses,
        'payments': payments,
    }
    
    return render(request, 'admin_panel/user_detail.html', context)


@staff_member_required
def add_user_manually(request):
    """Добавление пользователя вручную через админку"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        inviter_id = request.POST.get('inviter_id')
        
        try:
            inviter = User.objects.get(id=inviter_id) if inviter_id else None
            user = MLMService.register_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                referral_code=inviter.referral_code if inviter else None
            )
            return JsonResponse({'success': True, 'user_id': user.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # Получаем список пользователей для выбора пригласившего
    users = User.objects.filter(status='partner').order_by('username')
    
    return render(request, 'admin_panel/add_user.html', {'users': users})


@staff_member_required
def process_payment(request):
    """Обработка платежа через админку"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        amount = request.POST.get('amount')
        
        try:
            user = User.objects.get(id=user_id)
            amount = float(amount)
            
            payment = MLMService.process_payment(user, amount)
            
            return JsonResponse({
                'success': True,
                'payment_id': payment.id,
                'new_balance': float(user.balance)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@staff_member_required
def move_user(request):
    """Перемещение пользователя в структуре"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_parent_id = request.POST.get('new_parent_id')
        
        try:
            user = User.objects.get(id=user_id)
            new_parent = User.objects.get(id=new_parent_id) if new_parent_id else None
            
            # Обновляем структуру
            structure = user.structure
            old_parent = structure.parent
            
            structure.parent = new_parent
            structure.level = new_parent.structure.level + 1 if new_parent else 0
            structure.save()
            
            # Обновляем статистику старых и новых родителей
            if old_parent:
                MLMService._update_partner_stats(old_parent)
            if new_parent:
                MLMService._update_partner_stats(new_parent)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
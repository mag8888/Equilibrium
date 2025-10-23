from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils.crypto import get_random_string
from users.models import User, UserProfile
from mlm.models import MLMStructure, Payment, Bonus, Withdrawal, MLMSettings, RankUpgrade
from mlm.services import (
    get_bonus_summary,
    get_structure_statistics,
    get_next_position,
    place_user_in_structure,
)
from .models import AdminAction, SystemNotification, SystemStats
import json


def is_admin(user):
    """Проверка, является ли пользователь администратором"""
    return user.is_staff or user.is_superuser


def _collect_descendant_ids(user):
    """Возвращает список идентификаторов всех потомков пользователя."""
    descendants = []
    children = (
        MLMStructure.objects.filter(parent=user)
        .select_related("user")
        .order_by("position", "created_at")
    )
    for child in children:
        child_user = child.user
        descendants.append(child_user.id)
        descendants.extend(_collect_descendant_ids(child_user))
    return descendants


def _recalculate_child_levels(root_user, base_level):
    """Пересчитывает уровни структуры для всех потомков."""
    children = (
        MLMStructure.objects.filter(parent=root_user)
        .select_related("user")
        .order_by("position", "created_at")
    )
    for child in children:
        child.level = base_level + 1
        child.save(update_fields=["level"])
        _recalculate_child_levels(child.user, child.level)


def _normalize_positions(parent_user):
    """Приводит позиции партнеров к последовательному виду."""
    siblings = (
        MLMStructure.objects.filter(parent=parent_user)
        .select_related("user")
        .order_by("position", "created_at")
    )
    for idx, sibling in enumerate(siblings, start=1):
        if sibling.position != idx:
            sibling.position = idx
            sibling.save(update_fields=["position"])


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Главная страница админ-панели"""
    
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
    
    # Уведомления
    notifications = SystemNotification.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        'recent_withdrawals': recent_withdrawals,
        'notifications': notifications,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def users_list(request):
    """Список пользователей"""
    
    users = User.objects.all().order_by('-date_joined')
    
    # Фильтрация
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    rank = request.GET.get('rank', '')
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    if status:
        users = users.filter(status=status)
    
    if rank:
        users = users.filter(rank=rank)
    
    # Статистика для дашборда
    total_users = User.objects.count()
    active_partners = User.objects.filter(status='partner').count()
    new_users_week = User.objects.filter(date_joined__gte=timezone.now() - timezone.timedelta(days=7)).count()
    total_balance = User.objects.aggregate(Sum('balance'))['balance__sum'] or 0
    
    # Пагинация
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'total_users': total_users,
        'active_partners': active_partners,
        'new_users_week': new_users_week,
        'total_balance': total_balance,
        'search': search,
        'status': status,
        'rank': rank,
        'rank_choices': User.RANK_CHOICES,
        'status_choices': User.STATUS_CHOICES,
    }
    
    return render(request, 'admin_panel/users_list.html', context)


@login_required
@user_passes_test(is_admin)
def user_create(request):
    """Создание нового участника вручную."""
    
    inviters = User.objects.order_by('username')
    generated_password = None
    form_data = request.POST.copy() if request.method == 'POST' else {'auto_place': 'on'}
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        status = request.POST.get('status', 'participant')
        rank = request.POST.get('rank', '0')
        inviter_id = request.POST.get('invited_by') or None
        password = request.POST.get('password', '').strip()
        auto_place = request.POST.get('auto_place') == 'on'
        
        if not username or not email:
            messages.error(request, 'Заполните имя пользователя и email')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
        else:
            inviter = None
            if inviter_id:
                inviter = get_object_or_404(User, id=inviter_id)
            
            if not password:
                password = get_random_string(10)
                generated_password = password
            
            try:
                with transaction.atomic():
                    new_user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        invited_by=inviter,
                        status=status,
                        rank=int(rank or 0),
                    )
                    
                    UserProfile.objects.get_or_create(user=new_user)
                    
                    if inviter and auto_place:
                        place_user_in_structure(new_user, inviter)
                    
                    AdminAction.objects.create(
                        admin_user=request.user,
                        action_type='user_create',
                        target_user=new_user,
                        description=f'Создан пользователь {new_user.username}',
                        details={
                            'status': status,
                            'rank': rank,
                            'invited_by': inviter.username if inviter else None,
                            'auto_place': auto_place,
                        }
                    )
                    
                    if generated_password:
                        messages.success(
                            request,
                            f'Пользователь создан. Временный пароль: {generated_password}',
                        )
                    else:
                        messages.success(request, 'Пользователь создан')
                    
                    return redirect('admin_panel:user_detail', user_id=new_user.id)
            except Exception as exc:
                messages.error(request, f'Ошибка при создании пользователя: {exc}')
    
    context = {
        'inviters': inviters,
        'status_choices': User.STATUS_CHOICES,
        'rank_choices': User.RANK_CHOICES,
        'form_data': form_data,
    }
    
    return render(request, 'admin_panel/user_create.html', context)


@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    """Детальная информация о пользователе"""
    
    user = get_object_or_404(User, id=user_id)
    
    # Статистика пользователя
    user_stats = {
        'referrals_count': user.referrals.count(),
        'partners_count': user.referrals.filter(status='partner').count(),
        'total_earned': user.total_earned,
        'current_balance': user.balance,
        'bonuses_count': Bonus.objects.filter(user=user).count(),
        'payments_count': Payment.objects.filter(user=user).count(),
    }
    
    # Структура пользователя
    try:
        mlm_structure = user.mlm_structure
        children = MLMStructure.objects.filter(parent=user).order_by('position')
    except MLMStructure.DoesNotExist:
        mlm_structure = None
        children = []
    
    direct_partners_count = children.filter(user__status='partner').count() if hasattr(children, 'filter') else 0
    direct_participants_count = children.filter(user__status='participant').count() if hasattr(children, 'filter') else 0
    
    # Последние действия
    recent_payments = Payment.objects.filter(user=user).order_by('-created_at')[:5]
    recent_bonuses = Bonus.objects.filter(user=user).order_by('-created_at')[:5]
    recent_referrals = user.referrals.order_by('-date_joined')[:5]
    
    context = {
        'user': user,
        'user_stats': user_stats,
        'mlm_structure': mlm_structure,
        'children': children,
        'recent_payments': recent_payments,
        'recent_bonuses': recent_bonuses,
        'recent_referrals': recent_referrals,
    }
    
    return render(request, 'admin_panel/user_detail.html', context)


@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    """Редактирование пользователя"""
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Обновление основных полей
                user.username = request.POST.get('username', user.username)
                user.email = request.POST.get('email', user.email)
                user.first_name = request.POST.get('first_name', user.first_name)
                user.last_name = request.POST.get('last_name', user.last_name)
                user.phone = request.POST.get('phone', user.phone)
                user.telegram_username = request.POST.get('telegram_username', user.telegram_username)
                user.status = request.POST.get('status', user.status)
                user.rank = int(request.POST.get('rank', user.rank))
                user.balance = float(request.POST.get('balance', user.balance))
                user.is_verified = request.POST.get('is_verified') == 'on'
                user.is_active_mlm = request.POST.get('is_active_mlm') == 'on'
                user.save()
                
                # Логирование действия
                AdminAction.objects.create(
                    admin_user=request.user,
                    action_type='user_edit',
                    target_user=user,
                    description=f'Редактирование пользователя {user.username}',
                    details={
                        'changed_fields': list(request.POST.keys()),
                        'new_values': dict(request.POST)
                    }
                )
                
                messages.success(request, 'Пользователь успешно обновлен')
                return redirect('admin_panel:user_detail', user_id=user.id)
                
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении пользователя: {str(e)}')
    
    return render(request, 'admin_panel/user_edit.html', {'user': user})


@login_required
@user_passes_test(is_admin)
def user_move(request, user_id):
    """Перестановка пользователя в структуре."""
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        mlm_structure = user.mlm_structure
    except MLMStructure.DoesNotExist:
        mlm_structure = None
    
    if not mlm_structure:
        messages.error(request, 'У пользователя нет позиции в структуре')
        return redirect('admin_panel:user_detail', user_id=user.id)
    
    descendants_ids = _collect_descendant_ids(user)
    excluded_ids = [user.id] + descendants_ids
    available_parents = (
        User.objects.exclude(id__in=excluded_ids)
        .order_by('username')
    )
    
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id') or None
        
        new_parent = None
        if parent_id:
            new_parent = get_object_or_404(User, id=parent_id)
        
        if new_parent and new_parent.id == user.id:
            messages.error(request, 'Нельзя разместить пользователя под самим собой')
        else:
            try:
                with transaction.atomic():
                    old_parent = mlm_structure.parent
                    
                    if new_parent:
                        new_parent_structure = getattr(new_parent, 'mlm_structure', None)
                        new_level = (new_parent_structure.level + 1) if new_parent_structure else 1
                        mlm_structure.parent = new_parent
                        mlm_structure.position = get_next_position(new_parent)
                    else:
                        new_level = 0
                        mlm_structure.parent = None
                        mlm_structure.position = 0
                    
                    mlm_structure.level = new_level
                    mlm_structure.save(update_fields=['parent', 'position', 'level'])
                    
                    if old_parent:
                        _normalize_positions(old_parent)
                    
                    if new_parent:
                        _normalize_positions(new_parent)
                    
                    _recalculate_child_levels(user, mlm_structure.level)
                    
                    AdminAction.objects.create(
                        admin_user=request.user,
                        action_type='structure_edit',
                        target_user=user,
                        description=f'Изменено положение {user.username} в структуре',
                        details={
                            'new_parent': new_parent.username if new_parent else None,
                            'old_parent': old_parent.username if old_parent else None,
                        }
                    )
                    
                    messages.success(request, 'Структура обновлена')
                    return redirect('admin_panel:user_structure', user_id=user.id)
            except Exception as exc:
                messages.error(request, f'Ошибка при обновлении структуры: {exc}')
    
    context = {
        'user': user,
        'available_parents': available_parents,
        'current_parent': mlm_structure.parent,
    }
    
    return render(request, 'admin_panel/user_move.html', context)


@login_required
@user_passes_test(is_admin)
def structure_view(request):
    """Визуализация MLM структуры"""
    
    # Получение корневого пользователя (администратора)
    root_user = User.objects.filter(is_superuser=True).first()
    if not root_user:
        root_user = User.objects.first()
    
    # Построение дерева структуры
    def build_tree(user, max_depth=5, current_depth=0):
        if current_depth >= max_depth:
            return None
        
        try:
            mlm_structure = user.mlm_structure
        except MLMStructure.DoesNotExist:
            return None
        
        children = MLMStructure.objects.filter(parent=user).order_by('position')
        tree_children = []
        
        for child in children:
            child_tree = build_tree(child.user, max_depth, current_depth + 1)
            if child_tree:
                tree_children.append(child_tree)
        
        return {
            'user': user,
            'mlm_structure': mlm_structure,
            'children': tree_children,
            'level': current_depth
        }
    
    structure_tree = build_tree(root_user) if root_user else None
    
    # Статистика структуры
    total_in_structure = MLMStructure.objects.count()
    active_partners = User.objects.filter(status='partner').count()
    max_depth = MLMStructure.objects.aggregate(max_level=Count('level'))['max_level'] or 0
    avg_level = MLMStructure.objects.aggregate(avg_level=Count('level'))['avg_level'] or 0
    
    context = {
        'structure_tree': structure_tree,
        'root_user': root_user,
        'total_in_structure': total_in_structure,
        'active_partners': active_partners,
        'max_depth': max_depth,
        'avg_level': avg_level,
    }
    
    return render(request, 'admin_panel/structure_view.html', context)


@login_required
@user_passes_test(is_admin)
def payments_list(request):
    """Список платежей"""
    
    payments = Payment.objects.all().order_by('-created_at')
    
    # Фильтрация
    status = request.GET.get('status', '')
    payment_type = request.GET.get('type', '')
    search = request.GET.get('search', '')
    
    if status:
        payments = payments.filter(status=status)
    
    if payment_type:
        payments = payments.filter(payment_type=payment_type)
    
    if search:
        payments = payments.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(transaction_id__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(payments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status': status,
        'payment_type': payment_type,
        'search': search,
    }
    
    return render(request, 'admin_panel/payments_list.html', context)


@login_required
@user_passes_test(is_admin)
def approve_payment(request, payment_id):
    """Одобрение платежа"""
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.save()
                
                # Обновление статуса пользователя если это регистрация
                if payment.payment_type == 'registration':
                    payment.user.status = 'partner'
                    payment.user.last_payment_date = timezone.now()
                    payment.user.save()
                
                # Логирование действия
                AdminAction.objects.create(
                    admin_user=request.user,
                    action_type='payment_approve',
                    target_user=payment.user,
                    description=f'Одобрен платеж {payment.amount}$ для {payment.user.username}',
                    details={'payment_id': payment.id, 'amount': str(payment.amount)}
                )
                
                messages.success(request, 'Платеж одобрен')
                return redirect('admin_panel:payments_list')
                
        except Exception as e:
            messages.error(request, f'Ошибка при одобрении платежа: {str(e)}')
    
    return render(request, 'admin_panel/approve_payment.html', {'payment': payment})


@login_required
@user_passes_test(is_admin)
def reject_payment(request, payment_id):
    """Отклонение платежа"""
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                payment.status = 'failed'
                payment.save()
                
                # Логирование действия
                AdminAction.objects.create(
                    admin_user=request.user,
                    action_type='payment_reject',
                    target_user=payment.user,
                    description=f'Отклонен платеж {payment.amount}$ для {payment.user.username}',
                    details={'payment_id': payment.id, 'amount': str(payment.amount)}
                )
                
                messages.success(request, 'Платеж отклонен')
                return redirect('admin_panel:payments_list')
                
        except Exception as e:
            messages.error(request, f'Ошибка при отклонении платежа: {str(e)}')
    
    return render(request, 'admin_panel/reject_payment.html', {'payment': payment})


@login_required
@user_passes_test(is_admin)
def bonuses_list(request):
    """Список бонусов"""
    
    bonuses = Bonus.objects.all().order_by('-created_at')
    
    # Фильтрация
    bonus_type = request.GET.get('type', '')
    is_paid = request.GET.get('is_paid', '')
    search = request.GET.get('search', '')
    
    if bonus_type:
        bonuses = bonuses.filter(bonus_type=bonus_type)
    
    if is_paid:
        bonuses = bonuses.filter(is_paid=is_paid == 'true')
    
    if search:
        bonuses = bonuses.filter(
            Q(user__username__icontains=search) |
            Q(from_user__username__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(bonuses, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'bonus_type': bonus_type,
        'is_paid': is_paid,
        'search': search,
    }
    
    return render(request, 'admin_panel/bonuses_list.html', context)


@login_required
@user_passes_test(is_admin)
def withdrawals_list(request):
    """Список запросов на вывод"""
    
    withdrawals = Withdrawal.objects.all().order_by('-created_at')
    
    # Фильтрация
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    if status:
        withdrawals = withdrawals.filter(status=status)
    
    if search:
        withdrawals = withdrawals.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(withdrawals, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status': status,
        'search': search,
    }
    
    return render(request, 'admin_panel/withdrawals_list.html', context)


@login_required
@user_passes_test(is_admin)
def process_withdrawal(request, withdrawal_id):
    """Обработка запроса на вывод"""
    
    withdrawal = get_object_or_404(Withdrawal, id=withdrawal_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            with transaction.atomic():
                if action == 'approve':
                    withdrawal.status = 'completed'
                    withdrawal.processed_at = timezone.now()
                    withdrawal.processed_by = request.user
                    withdrawal.save()
                    
                    messages.success(request, 'Вывод средств одобрен')
                    
                elif action == 'reject':
                    withdrawal.status = 'rejected'
                    withdrawal.processed_at = timezone.now()
                    withdrawal.processed_by = request.user
                    withdrawal.admin_notes = request.POST.get('admin_notes', '')
                    withdrawal.save()
                    
                    # Возвращаем средства на баланс
                    withdrawal.user.balance += withdrawal.amount
                    withdrawal.user.save()
                    
                    messages.success(request, 'Вывод средств отклонен')
                
                # Логирование действия
                AdminAction.objects.create(
                    admin_user=request.user,
                    action_type='withdrawal_process',
                    target_user=withdrawal.user,
                    description=f'Обработан вывод {withdrawal.amount}$ для {withdrawal.user.username}',
                    details={'withdrawal_id': withdrawal.id, 'action': action}
                )
                
                return redirect('admin_panel:withdrawals_list')
                
        except Exception as e:
            messages.error(request, f'Ошибка при обработке вывода: {str(e)}')
    
    return render(request, 'admin_panel/process_withdrawal.html', {'withdrawal': withdrawal})


@login_required
@user_passes_test(is_admin)
def statistics(request):
    """Статистика системы"""
    
    # Общая статистика
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active_mlm=True).count(),
        'participants': User.objects.filter(status='participant').count(),
        'partners': User.objects.filter(status='partner').count(),
        'total_payments': Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_bonuses': Bonus.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_withdrawals': Withdrawal.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    
    # Статистика по рангам
    rank_stats = User.objects.values('rank').annotate(count=Count('id')).order_by('rank')
    
    # Статистика по статусам
    status_stats = User.objects.values('status').annotate(count=Count('id'))
    
    # Ежедневная статистика за последние 30 дней
    daily_stats = []
    for i in range(30):
        date = timezone.now().date() - timezone.timedelta(days=i)
        daily_registrations = User.objects.filter(date_joined__date=date).count()
        daily_payments = Payment.objects.filter(created_at__date=date, status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        
        daily_stats.append({
            'date': date,
            'registrations': daily_registrations,
            'payments': daily_payments,
        })
    
    context = {
        'stats': stats,
        'rank_stats': rank_stats,
        'status_stats': status_stats,
        'daily_stats': daily_stats,
    }
    
    return render(request, 'admin_panel/statistics.html', context)


@login_required
@user_passes_test(is_admin)
def settings(request):
    """Настройки системы"""
    
    mlm_settings = MLMSettings.objects.filter(is_active=True).first()
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                if mlm_settings:
                    mlm_settings.registration_fee = float(request.POST.get('registration_fee', 100))
                    mlm_settings.green_bonus_first = float(request.POST.get('green_bonus_first', 100))
                    mlm_settings.green_bonus_second = float(request.POST.get('green_bonus_second', 50))
                    mlm_settings.red_bonus = float(request.POST.get('red_bonus', 50))
                    mlm_settings.red_bonus_second_partner = float(request.POST.get('red_bonus_second_partner', 50))
                    mlm_settings.red_bonus_third_partner = float(request.POST.get('red_bonus_third_partner', 100))
                    mlm_settings.max_partners_per_level = int(request.POST.get('max_partners_per_level', 3))
                    mlm_settings.save()
                else:
                    mlm_settings = MLMSettings.objects.create(
                        registration_fee=float(request.POST.get('registration_fee', 100)),
                        green_bonus_first=float(request.POST.get('green_bonus_first', 100)),
                        green_bonus_second=float(request.POST.get('green_bonus_second', 50)),
                        red_bonus=float(request.POST.get('red_bonus', 50)),
                        red_bonus_second_partner=float(request.POST.get('red_bonus_second_partner', 50)),
                        red_bonus_third_partner=float(request.POST.get('red_bonus_third_partner', 100)),
                        max_partners_per_level=int(request.POST.get('max_partners_per_level', 3)),
                    )
                
                messages.success(request, 'Настройки сохранены')
                return redirect('admin_panel:settings')
                
        except Exception as e:
            messages.error(request, f'Ошибка при сохранении настроек: {str(e)}')
    
    context = {
        'mlm_settings': mlm_settings,
    }
    
    return render(request, 'admin_panel/settings.html', context)


@login_required
@user_passes_test(is_admin)
def user_structure(request, user_id):
    """Структура конкретного пользователя"""
    
    user = get_object_or_404(User, id=user_id)
    
    # Получение структуры пользователя
    try:
        mlm_structure = user.mlm_structure
        children = MLMStructure.objects.filter(parent=user).order_by('position')
    except MLMStructure.DoesNotExist:
        mlm_structure = None
        children = []
    
    # Построение дерева структуры
    def build_tree(current_user, max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return None
        
        try:
            current_mlm = current_user.mlm_structure
        except MLMStructure.DoesNotExist:
            return None
        
        children = MLMStructure.objects.filter(parent=current_user).order_by('position')
        tree_children = []
        
        for child in children:
            child_tree = build_tree(child.user, max_depth, current_depth + 1)
            if child_tree:
                tree_children.append(child_tree)
        
        return {
            'user': current_user,
            'mlm_structure': current_mlm,
            'children': tree_children,
            'level': current_depth
        }
    
    structure_tree = build_tree(user)
    
    context = {
        'user': user,
        'structure_tree': structure_tree,
        'mlm_structure': mlm_structure,
        'children': children,
        'direct_partners_count': direct_partners_count,
        'direct_participants_count': direct_participants_count,
    }
    
    return render(request, 'admin_panel/user_structure.html', context)


@login_required
@user_passes_test(is_admin)
def notifications(request):
    """Управление уведомлениями"""
    
    notifications = SystemNotification.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            title = request.POST.get('title')
            message = request.POST.get('message')
            notification_type = request.POST.get('type')
            is_global = request.POST.get('is_global') == 'on'
            
            notification = SystemNotification.objects.create(
                title=title,
                message=message,
                notification_type=notification_type,
                is_global=is_global
            )
            
            messages.success(request, 'Уведомление создано')
            
        elif action == 'delete':
            notification_id = request.POST.get('notification_id')
            notification = get_object_or_404(SystemNotification, id=notification_id)
            notification.delete()
            messages.success(request, 'Уведомление удалено')
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'admin_panel/notifications.html', context)

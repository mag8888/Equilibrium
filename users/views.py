from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from .models import User, UserProfile
from mlm.models import MLMStructure, Payment, Bonus, MLMSettings
from mlm.utils import place_user_in_structure, calculate_bonuses
import json


def register(request):
    """Регистрация пользователя по реферальной ссылке"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        referral_code = request.POST.get('referral_code')
        
        # Валидация
        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'users/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return render(request, 'users/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, 'users/register.html')
        
        # Поиск пригласившего
        inviter = None
        if referral_code:
            try:
                inviter = User.objects.get(referral_code=referral_code)
            except User.DoesNotExist:
                messages.error(request, 'Неверный реферальный код')
                return render(request, 'users/register.html')
        
        # Создание пользователя
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    invited_by=inviter,
                    status='participant',
                    rank=0
                )
                
                # Создание профиля
                UserProfile.objects.create(user=user)
                
                # Размещение в структуре
                if inviter:
                    place_user_in_structure(user, inviter)
                
                messages.success(request, 'Регистрация успешна! Теперь вы можете войти в систему.')
                return redirect('users:login')
                
        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return render(request, 'users/register.html')
    
    # GET запрос
    referral_code = request.GET.get('ref', '')
    return render(request, 'users/register.html', {'referral_code': referral_code})


def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('users:dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'users/login.html')


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('users:login')


@login_required
def dashboard(request):
    """Главная страница пользователя"""
    user = request.user
    
    # Статистика пользователя
    stats = {
        'total_referrals': user.referrals.count(),
        'active_partners': user.referrals.filter(status='partner').count(),
        'total_earned': user.total_earned,
        'current_balance': user.balance,
        'rank': user.get_rank_display(),
        'status': user.get_status_display(),
    }
    
    # Последние бонусы
    recent_bonuses = Bonus.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Последние рефералы
    recent_referrals = user.referrals.order_by('-date_joined')[:5]
    
    context = {
        'user': user,
        'stats': stats,
        'recent_bonuses': recent_bonuses,
        'recent_referrals': recent_referrals,
    }
    
    return render(request, 'users/dashboard.html', context)


@login_required
def profile(request):
    """Профиль пользователя"""
    user = request.user
    
    if request.method == 'POST':
        # Обновление профиля
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.phone = request.POST.get('phone', '')
        user.telegram_username = request.POST.get('telegram_username', '')
        user.save()
        
        # Обновление профиля
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.bio = request.POST.get('bio', '')
        profile.country = request.POST.get('country', '')
        profile.city = request.POST.get('city', '')
        profile.save()
        
        messages.success(request, 'Профиль обновлен')
        return redirect('users:profile')
    
    return render(request, 'users/profile.html', {'user': user})


@login_required
def referrals(request):
    """Страница рефералов"""
    user = request.user
    referrals_list = user.referrals.all().order_by('-date_joined')
    
    # Статистика по рефералам
    referrals_stats = {
        'total': referrals_list.count(),
        'participants': referrals_list.filter(status='participant').count(),
        'partners': referrals_list.filter(status='partner').count(),
        'inactive': referrals_list.filter(status='inactive').count(),
    }
    
    context = {
        'referrals': referrals_list,
        'stats': referrals_stats,
        'referral_link': user.get_referral_link(),
    }
    
    return render(request, 'users/referrals.html', context)


@login_required
def structure(request):
    """Структура пользователя"""
    user = request.user
    
    # Получение структуры
    try:
        mlm_structure = user.mlm_structure
        children = MLMStructure.objects.filter(parent=user).order_by('position')
        
        # Построение дерева структуры
        structure_tree = build_structure_tree(user, max_depth=3)
        
    except MLMStructure.DoesNotExist:
        mlm_structure = None
        children = []
        structure_tree = []
    
    context = {
        'user': user,
        'mlm_structure': mlm_structure,
        'children': children,
        'structure_tree': structure_tree,
    }
    
    return render(request, 'users/structure.html', context)


def build_structure_tree(user, max_depth=3, current_depth=0):
    """Построение дерева структуры"""
    if current_depth >= max_depth:
        return []
    
    children = MLMStructure.objects.filter(parent=user).order_by('position')
    tree = []
    
    for child in children:
        child_data = {
            'user': child.user,
            'position': child.position,
            'level': child.level,
            'children': build_structure_tree(child.user, max_depth, current_depth + 1)
        }
        tree.append(child_data)
    
    return tree


@login_required
def upgrade_to_partner(request):
    """Обновление статуса до партнера (оплата $100)"""
    user = request.user
    
    if user.status != 'participant':
        messages.error(request, 'Вы уже являетесь партнером')
        return redirect('users:dashboard')
    
    # Получение настроек MLM
    try:
        mlm_settings = MLMSettings.objects.filter(is_active=True).first()
        if not mlm_settings:
            messages.error(request, 'Настройки MLM не найдены')
            return redirect('users:dashboard')
        
        registration_fee = mlm_settings.registration_fee
        
    except Exception:
        registration_fee = 100.00  # Значение по умолчанию
    
    if request.method == 'POST':
        # Создание платежа
        try:
            with transaction.atomic():
                payment = Payment.objects.create(
                    user=user,
                    amount=registration_fee,
                    payment_type='registration',
                    status='pending',
                    description=f'Оплата за статус партнера - {registration_fee}$'
                )
                
                # Здесь должна быть интеграция с платежной системой
                # Пока что автоматически подтверждаем платеж для тестирования
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.save()
                
                # Обновление статуса пользователя
                user.status = 'partner'
                user.last_payment_date = timezone.now()
                user.save()
                
                # Расчет и начисление бонусов
                calculate_bonuses(user, payment)
                
                messages.success(request, f'Поздравляем! Вы стали партнером. Оплачено: {registration_fee}$')
                return redirect('users:dashboard')
                
        except Exception as e:
            messages.error(request, f'Ошибка при обработке платежа: {str(e)}')
    
    context = {
        'user': user,
        'registration_fee': registration_fee,
    }
    
    return render(request, 'users/upgrade_to_partner.html', context)
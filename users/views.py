from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from .models import User, UserProfile
from mlm.models import MLMStructure, MLMSettings
from mlm.services import place_user_in_structure
import json


def home(request):
    """Главная страница"""
    return render(request, 'users/simple_home.html')


def register(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        referral_code = request.POST.get('referral_code', '')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
        else:
            # Поиск пригласившего по коду
            inviter = None
            if referral_code:
                try:
                    inviter = User.objects.get(referral_code=referral_code)
                except User.DoesNotExist:
                    pass
            
            # Создание пользователя
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
            
            # Автоматический вход
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('users:dashboard')
    
    return render(request, 'users/register.html')


def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Добро пожаловать!')
            return redirect('users:dashboard')
        else:
            messages.error(request, 'Неверные данные для входа')
    
    return render(request, 'users/login.html')


def logout_view(request):
    """Выход из системы"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('users:home')


@login_required
def dashboard(request):
    """Панель пользователя"""
    user = request.user
    
    # Статистика пользователя
    user_stats = {
        'referrals_count': user.referrals.count(),
        'partners_count': user.referrals.filter(status='partner').count(),
        'total_earned': user.total_earned,
        'current_balance': user.balance,
    }
    
    # Структура пользователя
    try:
        mlm_structure = user.mlm_structure
        children = MLMStructure.objects.filter(parent=user).order_by('position')
    except MLMStructure.DoesNotExist:
        mlm_structure = None
        children = []
    
    context = {
        'user': user,
        'user_stats': user_stats,
        'mlm_structure': mlm_structure,
        'children': children,
    }
    
    return render(request, 'users/dashboard.html', context)


@login_required
def profile(request):
    """Профиль пользователя"""
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def referrals(request):
    """Рефералы пользователя"""
    user = request.user
    referrals = user.referrals.all().order_by('-date_joined')
    
    context = {
        'user': user,
        'referrals': referrals,
    }
    
    return render(request, 'users/referrals.html', context)


@login_required
def structure(request):
    """Структура пользователя"""
    user = request.user
    
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
    }
    
    return render(request, 'users/structure.html', context)


@login_required
def upgrade_to_partner(request):
    """Обновление до партнера"""
    user = request.user
    
    if request.method == 'POST':
        # Здесь будет логика оплаты
        # Пока просто обновляем статус
        user.status = 'partner'
        user.save()
        
        messages.success(request, 'Поздравляем! Вы стали партнером!')
        return redirect('users:dashboard')
    
    return render(request, 'users/upgrade_to_partner.html', {'user': user})


def get_referral_link(request):
    """Получение реферальной ссылки"""
    if request.user.is_authenticated:
        referral_code = request.user.referral_code
        referral_link = f"{request.build_absolute_uri('/')}register/?ref={referral_code}"
        return JsonResponse({'referral_link': referral_link})
    return JsonResponse({'error': 'Not authenticated'}, status=401)
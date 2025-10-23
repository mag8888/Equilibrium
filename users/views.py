from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from .models import User, UserProfile
from mlm.models import MLMStructure, MLMSettings
from mlm.services import place_user_in_structure
import json


def home(request):
    """Главная страница - простой HTML с принудительным обновлением"""
    import time
    timestamp = int(time.time())
    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TRINARY MLM - Система работает! (v{timestamp})</title>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                margin: 0;
                animation: fadeIn 1s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .container {
                text-align: center;
                max-width: 800px;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            }
            .logo {
                font-size: 4rem;
                font-weight: 700;
                margin-bottom: 1rem;
                text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            .subtitle {
                font-size: 1.5rem;
                margin-bottom: 2rem;
                opacity: 0.9;
            }
            .btn {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 1rem 2rem;
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                color: white;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                margin: 0.5rem;
            }
            .btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                color: white;
                text-decoration: none;
            }
            .status {
                margin-top: 2rem;
                padding: 1rem;
                background: rgba(40, 167, 69, 0.2);
                border: 2px solid rgba(40, 167, 69, 0.3);
                border-radius: 12px;
                font-size: 0.9rem;
            }
            .timestamp {
                margin-top: 1rem;
                font-size: 0.8rem;
                opacity: 0.7;
            }
        </style>
        <script>
            // Принудительное обновление каждые 30 секунд
            setTimeout(() => {
                location.reload(true);
            }, 30000);
            
            // Показать время загрузки
            document.addEventListener('DOMContentLoaded', function() {
                const timestamp = new Date().toLocaleString('ru-RU');
                document.querySelector('.timestamp').textContent = 'Загружено: ' + timestamp;
            });
        </script>
    </head>
    <body>
        <div class="container">
            <h1 class="logo">🚀 TRINARY MLM</h1>
            <p class="subtitle">Современная MLM система с передовыми технологиями</p>
            
            <div>
                <a href="/admin-panel/" class="btn">🎛️ Админ-панель</a>
                <a href="/admin/" class="btn">⚙️ Django Admin</a>
                <a href="/health/" class="btn">❤️ Health Check</a>
            </div>
            
            <div class="status">
                <strong>✅ Система запущена и работает!</strong><br>
                <small>Современный дизайн • Glass morphism • Адаптивная верстка</small><br>
                <small>Версия: {timestamp} • Время: {time.strftime('%H:%M:%S')}</small>
                <div class="timestamp"></div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html, headers={
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'X-Timestamp': str(timestamp),
        'X-Version': f'v{timestamp}',
        'X-Content-Type': 'text/html; charset=utf-8'
    })


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
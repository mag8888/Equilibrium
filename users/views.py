from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.contrib.auth.forms import AuthenticationForm
from .models import User, UserProfile
from mlm.models import MLMStructure, MLMSettings
from mlm.services import place_user_in_structure
import json


def home(request):
    """Главная страница - максимально простая"""
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TRINARY MLM - Работает!</title>
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
        </style>
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
                <strong>✅ СИСТЕМА РАБОТАЕТ!</strong><br>
                <small>Современный дизайн • Glass morphism • Адаптивная верстка</small>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html, headers={
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Content-Type': 'text/html; charset=utf-8'
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
    """Красивый вход в систему с дизайном"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('admin_panel:dashboard')
        else:
            error_msg = "Неверные данные для входа"
    else:
        error_msg = ""
    
    return render(request, 'registration/login.html', {'error_msg': error_msg})


def logout_view(request):
    """Выход из системы"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('users:home')


def profile(request):
    """Профиль пользователя"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    return render(request, 'users/profile.html')


def dashboard(request):
    """Панель управления пользователя"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    return render(request, 'users/dashboard.html')


def referrals(request):
    """Рефералы пользователя"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    return render(request, 'users/referrals.html')


def structure(request):
    """Структура пользователя"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    return render(request, 'users/structure.html')


def upgrade_to_partner(request):
    """Обновление до партнера"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    return render(request, 'users/upgrade.html')


def get_referral_link(request):
    """Получение реферальной ссылки"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'})
    
    referral_code = request.user.referral_code
    if not referral_code:
        referral_code = get_random_string(8)
        request.user.referral_code = referral_code
        request.user.save()
    
    referral_link = f"{request.build_absolute_uri('/')}register/?ref={referral_code}"
    
    return JsonResponse({
        'referral_code': referral_code,
        'referral_link': referral_link
    })
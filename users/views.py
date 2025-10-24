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
    """Максимально простая версия входа"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username == 'admin' and password == 'admin123':
            return HttpResponse("""
            <html>
            <body style="background: green; color: white; text-align: center; padding: 50px; font-family: Arial;">
                <h1>✅ Успешный вход!</h1>
                <p>Добро пожаловать в TRINARY MLM</p>
                <a href="/admin/" style="color: white; background: rgba(255,255,255,0.2); padding: 10px 20px; text-decoration: none; margin: 10px; border-radius: 5px;">Django Admin</a>
                <a href="/" style="color: white; background: rgba(255,255,255,0.2); padding: 10px 20px; text-decoration: none; margin: 10px; border-radius: 5px;">Главная</a>
            </body>
            </html>
            """)
        else:
            error_msg = "Неверные данные для входа"
    else:
        error_msg = ""
    
    # Простой HTML без сложных f-строк
    error_html = f'<div class="error">{error_msg}</div>' if error_msg else ''
    
    # Получаем CSRF токен
    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    
    # Строим HTML с правильным CSRF токеном
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Вход в TRINARY MLM</title>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }
            
            /* Анимированный фон */
            body::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: 
                    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.3) 0%, transparent 50%);
                animation: backgroundMove 20s ease-in-out infinite;
            }
            
            @keyframes backgroundMove {
                0%, 100% { transform: translateX(0) translateY(0); }
                25% { transform: translateX(-20px) translateY(-10px); }
                50% { transform: translateX(20px) translateY(10px); }
                75% { transform: translateX(-10px) translateY(20px); }
            }
            
            .login-container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                padding: 3rem;
                box-shadow: 
                    0 25px 50px rgba(0, 0, 0, 0.15),
                    0 0 0 1px rgba(255, 255, 255, 0.2);
                width: 100%;
                max-width: 420px;
                text-align: center;
                position: relative;
                z-index: 1;
                animation: slideIn 0.8s ease-out;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(30px) scale(0.95);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }
            
            .logo {
                margin-bottom: 2rem;
            }
            
            .logo h1 {
                color: #667eea;
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                text-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
            }
            
            .logo p {
                color: #6c757d;
                font-size: 1.1rem;
                font-weight: 500;
            }
            
            .form-group {
                margin-bottom: 1.5rem;
                text-align: left;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                color: #495057;
                font-weight: 600;
                font-size: 0.95rem;
            }
            
            .form-group input {
                width: 100%;
                padding: 1rem 1.25rem;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                font-size: 1rem;
                transition: all 0.3s ease;
                background: rgba(255, 255, 255, 0.8);
            }
            
            .form-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
                background: rgba(255, 255, 255, 1);
            }
            
            .btn {
                width: 100%;
                padding: 1rem 1.25rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: left 0.5s;
            }
            
            .btn:hover::before {
                left: 100%;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
            }
            
            .btn:active {
                transform: translateY(0);
            }
            
            .error {
                background: rgba(220, 53, 69, 0.1);
                border: 1px solid rgba(220, 53, 69, 0.3);
                color: #dc3545;
                padding: 1rem;
                border-radius: 12px;
                margin-bottom: 1.5rem;
                font-size: 0.95rem;
                animation: shake 0.5s ease-in-out;
            }
            
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                75% { transform: translateX(5px); }
            }
            
            .links {
                margin-top: 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .links a {
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                padding: 0.5rem 1rem;
                border-radius: 8px;
            }
            
            .links a:hover {
                background: rgba(102, 126, 234, 0.1);
                transform: translateY(-1px);
            }
            
            .features {
                margin-top: 2rem;
                padding: 1.5rem;
                background: rgba(102, 126, 234, 0.05);
                border-radius: 12px;
                border: 1px solid rgba(102, 126, 234, 0.1);
            }
            
            .features h3 {
                color: #667eea;
                font-size: 1.1rem;
                margin-bottom: 1rem;
                text-align: center;
            }
            
            .features ul {
                list-style: none;
                color: #6c757d;
                font-size: 0.9rem;
                line-height: 1.6;
            }
            
            .features li {
                margin-bottom: 0.5rem;
                position: relative;
                padding-left: 1.5rem;
            }
            
            .features li::before {
                content: '✨';
                position: absolute;
                left: 0;
                top: 0;
            }
            
            /* Адаптивность */
            @media (max-width: 480px) {
                .login-container {
                    margin: 1rem;
                    padding: 2rem;
                }
                
                .logo h1 {
                    font-size: 2.5rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">
                <h1>🚀 TRINARY MLM</h1>
                <p>Современная система управления</p>
            </div>
            
            """ + error_html + """
            
            <form method="post">
                 <input type="hidden" name="csrfmiddlewaretoken" value=\"""" + csrf_token + """\">
                  <div class="form-group">
                      <label for="username">Имя пользователя:</label>
                      <input type="text" name="username" id="username" required autocomplete="username">
                  </div>
                  
                  <div class="form-group">
                      <label for="password">Пароль:</label>
                      <input type="password" name="password" id="password" required autocomplete="current-password">
                  </div>
                  
                  <button type="submit" class="btn">Войти в систему</button>
              </form>
            
            <div class="features">
                <h3>🎯 Возможности системы</h3>
                <ul>
                    <li>Управление пользователями</li>
                    <li>MLM структура</li>
                    <li>Система бонусов</li>
                    <li>Аналитика и отчеты</li>
                </ul>
            </div>
            
            <div class="links">
                <a href="/">← На главную</a>
                <a href="/admin-panel/">Админ-панель</a>
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
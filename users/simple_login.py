from django.http import HttpResponse

def simple_login(request):
    """Полностью независимая страница входа"""
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
    
    return HttpResponse(f"""
    <html>
    <head>
        <title>Вход - TRINARY MLM</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 50px; }}
            .container {{ background: rgba(255,255,255,0.1); padding: 30px; border-radius: 10px; max-width: 400px; margin: 0 auto; }}
            input {{ width: 100%; padding: 10px; margin: 10px 0; border: none; border-radius: 5px; }}
            button {{ width: 100%; padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }}
            .error {{ background: rgba(220,53,69,0.8); padding: 10px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 TRINARY MLM</h1>
            <p>Вход в систему</p>
            {f'<div class="error">{error_msg}</div>' if error_msg else ''}
            <form method="post">
                <input type="text" name="username" placeholder="Имя пользователя" required>
                <input type="password" name="password" placeholder="Пароль" required>
                <button type="submit">Войти</button>
            </form>
            <p><a href="/" style="color: white;">← На главную</a></p>
        </div>
    </body>
    </html>
    """)

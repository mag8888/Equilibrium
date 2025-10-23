from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def simple_test(request):
    """Ultra simple test page - no database required"""
    return HttpResponse("""
    <html>
    <head>
        <title>Railway Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .success { color: #27ae60; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Railway Deployment Working!</h1>
            <p class="success">✅ Django is running successfully on Railway!</p>
            <p>Status: All systems operational</p>
            <p>Time: """ + str(__import__('datetime').datetime.now()) + """</p>
        </div>
    </body>
    </html>
    """)

@csrf_exempt
def health_check(request):
    """Simple health check - no database required"""
    return HttpResponse("OK")
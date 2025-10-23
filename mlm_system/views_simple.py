from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Railway deployment is working!',
        'debug': True
    })

def simple_test(request):
    """Simple test page"""
    return HttpResponse("""
    <html>
    <head>
        <title>Railway Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #2c3e50; }
            .success { color: #27ae60; }
        </style>
    </head>
    <body>
        <h1>🚀 Railway Deployment Working!</h1>
        <p class="success">Django is running successfully on Railway!</p>
        <p>Time: """ + str(__import__('datetime').datetime.now()) + """</p>
        <p>Status: ✅ All systems operational</p>
    </body>
    </html>
    """)

def admin_redirect(request):
    """Redirect to admin"""
    from django.shortcuts import redirect
    return redirect('/admin/')

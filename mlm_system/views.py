from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    """Simple health check endpoint that doesn't use database"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Railway deployment is working!',
        'debug': True
    })

def simple_test(request):
    """Simple test page without database"""
    return HttpResponse("""
    <html>
    <head><title>Railway Test</title></head>
    <body>
        <h1>🚀 Railway Deployment Working!</h1>
        <p>Django is running successfully on Railway!</p>
        <p>Time: """ + str(__import__('datetime').datetime.now()) + """</p>
    </body>
    </html>
    """)

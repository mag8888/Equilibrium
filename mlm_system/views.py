from django.http import HttpResponse

def simple_test(request):
    """Ultra simple test page"""
    return HttpResponse("""
    <html>
    <head><title>Railway Test</title></head>
    <body>
        <h1>🚀 Railway Working!</h1>
        <p>Django is running on Railway!</p>
    </body>
    </html>
    """)

def health_check(request):
    """Simple health check"""
    return HttpResponse("OK")
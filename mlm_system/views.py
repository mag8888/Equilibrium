from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    """Simple health check endpoint that doesn't use database"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Railway deployment is working!',
        'debug': True
    })

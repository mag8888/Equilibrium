"""
Максимально простой healthcheck endpoint
Не требует БД и не блокируется при загрузке Django
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """
    Простой healthcheck - отвечает сразу, не требует БД
    """
    if request.method == "HEAD":
        # Для HEAD запросов возвращаем пустой ответ с 200
        return HttpResponse(status=200)
    
    # Для GET запросов возвращаем JSON
    payload = {
        "status": "ok",
        "message": "Equilibrium MLM backend is running",
    }
    response = JsonResponse(payload)
    # Устанавливаем заголовки для быстрого ответа
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

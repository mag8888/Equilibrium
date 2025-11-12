from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    payload = {
        "status": "ok",
        "message": "Equilibrium MLM backend is running",
    }
    response = JsonResponse(payload)
    if request.method == "HEAD":
        response.content = b""
    return response

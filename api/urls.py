from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'mlm', views.MLMViewSet, basename='mlm')
router.register(r'admin', views.AdminViewSet, basename='admin')

# Direct endpoints for admin panel
@api_view(['GET'])
@permission_classes([AllowAny])
def structure_api(request):
    """API endpoint for /api/structure/"""
    try:
        mlm_viewset = views.MLMViewSet()
        mlm_viewset.request = request
        mlm_viewset.format_kwarg = None
        return mlm_viewset.structure(request)
    except Exception as e:
        from rest_framework.response import Response
        return Response([], status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def queue_api(request):
    """API endpoint for /api/queue/"""
    try:
        mlm_viewset = views.MLMViewSet()
        mlm_viewset.request = request
        mlm_viewset.format_kwarg = None
        return mlm_viewset.queue(request)
    except Exception as e:
        from rest_framework.response import Response
        return Response([], status=200)

@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def init_system(request):
    """Инициализация системы: создание root admin и MLM структуры"""
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Вызываем auto_init
        output = StringIO()
        call_command('auto_init', stdout=output)
        auto_init_output = output.getvalue()
        
        # Вызываем create_superuser
        output = StringIO()
        call_command('create_superuser', stdout=output)
        create_superuser_output = output.getvalue()
        
        return Response({
            'status': 'success',
            'message': 'Система инициализирована',
            'auto_init': auto_init_output,
            'create_superuser': create_superuser_output
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

urlpatterns = [
    path('structure/', structure_api, name='api_structure'),
    path('queue/', queue_api, name='api_queue'),
    path('init/', init_system, name='api_init'),
    path('', include(router.urls)),
    path('login/', views.api_login, name='api_login'),
    path('auth-token/', obtain_auth_token, name='api_token_auth'),
]

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
    mlm_viewset = views.MLMViewSet()
    mlm_viewset.request = request
    return mlm_viewset.structure(request)

@api_view(['GET'])
@permission_classes([AllowAny])
def queue_api(request):
    """API endpoint for /api/queue/"""
    mlm_viewset = views.MLMViewSet()
    mlm_viewset.request = request
    return mlm_viewset.queue(request)

urlpatterns = [
    path('structure/', structure_api, name='api_structure'),
    path('queue/', queue_api, name='api_queue'),
    path('', include(router.urls)),
    path('login/', views.api_login, name='api_login'),
    path('auth-token/', obtain_auth_token, name='api_token_auth'),
]

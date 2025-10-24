from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'mlm', views.MLMViewSet, basename='mlm')
router.register(r'admin', views.AdminViewSet, basename='admin')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.api_login, name='api_login'),
    path('auth-token/', obtain_auth_token, name='api_token_auth'),
]

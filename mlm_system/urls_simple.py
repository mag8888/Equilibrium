from django.contrib import admin
from django.urls import path
from . import views_simple

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', views_simple.health_check, name='health_check'),
    path('test/', views_simple.simple_test, name='simple_test'),
    path('admin-redirect/', views_simple.admin_redirect, name='admin_redirect'),
    path('', views_simple.simple_test),  # Root URL
]

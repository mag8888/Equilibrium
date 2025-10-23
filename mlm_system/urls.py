from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', views.health_check, name='health_check'),
    path('test/', views.simple_test, name='simple_test'),
    path('admin-redirect/', views.admin_redirect, name='admin_redirect'),
    path('', views.simple_test),  # Root URL
]
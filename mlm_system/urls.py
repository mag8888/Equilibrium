from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health),
    path('admin-panel/', views.home),  # Добавляем URL для Railway healthcheck
    path('', views.home),
]
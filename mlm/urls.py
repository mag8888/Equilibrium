from django.urls import path
from . import views

app_name = 'mlm'

urlpatterns = [
    path('upgrade/', views.upgrade_rank, name='upgrade_rank'),
    path('bonuses/', views.bonuses, name='bonuses'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('history/', views.payment_history, name='payment_history'),
]

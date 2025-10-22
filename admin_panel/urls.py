from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.users_table, name='users_table'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('add-user/', views.add_user_manually, name='add_user'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('move-user/', views.move_user, name='move_user'),
]

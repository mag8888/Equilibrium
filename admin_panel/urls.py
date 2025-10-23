from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.users_list, name='users_list'),
    path('users/new/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/move/', views.user_move, name='user_move'),
    path('users/<int:user_id>/structure/', views.user_structure, name='user_structure'),
    path('structure/', views.structure_view, name='structure_view'),
    path('payments/', views.payments_list, name='payments_list'),
    path('payments/<int:payment_id>/approve/', views.approve_payment, name='approve_payment'),
    path('payments/<int:payment_id>/reject/', views.reject_payment, name='reject_payment'),
    path('bonuses/', views.bonuses_list, name='bonuses_list'),
    path('withdrawals/', views.withdrawals_list, name='withdrawals_list'),
    path('withdrawals/<int:withdrawal_id>/process/', views.process_withdrawal, name='process_withdrawal'),
    path('statistics/', views.statistics, name='statistics'),
    path('settings/', views.settings, name='settings'),
    path('notifications/', views.notifications, name='notifications'),
]

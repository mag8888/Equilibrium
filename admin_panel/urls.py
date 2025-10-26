from django.urls import path
from . import views, demo_views

app_name = 'admin_panel'

urlpatterns = [
    # Демо-версия админки (без требования аутентификации)
    path('', demo_views.admin_demo_dashboard, name='dashboard'),
    path('users/', demo_views.admin_demo_users, name='users_list'),
    path('structure/', demo_views.admin_demo_structure_new, name='structure_view'),  # Новая горизонтальная майнд-карта
]

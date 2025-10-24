from django.urls import path
from . import views, demo_views

app_name = 'admin_panel'

urlpatterns = [
    # Демо-версия админки (без требования аутентификации)
    path('', demo_views.admin_demo_dashboard, name='dashboard'),
    path('users/', demo_views.admin_demo_users, name='users_list'),
    path('structure/', demo_views.admin_demo_structure, name='structure_view'),
    path('structure-viewer/', demo_views.structure_viewer, name='structure_viewer'),  # Новый интерактивный вьюер
]

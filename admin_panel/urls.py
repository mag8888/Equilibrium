from django.urls import path
from . import views, demo_views

app_name = 'admin_panel'

urlpatterns = [
    # Демо-версия админки (без требования аутентификации)
    path('', demo_views.admin_demo_dashboard, name='dashboard'),
    path('users/', demo_views.admin_demo_users, name='users_list'),
    path('users-management/', demo_views.admin_users_management, name='users_management'),
    path('structure/', demo_views.admin_demo_structure_v6, name='structure_view'),  # Новая горизонтальная майнд-карта
    path('structure-v3/', demo_views.admin_demo_structure_v3, name='structure_v3_view'),
    path('structure-v2/', demo_views.admin_demo_structure_v2, name='structure_v2_view'),
    # API endpoints
    path('api/structure-data/', demo_views.structure_data_api, name='structure_data_api'),
    path('api/save-card/', demo_views.save_card_api, name='save_card_api'),
]

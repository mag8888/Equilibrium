from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('referrals/', views.referrals, name='referrals'),
    path('structure/', views.structure, name='structure'),
    path('upgrade/', views.upgrade_to_partner, name='upgrade_to_partner'),
    path('api/referral-link/', views.get_referral_link, name='referral_link'),
    # Для accounts/login/ перенаправления
    path('', views.login_view, name='accounts_login'),
]

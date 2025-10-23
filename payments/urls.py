from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create/', views.create_payment, name='create_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('status/<str:payment_id>/', views.payment_status, name='payment_status'),
    path('methods/', views.payment_methods, name='payment_methods'),
]

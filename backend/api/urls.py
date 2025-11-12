from django.urls import path

from api.views import (
    HealthStatusView,
    PartnerRegistrationView,
    RegistrationQueueView,
    CompleteRegistrationView,
    StructureTreeView,
)

urlpatterns = [
    path('status/', HealthStatusView.as_view(), name='api-status'),
    path('register/', PartnerRegistrationView.as_view(), name='api-register-partner'),
    path('queue/', RegistrationQueueView.as_view(), name='api-registration-queue'),
    path('complete/', CompleteRegistrationView.as_view(), name='api-complete-registration'),
    path('structure/', StructureTreeView.as_view(), name='api-structure'),
]

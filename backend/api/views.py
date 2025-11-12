from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.models import User
from billing.models import Payment, Bonus
from billing.services import apply_signup_bonuses
from mlm.models import StructureNode, Tariff
from mlm.services import place_user, get_active_tariff
from api.serializers import (
    RegisterPartnerSerializer,
    CompleteRegistrationSerializer,
    QueueEntrySerializer,
    StructureNodeSerializer,
)


class HealthStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "name": "Equilibrium API",
            "version": "0.1.0",
            "status": "ok",
        })


class PartnerRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterPartnerSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        inviter: User = serializer.context['inviter']
        tariff: Tariff = serializer.context.get('tariff') or get_active_tariff()

        with transaction.atomic():
            username = data['username']
            email = data.get('email', '')
            password = User.objects.make_random_password()
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                status=User.Status.PARTICIPANT,
                invited_by=inviter,
            )
            payment = Payment.objects.create(
                user=user,
                amount=tariff.entry_amount,
                tariff=tariff,
                status=Payment.Status.PENDING,
            )
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "temporary_password": password,
                "payment_id": payment.id,
            },
            status=status.HTTP_201_CREATED,
        )


class RegistrationQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = (
            Payment.objects.select_related('user', 'tariff', 'user__invited_by')
            .filter(status=Payment.Status.PENDING)
            .order_by('created_at')
        )
        serializer = QueueEntrySerializer(payments, many=True)
        return Response(serializer.data)


class CompleteRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompleteRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.context['user']

        payment = (
            user.payments.filter(status=Payment.Status.PENDING)
            .order_by('created_at')
            .first()
        )
        if not payment:
            return Response({"detail": "No pending payment found."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.invited_by:
            return Response({"detail": "User has no inviter and cannot be placed."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            payment.mark_completed()
            user.status = User.Status.PARTNER
            user.save(update_fields=['status'])
            placement = place_user(
                inviter=user.invited_by,
                new_user=user,
                tariff=payment.tariff,
            )
            apply_signup_bonuses(payment, placement)

        return Response({
            "detail": "Registration completed",
            "placement_parent": placement.parent.username if placement.parent else None,
            "level": placement.level,
        })


class StructureTreeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nodes = StructureNode.objects.select_related('user', 'parent', 'tariff').all()
        serializer = StructureNodeSerializer(nodes, many=True)
        return Response(serializer.data)

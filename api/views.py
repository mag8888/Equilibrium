from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db.models import Q, Count, Sum
from users.models import User, UserProfile
from mlm.models import MLMStructure, Payment, Bonus, Withdrawal, MLMSettings
from .serializers import (
    UserSerializer, UserProfileSerializer, 
    MLMStructureSerializer, PaymentSerializer,
    BonusSerializer, WithdrawalSerializer
)
import json


class UserViewSet(viewsets.ModelViewSet):
    """API для управления пользователями"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить информацию о текущем пользователе"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def referrals(self, request):
        """Получить рефералов пользователя"""
        user = request.user
        referrals = User.objects.filter(invited_by=user)
        serializer = self.get_serializer(referrals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def structure(self, request):
        """Получить структуру пользователя"""
        user = request.user
        structure = MLMStructure.objects.filter(user=user)
        serializer = MLMStructureSerializer(structure, many=True)
        return Response(serializer.data)


class MLMViewSet(viewsets.ViewSet):
    """API для MLM операций"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    @action(detail=False, methods=['get'])
    def bonuses(self, request):
        """Получить бонусы пользователя"""
        user = request.user
        bonuses = Bonus.objects.filter(user=user)
        serializer = BonusSerializer(bonuses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def payments(self, request):
        """Получить платежи пользователя"""
        user = request.user
        payments = Payment.objects.filter(user=user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def upgrade(self, request):
        """Обновление статуса пользователя"""
        user = request.user
        if user.status == 'participant':
            user.status = 'partner'
            user.rank = 0
            user.save()
            return Response({'status': 'success', 'message': 'Статус обновлен до партнера'})
        return Response({'status': 'error', 'message': 'Нельзя обновить статус'})


class AdminViewSet(viewsets.ViewSet):
    """API для админ-панели"""
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Получить статистику системы"""
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'partners': User.objects.filter(status='partner').count(),
            'participants': User.objects.filter(status='participant').count(),
            'total_payments': Payment.objects.aggregate(total=Sum('amount'))['total'] or 0,
            'total_bonuses': Bonus.objects.aggregate(total=Sum('amount'))['total'] or 0,
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def users_list(self, request):
        """Список всех пользователей"""
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_user(self, request):
        """Создать нового пользователя"""
        data = request.data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            status=data.get('status', 'participant'),
            rank=data.get('rank', 0)
        )
        UserProfile.objects.create(user=user)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def api_login(request):
    """API для входа в систему"""
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        else:
            return Response({'error': 'Неверные данные'}, status=400)
    
    return Response({'error': 'Метод не поддерживается'}, status=405)
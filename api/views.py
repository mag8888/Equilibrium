from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.db.models import Q, Count, Sum
from users.models import User, UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from mlm.models import MLMStructure, Payment, Bonus, Withdrawal, MLMSettings, MLMPartner
from django.db.utils import ProgrammingError, OperationalError
import traceback
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

    def _get_root_user(self, request):
        """Возвращает пользователя-владельца структуры. Если не авторизован — демо-пользователь.
        При отсутствии БД/таблиц возвращает None вместо 500."""
        if request.user and request.user.is_authenticated:
            return request.user
        try:
            demo_user, created = User.objects.get_or_create(
                username='mlm_demo',
                defaults={
                    'email': 'mlm_demo@example.com',
                },
            )
            if created:
                try:
                    demo_user.set_password('mlm_demo_password')
                    demo_user.save(update_fields=['password'])
                except Exception:
                    pass
            return demo_user
        except (ProgrammingError, OperationalError):
            # База или таблицы ещё не готовы
            return None

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
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def create_partner(self, request):
        """Создать нового партнера"""
        try:
            data = request.data
            user = self._get_root_user(request)
            if user is None:
                return Response({'error': 'Database not ready'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Разрешаем parent_id как unique_id родителя
            parent_uid = data.get('parent_id')
            parent_obj = None
            if parent_uid:
                parent_obj = MLMPartner.objects.filter(unique_id=parent_uid, root_user=user).first()

            # Создаем нового партнера
            partner = MLMPartner.objects.create(
                unique_id=data['unique_id'],
                human_name=data['human_name'],
                level=data.get('level', 0),
                position_x=data.get('position_x', 0),
                position_y=data.get('position_y', 0),
                parent=parent_obj,
                root_user=user
            )
            
            return Response({
                'id': partner.id,
                'unique_id': partner.unique_id,
                'human_name': partner.human_name,
                'level': partner.level,
                'position_x': partner.position_x,
                'position_y': partner.position_y,
                'parent_uid': partner.parent.unique_id if partner.parent else None,
                'created_at': partner.created_at.isoformat() if partner.created_at else None
            }, status=status.HTTP_201_CREATED)
        except (ProgrammingError, OperationalError) as e:
            # Таблицы ещё нет (миграции не применены) — не валим 500, а возвращаем понятное сообщение
            return Response({
                'error': 'mlm_mlmpartner table is not ready (migrations not applied)',
                'detail': str(e),
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            import traceback
            return Response({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def partners(self, request):
        """Получить всех партнеров пользователя"""
        try:
            user = self._get_root_user(request)
            if user is None:
                # База не готова — пустой список, чтобы фронт спокойно создал IVA локально
                return Response([], status=status.HTTP_200_OK)
            try:
                partners = MLMPartner.objects.filter(root_user=user, is_active=True)
            except (ProgrammingError, OperationalError):
                # Если таблица ещё не создана — возвращаем пустой список, чтобы фронт не падал
                return Response([], status=status.HTTP_200_OK)
            
            data = []
            for partner in partners:
                data.append({
                    'id': partner.id,
                    'unique_id': partner.unique_id,
                    'human_name': partner.human_name,
                    'level': partner.level,
                    'position_x': partner.position_x,
                    'position_y': partner.position_y,
                    'parent_uid': partner.parent.unique_id if partner.parent else None,
                    'created_at': partner.created_at.isoformat() if partner.created_at else None
                })
            
            return Response(data)
        except Exception as e:
            import traceback
            return Response({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def clear_partners(self, request):
        """Очистить всех партнеров пользователя (для тестирования)"""
        user = self._get_root_user(request)
        deleted_count = MLMPartner.objects.filter(root_user=user).count()
        MLMPartner.objects.filter(root_user=user).delete()
        
        return Response({
            'message': f'Удалено {deleted_count} партнеров',
            'deleted_count': deleted_count
        })


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
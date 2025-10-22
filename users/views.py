from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import User, Bonus
from payments.models import Payment
from .serializers import UserSerializer, BonusSerializer, PaymentSerializer
from .services import MLMService


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Фильтрация по статусу
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Фильтрация по рангу
        rank = self.request.query_params.get('rank', None)
        if rank:
            queryset = queryset.filter(rank=rank)
        
        # Поиск
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Обработка платежа для пользователя"""
        user = self.get_object()
        amount = request.data.get('amount')
        
        if not amount:
            return Response({'error': 'Сумма не указана'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = MLMService.process_payment(user, float(amount))
            return Response({
                'success': True,
                'payment_id': payment.id,
                'new_balance': float(user.balance)
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def structure(self, request, pk=None):
        """Получение структуры пользователя"""
        user = self.get_object()
        structure = user.structure
        children = structure.children.all() if hasattr(structure, 'children') else []
        
        return Response({
            'user': UserSerializer(user).data,
            'structure': {
                'level': structure.level,
                'position': structure.position,
                'children_count': structure.children_count,
                'total_children': structure.total_children,
            },
            'children': UserSerializer(children, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def bonuses(self, request, pk=None):
        """Получение бонусов пользователя"""
        user = self.get_object()
        bonuses = Bonus.objects.filter(user=user).order_by('-created_at')
        serializer = BonusSerializer(bonuses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Получение платежей пользователя"""
        user = self.get_object()
        payments = Payment.objects.filter(user=user).order_by('-created_at')
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class RegisterView(APIView):
    """Регистрация нового пользователя"""
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        referral_code = request.data.get('referral_code')
        
        if not username:
            return Response({'error': 'Username обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = MLMService.register_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                referral_code=referral_code
            )
            
            return Response({
                'success': True,
                'user_id': user.id,
                'referral_code': user.referral_code
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """Профиль текущего пользователя"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
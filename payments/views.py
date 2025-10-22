from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления платежами"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Payment.objects.all()
        
        # Фильтрация по статусу
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Фильтрация по пользователю
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Завершение платежа"""
        payment = self.get_object()
        
        if payment.status != 'pending':
            return Response(
                {'error': 'Платеж уже обработан'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'completed'
        payment.save()
        
        return Response({'success': True})
    
    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        """Отметка платежа как неудачного"""
        payment = self.get_object()
        
        if payment.status != 'pending':
            return Response(
                {'error': 'Платеж уже обработан'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'failed'
        payment.save()
        
        return Response({'success': True})
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Возврат платежа"""
        payment = self.get_object()
        
        if payment.status != 'completed':
            return Response(
                {'error': 'Можно вернуть только завершенные платежи'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'refunded'
        payment.save()
        
        return Response({'success': True})
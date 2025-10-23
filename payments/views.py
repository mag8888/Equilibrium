from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from .models import PaymentMethod, PaymentGateway
from mlm.models import Payment
from users.models import User
import uuid


@login_required
def create_payment(request):
    """Создание платежа"""
    
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        payment_type = request.POST.get('payment_type', 'registration')
        payment_method = request.POST.get('payment_method', '')
        description = request.POST.get('description', '')
        
        # Валидация
        if amount <= 0:
            return JsonResponse({'error': 'Сумма должна быть больше 0'}, status=400)
        
        try:
            with transaction.atomic():
                # Создание платежа
                payment = Payment.objects.create(
                    user=request.user,
                    amount=amount,
                    payment_type=payment_type,
                    payment_method=payment_method,
                    description=description,
                    status='pending',
                    transaction_id=str(uuid.uuid4())
                )
                
                # Здесь должна быть интеграция с платежным шлюзом
                # Пока что возвращаем успешный ответ
                
                return JsonResponse({
                    'success': True,
                    'payment_id': payment.id,
                    'transaction_id': payment.transaction_id,
                    'amount': amount,
                    'status': 'pending'
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET запрос - получение доступных способов оплаты
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    return JsonResponse({
        'payment_methods': [
            {
                'id': method.id,
                'name': method.name,
                'min_amount': float(method.min_amount),
                'max_amount': float(method.max_amount),
                'commission_percent': float(method.commission_percent),
                'commission_fixed': float(method.commission_fixed),
            }
            for method in payment_methods
        ]
    })


def payment_callback(request):
    """Callback от платежного шлюза"""
    
    if request.method == 'POST':
        # Получение данных от платежного шлюза
        transaction_id = request.POST.get('transaction_id')
        status = request.POST.get('status')
        amount = request.POST.get('amount')
        
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            
            with transaction.atomic():
                if status == 'success':
                    payment.status = 'completed'
                    payment.completed_at = timezone.now()
                    payment.save()
                    
                    # Обновление статуса пользователя если это регистрация
                    if payment.payment_type == 'registration':
                        payment.user.status = 'partner'
                        payment.user.last_payment_date = timezone.now()
                        payment.user.save()
                    
                    # Расчет бонусов
                    from mlm.utils import calculate_bonuses
                    calculate_bonuses(payment.user, payment)
                    
                elif status == 'failed':
                    payment.status = 'failed'
                    payment.save()
                
                return JsonResponse({'status': 'ok'})
                
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def payment_status(request, payment_id):
    """Проверка статуса платежа"""
    
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
        
        return JsonResponse({
            'payment_id': payment.id,
            'transaction_id': payment.transaction_id,
            'amount': float(payment.amount),
            'status': payment.status,
            'payment_type': payment.payment_type,
            'created_at': payment.created_at.isoformat(),
            'completed_at': payment.completed_at.isoformat() if payment.completed_at else None,
        })
        
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)


def payment_methods(request):
    """Получение доступных способов оплаты"""
    
    methods = PaymentMethod.objects.filter(is_active=True)
    
    return JsonResponse({
        'methods': [
            {
                'id': method.id,
                'name': method.name,
                'min_amount': float(method.min_amount),
                'max_amount': float(method.max_amount),
                'commission_percent': float(method.commission_percent),
                'commission_fixed': float(method.commission_fixed),
            }
            for method in methods
        ]
    })
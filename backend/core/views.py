from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models import User
try:
    from mlm.models import StructureNode, Tariff
    from billing.models import Payment, Bonus
except ImportError:
    StructureNode = None
    Tariff = None
    Payment = None
    Bonus = None


@require_http_methods(["GET"])
def admin_dashboard(request):
    """Главная страница админ-панели"""
    stats = {
        'total_users': User.objects.count(),
        'partners': User.objects.filter(status=User.Status.PARTNER).count(),
        'participants': User.objects.filter(status=User.Status.PARTICIPANT).count(),
        'total_nodes': StructureNode.objects.count() if StructureNode else 0,
        'pending_payments': Payment.objects.filter(status=Payment.Status.PENDING).count() if Payment else 0,
        'total_bonuses': sum(b.amount for b in Bonus.objects.all()) if Bonus else 0,
    }
    return render(request, 'admin/dashboard.html', {'stats': stats})


@api_view(['GET'])
@permission_classes([AllowAny])
def admin_structure_api(request):
    """API для получения структуры"""
    if not StructureNode:
        return Response([])
    nodes = StructureNode.objects.select_related('user', 'parent', 'tariff').all()
    data = []
    for node in nodes:
        data.append({
            'id': node.id,
            'uid': str(node.user.id) if node.user else None,
            'name': node.user.username if node.user else 'Empty',
            'level': node.level,
            'parent_id': node.parent.id if node.parent else None,
            'tariff': node.tariff.name if node.tariff else None,
            'position': node.position,
        })
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def admin_queue_api(request):
    """API для получения очереди регистраций"""
    if not Payment:
        return Response([])
    payments = Payment.objects.filter(status=Payment.Status.PENDING).select_related('user', 'tariff', 'user__invited_by')[:50]
    data = []
    for payment in payments:
        data.append({
            'id': payment.id,
            'username': payment.user.username if payment.user else 'Unknown',
            'referral_code': payment.user.referral_code if payment.user else None,
            'inviter': payment.user.invited_by.username if payment.user and payment.user.invited_by else None,
            'tariff': payment.tariff.name if payment.tariff else None,
            'amount': float(payment.amount) if payment.amount else 0,
        })
    return Response(data)

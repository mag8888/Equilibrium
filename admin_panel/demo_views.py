"""
Демо-версия админ-панели без требования аутентификации
Используется для демонстрации функционала
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from .structure_data import build_structure_dataset
from users.models import User
from mlm.models import MLMStructure


def admin_demo_dashboard(request):
    """Демо-версия главной страницы админ-панели"""
    
    # Демо-данные (не подключаемся к БД)
    stats = {
        'total_users': 42,
        'active_users': 38,
        'participants': 25,
        'partners': 17,
        'total_payments': 4250.00,
        'pending_payments': 3,
        'total_bonuses': 1520.50,
        'pending_withdrawals': 2,
    }
    recent_users = []
    recent_payments = []
    recent_withdrawals = []
    
    try:
        from mlm.models import Payment, Bonus, Withdrawal
        
        # Пытаемся получить реальные данные
        stats['total_users'] = User.objects.count()
        stats['active_users'] = User.objects.filter(is_active_mlm=True).count()
        stats['participants'] = User.objects.filter(status='participant').count()
        stats['partners'] = User.objects.filter(status='partner').count()
        stats['total_payments'] = Payment.objects.filter(status='completed').aggregate(Sum=__import__('django.db.models', fromlist=['Sum']).Sum('amount'))['Sum'] or 0
        stats['pending_payments'] = Payment.objects.filter(status='pending').count()
        stats['total_bonuses'] = Bonus.objects.aggregate(Sum=__import__('django.db.models', fromlist=['Sum']).Sum('amount'))['Sum'] or 0
        stats['pending_withdrawals'] = Withdrawal.objects.filter(status='pending').count()
        
        recent_users = User.objects.order_by('-date_joined')[:10]
        recent_payments = Payment.objects.order_by('-created_at')[:10]
        recent_withdrawals = Withdrawal.objects.order_by('-created_at')[:5]
    except:
        pass  # Если БД недоступна, используем демо-данные
    
    context = {
        'stats': stats,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        'recent_withdrawals': recent_withdrawals,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/demo_dashboard.html', context)


def admin_demo_users(request):
    """Демо-версия списка пользователей"""
    
    users = []
    total_users = 42
    active_partners = 17
    
    try:
        from users.models import User
        users = list(User.objects.all().order_by('-date_joined')[:50])
        total_users = User.objects.count()
        active_partners = User.objects.filter(status='partner').count()
    except:
        pass
    
    context = {
        'users': users,
        'total_users': total_users,
        'active_partners': active_partners,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/demo_users.html', context)


def admin_demo_structure(request):
    """Демо-версия структуры - СИММЕТРИЧНАЯ МАЙНД-КАРТА"""
    
    root_users = []
    
    try:
        from users.models import User
        root_users = list(User.objects.filter(invited_by__isnull=True).order_by('-date_joined')[:20])
    except:
        pass
    
    context = {
        'root_users': root_users,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/mindmap_symmetric_v3.html', context)


def admin_demo_structure_old(request):
    """Демо-версия структуры - СТАРАЯ ВЕРСИЯ"""
    
    root_users = []
    
    try:
        from users.models import User
        root_users = list(User.objects.filter(invited_by__isnull=True).order_by('-date_joined')[:20])
    except:
        pass
    
    context = {
        'root_users': root_users,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/demo_structure.html', context)


def admin_demo_structure_new(request):
    """Демо-версия структуры - НОВАЯ ГОРИЗОНТАЛЬНАЯ МАЙНД-КАРТА"""
    
    root_users = []
    
    try:
        from users.models import User
        root_users = list(User.objects.filter(invited_by__isnull=True).order_by('-date_joined')[:20])
    except:
        pass
    
    context = {
        'root_users': root_users,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/mindmap_final.html', context)


def structure_viewer(request):
    """Интерактивная визуализация структуры пользователей"""
    
    try:
        from users.models import User
        from mlm.models import MLMStructure
        
        # Получаем корневого пользователя (без инвайтера)
        root_user = User.objects.filter(invited_by__isnull=True).first()
        
        if root_user:
            structure_data = build_structure_tree(root_user)
        else:
            structure_data = None
            
    except Exception as e:
        # Демо-данные если БД недоступна
        structure_data = {
            'id': 1,
            'username': 'demo_admin',
            'name': 'Admin Demo',
            'level': 0,
            'status': 'root',
            'partners': [
                {
                    'id': 2,
                    'username': 'partner1',
                    'name': 'Partner 1',
                    'level': 1,
                    'status': 'partner',
                    'partners': []
                }
            ]
        }
    
    context = {
        'structure_data': structure_data,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/mindmap_final.html', context)


def admin_demo_structure_v3(request):
    """Демо-версия структуры - СИММЕТРИЧНАЯ МАЙНД-КАРТА v3"""
    
    root_users = []
    
    try:
        from users.models import User
        root_users = list(User.objects.filter(invited_by__isnull=True).order_by('-date_joined')[:20])
    except:
        pass
    
    context = {
        'root_users': root_users,
        'is_demo': True,
    }
    
    return render(request, 'admin_panel/mindmap_symmetric_v3.html', context)


def admin_demo_structure_v6(request):
    """Демо-версия структуры MLM с горизонтальной майнд-картой v6"""
    context = {
        'title': 'MLM Структура - Горизонтальная Майнд-карта v6',
        'description': 'Горизонтальный вид с изогнутыми синими линиями как в примере'
    }
    return render(request, 'admin_panel/mindmap_final.html', context)


def admin_demo_structure_v2(request):
    """Новая страница структуры v2: сетка, панорама, drag карточек"""
    return render(request, 'admin_panel/structure_v2.html', {})


def structure_data_api(request):
    """Возвращает актуальные данные структуры и статистику для визуализации v2."""
    try:
        dataset, stats = build_structure_dataset()
        response = {
            'structure': {
                'cards': dataset.cards,
                'childMap': dataset.child_map,
                'uidCounter': dataset.uid_counter,
            },
            'stats': {
                'root': stats.root,
                'levels': stats.levels,
                'totals': stats.totals,
                'generated_at': stats.generated_at,
            }
        }
        return JsonResponse(response, json_dumps_params={'ensure_ascii': False})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@csrf_exempt
def save_card_api(request):
    """API для сохранения карточки в базу данных"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        
        data = json.loads(request.body)
        uid = data.get('uid')
        name = data.get('name')
        inviter_uid = data.get('inviter_uid')
        
        if not uid or not name:
            return JsonResponse({'error': 'UID and name are required'}, status=400)
        
        # Разделяем имя на имя и фамилию
        name_parts = name.split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else name
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Используем UID как referral_code (первые 8 символов)
        referral_code = str(uid)[:8].upper()
        
        # Для root пользователя используем специальный username
        is_root = str(uid) == '0000001' or name == 'IVA'
        username = 'root' if is_root else f'user_{uid}'
        email = 'root@example.com' if is_root else f'user_{uid}@example.com'
        
        with transaction.atomic():
            # Ищем пользователя по referral_code или username
            user = None
            created = False
            
            try:
                user = User.objects.get(referral_code=referral_code)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    # Создаем нового пользователя
                    user = User.objects.create(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        referral_code=referral_code,
                    )
                    created = True
            
            # Обновляем имя если пользователь уже существует
            if not created:
                user.first_name = first_name
                user.last_name = last_name
                if not user.referral_code:
                    user.referral_code = referral_code
                user.save()
            
            # Устанавливаем пригласителя
            parent_user = None
            if inviter_uid:
                try:
                    inviter_code = str(inviter_uid)[:8].upper()
                    inviter = User.objects.get(referral_code=inviter_code)
                    parent_user = inviter
                    if user.invited_by != inviter:
                        user.invited_by = inviter
                except User.DoesNotExist:
                    parent_user = None
            # Обновляем статус пользователя как партнера
            if user.status != 'partner':
                user.status = 'partner'
            user.save()

            level = int(data.get('level', 0))
            if parent_user and level == 0:
                parent_structure = getattr(parent_user, 'mlm_structure', None)
                if parent_structure:
                    level = parent_structure.level + 1

            # Рассчитываем позицию в структуре
            position = data.get('position')
            if position is None and parent_user:
                existing_positions = set(
                    MLMStructure.objects.filter(parent=parent_user).values_list('position', flat=True)
                )
                for slot in range(1, 4):
                    if slot not in existing_positions:
                        position = slot
                        break
                if position is None:
                    position = (len(existing_positions) % 3) + 1
            elif position is None:
                position = 0

            structure_defaults = {
                'parent': parent_user,
                'level': level,
                'position': position,
                'is_active': True,
            }
            structure, structure_created = MLMStructure.objects.get_or_create(
                user=user,
                defaults=structure_defaults,
            )
            if not structure_created:
                updated = False
                if structure.parent != parent_user:
                    structure.parent = parent_user
                    updated = True
                if structure.level != level:
                    structure.level = level
                    updated = True
                if structure.position != position:
                    structure.position = position
                    updated = True
                if not structure.is_active:
                    structure.is_active = True
                    updated = True
                if updated:
                    structure.save()

            return JsonResponse({
                'success': True,
                'user_id': user.id,
                'created': created,
                'structure_created': structure_created,
            })
            
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@csrf_exempt
def clear_partners_api(request):
    """Удаляет всех партнеров из MLM структуры, сохраняя только корневого пользователя"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        with transaction.atomic():
            structures = list(MLMStructure.objects.select_related('user'))
            root_structure = next((item for item in structures if item.parent_id is None), None)

            if root_structure:
                MLMStructure.objects.exclude(pk=root_structure.pk).delete()
                root_structure.level = 0
                root_structure.position = 0
                root_structure.is_active = True
                root_structure.save()
                root_user = root_structure.user
            else:
                root_user = (
                    User.objects.filter(is_superuser=True).first()
                    or User.objects.filter(is_staff=True).first()
                    or User.objects.first()
                )
                MLMStructure.objects.all().delete()
                if root_user:
                    root_structure = MLMStructure.objects.create(
                        user=root_user,
                        parent=None,
                        level=0,
                        position=0,
                        is_active=True,
                    )

            if root_user and hasattr(root_user, 'status'):
                if root_user.status != 'partner':
                    root_user.status = 'partner'
                    root_user.save()

        return JsonResponse({'success': True})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


def admin_users_management(request):
    """Админка для управления пользователями с балансом"""
    from users.models import User
    from django.db.models import Q, Sum
    from django.core.paginator import Paginator
    import json
    
    # Получение списка пользователей
    users = User.objects.all().order_by('-date_joined')
    
    # Фильтрация
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(referral_code__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(users, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Статистика
    total_users = User.objects.count()
    total_balance = User.objects.aggregate(Sum('balance'))['balance__sum'] or 0
    
    # Обработка изменения баланса
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            user_id = request.POST.get('user_id')
            amount = float(request.POST.get('amount', 0))
            
            user = User.objects.get(id=user_id)
            
            if action == 'add_balance':
                user.balance += amount
                user.save()
                return JsonResponse({'success': True, 'new_balance': float(user.balance)})
            elif action == 'subtract_balance':
                if user.balance >= amount:
                    user.balance -= amount
                    user.save()
                    return JsonResponse({'success': True, 'new_balance': float(user.balance)})
                else:
                    return JsonResponse({'error': 'Недостаточно средств'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    context = {
        'users': page_obj,
        'total_users': total_users,
        'total_balance': total_balance,
        'search': search,
    }
    
    return render(request, 'admin_panel/users_management.html', context)


def build_structure_tree(user, level=0):
    """Рекурсивно строит дерево структуры"""
    
    # Получаем партнеров текущего пользователя
    partners = user.invited_by.filter(status='partner').order_by('date_joined')[:3]
    
    return {
        'id': user.id,
        'username': user.username,
        'name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'level': level,
        'status': 'root' if level == 0 else 'partner',
        'partners': [build_structure_tree(partner, level + 1) for partner in partners]
    }

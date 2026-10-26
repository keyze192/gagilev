from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cases, Chance, Users, CaseOpening, UserInventory
import random


@csrf_exempt
def open_case(request, case_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешен'})

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'need_auth': True,
            'error': 'Войдите через Steam'
        })

    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return JsonResponse({'success': False, 'error': 'Профиль не найден'})

    case = get_object_or_404(Cases, id=case_id)

    if user_profile.balance < case.price:
        return JsonResponse({'success': False, 'error': 'Недостаточно средств'})

    chances = Chance.objects.filter(cases=case).select_related('item')
    if not chances.exists():
        return JsonResponse({'success': False, 'error': 'В кейсе нет предметов'})

  
    items_with_chances = [{'item': c.item, 'chance': float(c.chance)} for c in chances]
    total = sum(i['chance'] for i in items_with_chances)

    r = random.uniform(0, total)
    cumulative = 0
    selected_item = items_with_chances[-1]['item']
    for i in items_with_chances:
        cumulative += i['chance']
        if r <= cumulative:
            selected_item = i['item']
            break

    with transaction.atomic():
        user_profile.balance -= case.price
        user_profile.save()

        CaseOpening.objects.create(user=user_profile, case=case, item=selected_item)

        inv, created = UserInventory.objects.get_or_create(
            user=user_profile, item=selected_item,
            defaults={'quantity': 1}
        )
        if not created:
            inv.quantity += 1
            inv.save()


    rarity_class_map = {
        'common': 'common', 'rare': 'rare', 'epic': 'epic',
        'legendary': 'legendary', 'ancient': 'ancient'
    }
    rarity_name_map = {
        'common': 'Обычный', 'rare': 'Редкий', 'epic': 'Эпический',
        'legendary': 'Легендарный', 'ancient': 'Древний'
    }

    def serialize_item(item):
        rarity = (item.rarity or 'common').lower()
        return {
            'id': item.id,
            'name': item.name,
            'price': float(item.price),
            'rarity': rarity,
            'rarity_class': rarity_class_map.get(rarity, 'common'),
            'rarity_name': rarity_name_map.get(rarity, 'Обычный'),
            'is_stattrack': item.is_stattrack,
            'icon': get_item_icon(item.name),
        }

    all_items = [serialize_item(c.item) for c in chances]

    return JsonResponse({
        'success': True,
        'item': serialize_item(selected_item),
        'all_items': all_items,
        'new_balance': float(user_profile.balance),
    })


def get_item_icon(name):

    n = (name or '').lower()
    if 'нож' in n or 'knife' in n:
        return 'fa-crosshairs'
    if 'перчатк' in n or 'glove' in n:
        return 'fa-hand-paper'
    if any(x in n for x in ['ak', 'awp', 'm4', 'деagle', 'deagle', 'usp', 'glock', 'famas']):
        return 'fa-gun'
    return 'fa-cube'


@csrf_exempt
def sell_item(request, inventory_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешен'})

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'need_auth': True, 'error': 'Войдите через Steam'})

    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return JsonResponse({'success': False, 'error': 'Профиль не найден'})

    try:
        with transaction.atomic():
            inv = UserInventory.objects.select_related('item').get(
                id=inventory_id, user=user_profile
            )
            sell_price = int(float(inv.item.price))
            if inv.quantity > 1:
                inv.quantity -= 1
                inv.save()
            else:
                inv.delete()
            user_profile.balance += sell_price
            user_profile.save()

        return JsonResponse({
            'success': True,
            'sold_price': sell_price,
            'new_balance': float(user_profile.balance),
        })
    except UserInventory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Предмет не найден'})


@csrf_exempt
def sell_all_items(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешен'})

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'need_auth': True, 'error': 'Войдите через Steam'})

    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return JsonResponse({'success': False, 'error': 'Профиль не найден'})

    with transaction.atomic():
        items = UserInventory.objects.select_related('item').filter(user=user_profile)
        total_price = 0
        count = 0
        for inv in items:
            total_price += int(float(inv.item.price)) * inv.quantity
            count += inv.quantity
        items.delete()
        user_profile.balance += total_price
        user_profile.save()

    return JsonResponse({
        'success': True,
        'items_count': count,
        'total_price': total_price,
        'new_balance': float(user_profile.balance),
    })


@csrf_exempt
def case_history(request, case_id):
    case = get_object_or_404(Cases, id=case_id)
    openings = CaseOpening.objects.filter(case=case).select_related(
        'user', 'item'
    ).order_by('-opened_at')[:20]

    from django.utils.timesince import timesince
    history = []
    for o in openings:
        history.append({
            'username': o.user.display_name if o.user else 'Аноним',
            'item_name': o.item.name,
            'item_price': float(o.item.price),
            'rarity': (o.item.rarity or 'common').lower(),
            'time_ago': timesince(o.opened_at, depth=1) + ' назад',
        })

    return JsonResponse({'success': True, 'history': history})


import random
from decimal import Decimal
from .models import Items, UserInventory

@csrf_exempt
def get_all_items(request):

    items = Items.objects.all().order_by('price')
    data = [{
        'id': i.id,
        'name': i.name,
        'price': float(i.price),
        'rarity': (i.rarity or 'common').lower(),
        'icon': get_item_icon(i.name)
    } for i in items]
    return JsonResponse({'success': True, 'items': data})

@csrf_exempt
def do_upgrade(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешен'})
    
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'need_auth': True, 'error': 'Войдите через Steam'})

    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return JsonResponse({'success': False, 'error': 'Профиль не найден'})

    try:
        import json
        body = json.loads(request.body)
        inv_id = body.get('inventory_id')
        target_item_id = body.get('target_item_id')
        

        inv = UserInventory.objects.select_related('item').get(id=inv_id, user=user_profile)
        target_item = Items.objects.get(id=target_item_id)
        
        inv_price = float(inv.item.price)
        target_price = float(target_item.price)
        
        if target_price <= inv_price:
            return JsonResponse({'success': False, 'error': 'Целевой предмет должен быть дороже'})
            
        chance = (inv_price / target_price) * 100
        chance = min(chance, 90.0) # Максимальный шанс 90%
        

        roll = random.uniform(0, 100)
        is_win = roll <= chance
        

        if inv.quantity > 1:
            inv.quantity -= 1
            inv.save()
        else:
            inv.delete()
            

        if is_win:
            new_inv, created = UserInventory.objects.get_or_create(
                user=user_profile, item=target_item, defaults={'quantity': 1}
            )
            if not created:
                new_inv.quantity += 1
                new_inv.save()
                

        inventory = UserInventory.objects.filter(user=user_profile).select_related('item')
        inv_list = [{
            'id': i.id,
            'quantity': i.quantity,
            'item_details': {
                'name': i.item.name,
                'price': float(i.item.price),
                'rarity': (i.item.rarity or 'common').lower(),
                'icon': get_item_icon(i.item.name)
            }
        } for i in inventory]

        return JsonResponse({
            'success': True,
            'is_win': is_win,
            'chance': round(chance, 2),
            'new_balance': float(user_profile.balance),
            'inventory': inv_list
        })
        
    except UserInventory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Предмет не найден в инвентаре'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


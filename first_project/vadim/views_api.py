from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Cases, Chance, Users, CaseOpening, UserInventory
from django.db import transaction
import random


@csrf_exempt
def open_case(request, case_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешен'})

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Войдите через Steam, чтобы открывать кейсы',
            'need_auth': True
        })

    try:
        case = get_object_or_404(Cases, id=case_id)

        try:
            user_profile = Users.objects.get(user=request.user)
        except Users.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Профиль не найден'})

        if user_profile.balance < case.price:
            return JsonResponse({
                'success': False,
                'error': f'Недостаточно средств. Нужно {case.price} ₽, у вас {user_profile.balance} ₽'
            })

        chances = Chance.objects.filter(cases=case).select_related('item')

        if not chances.exists():
            return JsonResponse({'success': False, 'error': 'В этом кейсе нет предметов'})

        items_with_chances = [
            {'item': c.item, 'chance': float(c.chance)}
            for c in chances
        ]

        selected_item = select_item_by_chance(items_with_chances)

        if not selected_item:
            return JsonResponse({'success': False, 'error': 'Ошибка при выборе предмета'})

        user_profile.balance -= case.price
        user_profile.save()

        CaseOpening.objects.create(
            user=user_profile,
            case=case,
            item=selected_item
        )

        inv, created = UserInventory.objects.get_or_create(
            user=user_profile,
            item=selected_item,
            defaults={'quantity': 1}
        )
        if not created:
            inv.quantity += 1
            inv.save()

        all_items = []
        for c in chances:
            all_items.append({
                'id': c.item.id,
                'name': c.item.name,
                'price': float(c.item.price),
                'rarity': c.item.rarity,
                'rarity_class': get_rarity_class(c.item.rarity),
                'is_stattrack': c.item.is_stattrack,
                'icon': get_item_icon(c.item.name),
            })

        return JsonResponse({
            'success': True,
            'item': {
                'id': selected_item.id,
                'name': selected_item.name,
                'price': float(selected_item.price),
                'rarity': selected_item.rarity,
                'rarity_class': get_rarity_class(selected_item.rarity),
                'rarity_name': get_rarity_name(selected_item.rarity),
                'is_stattrack': selected_item.is_stattrack,
                'icon': get_item_icon(selected_item.name),
            },
            'all_items': all_items,
            'new_balance': user_profile.balance,
            'case_price': case.price
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def select_item_by_chance(items_with_chances):
    total = sum(i['chance'] for i in items_with_chances)
    if total <= 0:
        return items_with_chances[0]['item'] if items_with_chances else None

    if abs(total - 100) > 0.01:
        for i in items_with_chances:
            i['chance'] = (i['chance'] / total) * 100

    r = random.uniform(0, 100)
    cumulative = 0
    for i in items_with_chances:
        cumulative += i['chance']
        if r <= cumulative:
            return i['item']

    return items_with_chances[-1]['item']


def get_rarity_class(rarity):
    return {
        'common': 'common',
        'rare': 'rare',
        'epic': 'epic',
        'legendary': 'legendary',
        'ancient': 'ancient'
    }.get(rarity.lower(), 'common')


def get_rarity_name(rarity):
    return {
        'common': 'Обычный',
        'rare': 'Редкий',
        'epic': 'Эпический',
        'legendary': 'Легендарный',
        'ancient': 'Древний'
    }.get(rarity.lower(), rarity)


def get_item_icon(name):
    n = name.lower()
    if 'нож' in n or 'knife' in n:
        return 'fa-crosshairs'
    if 'перчатк' in n or 'glove' in n:
        return 'fa-hand-paper'
    if 'ak' in n or 'awp' in n or 'm4' in n or 'deagle' in n:
        return 'fa-gun'
    return 'fa-cube'


@login_required
def case_history(request, case_id):
    try:
        case = get_object_or_404(Cases, id=case_id)
        openings = CaseOpening.objects.filter(case=case).select_related('user', 'item').order_by('-opened_at')[:20]

        history = [{
            'username': o.user.display_name if o.user else 'Аноним',
            'item_name': o.item.name,
            'item_price': float(o.item.price),
            'rarity': o.item.rarity,
            'time_ago': time_ago(o.opened_at)
        } for o in openings]

        return JsonResponse({'success': True, 'history': history})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def time_ago(dt):
    diff = timezone.now() - dt
    if diff.days > 0:
        return f'{diff.days} дн. назад'
    if diff.seconds > 3600:
        return f'{diff.seconds // 3600} ч. назад'
    if diff.seconds > 60:
        return f'{diff.seconds // 60} мин. назад'
    return 'только что'

@csrf_exempt
def sell_item(request, inventory_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешен'})

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Войдите, чтобы продавать предметы', 'need_auth': True})

    try:
        user_profile = Users.objects.get(user=request.user)
    except Users.DoesNotExist:
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
            'new_balance': user_profile.balance,
            'item_name': inv.item.name if inv.pk else 'Предмет',
        })

    except UserInventory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Предмет не найден в инвентаре'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def sell_all_items(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешен'})

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Войдите, чтобы продавать предметы', 'need_auth': True})

    try:
        user_profile = Users.objects.get(user=request.user)
    except Users.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Профиль не найден'})

    try:
        with transaction.atomic():
            inventory = UserInventory.objects.filter(user=user_profile).select_related('item')

            if not inventory.exists():
                return JsonResponse({'success': False, 'error': 'Инвентарь пуст'})

            total = 0
            count = 0
            for inv in inventory:
                total += int(float(inv.item.price)) * inv.quantity
                count += inv.quantity

            inventory.delete()

            user_profile.balance += total
            user_profile.save()

        return JsonResponse({
            'success': True,
            'total_price': total,
            'items_count': count,
            'new_balance': user_profile.balance,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
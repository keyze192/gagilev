from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Cases, Chance, Users, CaseOpening
import random
import json

@login_required
@csrf_exempt
def open_case(request, case_id):
    """
    API для открытия кейса
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешен'})
    
    try:

        case = get_object_or_404(Cases, id=case_id)

        try:
            user_profile = Users.objects.get(user=request.user)
        except Users.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Профиль не найден'})

        if user_profile.balance < case.price:
            return JsonResponse({'success': False, 'error': 'Недостаточно средств'})

        chances = Chance.objects.filter(cases=case).select_related('item')
        
        if not chances.exists():
            return JsonResponse({'success': False, 'error': 'В этом кейсе нет предметов'})

        items_with_chances = []
        for chance in chances:
            items_with_chances.append({
                'item': chance.item,
                'chance': float(chance.chance)
            })
        

        selected_item = select_item_by_chance(items_with_chances)
        
        if not selected_item:
            return JsonResponse({'success': False, 'error': 'Ошибка при выборе предмета'})

        user_profile.balance -= case.price
        user_profile.save()
  
        opening = CaseOpening.objects.create(
            user=user_profile,
            case=case,
            item=selected_item
        )
        

        rarity_class = get_rarity_class(selected_item.rarity)
        rarity_name = get_rarity_name(selected_item.rarity)
        
        return JsonResponse({
            'success': True,
            'item': {
                'id': selected_item.id,
                'name': selected_item.name,
                'price': float(selected_item.price),
                'rarity': selected_item.rarity,
                'rarity_class': rarity_class,
                'rarity_name': rarity_name,
                'is_stattrack': selected_item.is_stattrack,
                'image': get_item_image(selected_item)
            },
            'new_balance': user_profile.balance,
            'case_price': case.price
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def select_item_by_chance(items_with_chances):
    """
    Выбирает предмет на основе шансов
    """
    total_chance = sum(item['chance'] for item in items_with_chances)
    

    if total_chance != 100:
        for item in items_with_chances:
            item['chance'] = (item['chance'] / total_chance) * 100
    

    random_value = random.uniform(0, 100)
    cumulative = 0
    
    for item in items_with_chances:
        cumulative += item['chance']
        if random_value <= cumulative:
            return item['item']
    
    return items_with_chances[0]['item'] if items_with_chances else None

def get_rarity_class(rarity):
    """Возвращает CSS класс для редкости"""
    rarity_map = {
        'common': 'common',
        'rare': 'rare',
        'epic': 'epic',
        'legendary': 'legendary',
        'ancient': 'ancient'
    }
    return rarity_map.get(rarity.lower(), 'common')

def get_rarity_name(rarity):
    """Возвращает название редкости на русском"""
    rarity_map = {
        'common': 'Обычный',
        'rare': 'Редкий',
        'epic': 'Эпический',
        'legendary': 'Легендарный',
        'ancient': 'Древний'
    }
    return rarity_map.get(rarity.lower(), rarity)

def get_item_image(item):
    """Возвращает иконку для предмета (заглушка)"""
    if 'нож' in item.name.lower():
        return 'fa-crosshairs'
    elif 'перчатки' in item.name.lower():
        return 'fa-hand-paper'
    elif 'ak' in item.name.lower() or 'awp' in item.name.lower():
        return 'fa-gun'
    else:
        return 'fa-cube'

@login_required
def case_history(request, case_id):
    """
    API для получения истории открытий кейса
    """
    try:
        case = get_object_or_404(Cases, id=case_id)
        openings = CaseOpening.objects.filter(case=case).select_related('user', 'item').order_by('-opened_at')[:20]
        
        history = []
        for opening in openings:
            history.append({
                'username': opening.user.display_name if opening.user else 'Аноним',
                'item_name': opening.item.name,
                'item_price': float(opening.item.price),
                'rarity': opening.item.rarity,
                'time_ago': time_ago(opening.opened_at)
            })
        
        return JsonResponse({
            'success': True,
            'history': history
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def time_ago(dt):
    """Возвращает сколько времени прошло"""
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 0:
        return f'{diff.days} дн. назад'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'{hours} ч. назад'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'{minutes} мин. назад'
    else:
        return 'только что'
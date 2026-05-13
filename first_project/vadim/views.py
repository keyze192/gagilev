from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from .models import Cases, Chance, Items, Users, Upgrade, Contract
from .steam import SteamAPI
import secrets
import string

def index(request):
    all_cases = Cases.objects.all()
    popular_cases = all_cases[:100]
    context = {
        'popular_cases': popular_cases,
    }
    return render(request, 'main.html', context)

@csrf_exempt
def steam_login(request):
    steam_api = SteamAPI()
    login_url = steam_api.get_login_url()
    return redirect(login_url)

@csrf_exempt
def steam_callback(request):
    steam_api = SteamAPI()
    steam_id = steam_api.validate_steam_response(request)
    
    if not steam_id:
        messages.error(request, 'Ошибка авторизации через Steam')
        return redirect('main')
    
    player_data = steam_api.get_player_summary(steam_id)
    
    if not player_data:
        messages.error(request, 'Не удалось получить данные из Steam')
        return redirect('main')
    
    steam_username = player_data.get('personaname', f'steam_user_{steam_id[-6:]}')
    steam_avatar = player_data.get('avatarfull', '')
    steam_profile_url = player_data.get('profileurl', '')
    steam_realname = player_data.get('realname', '')
    steam_country = player_data.get('loccountrycode', '')
    steam_created_at = player_data.get('timecreated')
    
    try:

        user_profile = Users.objects.get(steam_id=steam_id)
        django_user = user_profile.user

        user_profile.steam_avatar = steam_avatar
        user_profile.steam_username = steam_username
        if steam_realname:
            user_profile.steam_realname = steam_realname
        if steam_country:
            user_profile.steam_country = steam_country
        user_profile.steam_profile_url = steam_profile_url
        user_profile.save()
        
        messages.success(request, f'С возвращением, {steam_username}!')
        
    except Users.DoesNotExist:

        base_username = f"steam_{steam_id[-8:]}"
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        alphabet = string.ascii_letters + string.digits + string.punctuation
        random_password = ''.join(secrets.choice(alphabet) for _ in range(32))

        django_user = User.objects.create_user(
            username=username,
            password=random_password,
            email=''
        )

        user_profile = Users.objects.create(
            user=django_user,
            user_name=username,
            email='',
            balance=1000,
            trade_link='',
            is_admin=False,
            steam_id=steam_id,
            steam_username=steam_username,
            steam_avatar=steam_avatar,
            steam_profile_url=steam_profile_url,
            steam_realname=steam_realname,
            steam_country=steam_country,
            steam_created_at=steam_created_at
        )
        
        messages.success(request, f'Добро пожаловать, {steam_username}! Вам начислено 1000 ₽')

    login(request, django_user)
    
    return redirect('main')

@login_required
def profile_view(request):
    try:
        user_profile = Users.objects.get(user=request.user)
    except Users.DoesNotExist:

        user_profile = Users.objects.create(
            user=request.user,
            user_name=request.user.username,
            balance=1000,
            trade_link=''
        )
    
    context = {
        'profile': user_profile,
        'steam_connected': user_profile.steam_id is not None,
        'steam_data': {
            'username': user_profile.steam_username,
            'avatar': user_profile.steam_avatar,
            'profile_url': user_profile.steam_profile_url,
            'realname': user_profile.steam_realname,
            'country': user_profile.steam_country,
            'steam_id': user_profile.steam_id,
            'created_at': user_profile.steam_created_at,
        } if user_profile.steam_id else None
    }
    
    return render(request, 'profile.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы.')
    return redirect('main')

def upgrade_page(request):
    return render(request, 'upgrade.html')

def contract_page(request):
    return render(request, 'contract.html')

def case_detail(request, case_id):
    case = get_object_or_404(Cases, id=case_id)
    
    chances = Chance.objects.filter(cases=case).select_related('item')
    
    items_by_rarity = {}
    for chance in chances:
        rarity = chance.item.rarity.lower()
        if rarity not in items_by_rarity:
            items_by_rarity[rarity] = []
        items_by_rarity[rarity].append({
            'item': chance.item,
            'chance': chance.chance,
            'price': chance.item.price,
            'is_stattrack': chance.item.is_stattrack
        })
    
    context = {
        'case': case,
        'chances': chances,
        'items_by_rarity': items_by_rarity,
        'total_items': chances.count(),
    }
    
    return render(request, 'case_detail.html', context)

def filter_cases(request):
    if request.method == 'GET':
        search = request.GET.get('search', '').strip()
        price_filter = request.GET.get('price', 'all')
        rarity_filter = request.GET.get('rarity', 'all')
        sort_by = request.GET.get('sort', 'popular')
        
        cases = Cases.objects.all()
        
        if search:
            cases = cases.filter(name__icontains=search)
        
        if price_filter != 'all':
            if price_filter == '0-500':
                cases = cases.filter(price__lte=500)
            elif price_filter == '500-1000':
                cases = cases.filter(price__gt=500, price__lte=1000)
            elif price_filter == '1000-5000':
                cases = cases.filter(price__gt=1000, price__lte=5000)
            elif price_filter == '5000+':
                cases = cases.filter(price__gt=5000)
        
        if sort_by == 'price-asc':
            cases = cases.order_by('price')
        elif sort_by == 'price-desc':
            cases = cases.order_by('-price')
        elif sort_by == 'name':
            cases = cases.order_by('name')
        
        cases_data = []
        for case in cases:
            case_data = {
                'id': case.id,
                'name': case.name,
                'price': case.price,
                'description': case.description,
                'image_url': case.image.url if case.image else None,
                'url': f'/case/{case.id}/'
            }
            cases_data.append(case_data)
        
        return JsonResponse({
            'success': True,
            'cases': cases_data,
            'count': len(cases_data)
        })
    
    return JsonResponse({'success': False, 'error': 'Метод не разрешен'})
def login_redirect(request):
    return redirect('steam_login')

def register_redirect(request):
    return redirect('steam_login')
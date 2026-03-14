from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from .models import Cases, Chance, Items, Users, Upgrade, Contract
from .steam import SteamAPI

def index(request):
    all_cases = Cases.objects.all()
    popular_cases = all_cases[:100]
    context = {
        'popular_cases': popular_cases,
    }
    return render(request, 'main.html', context)

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            try:
                user_profile = Users.objects.get(user_name=user.username)
                if user_profile.email != user.email:
                    user_profile.email = user.email
                    user_profile.save()
            except Users.DoesNotExist:
                user_profile = Users.objects.create(
                    user_name=user.username,
                    email=user.email,
                    balance=1000,
                    trade_link=''
                )
            except Exception as e:
                try:
                    user_profile = Users.objects.create(
                        user_name=user.username,
                        balance=1000,
                        trade_link=''
                    )
                except:
                    pass
            
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('main')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    return render(request, 'login.html')

@csrf_protect
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'register.html')
        
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с такой почтой уже существует.')
            return render(request, 'register.html')
        user = User.objects.create_user(
            username=username,
            email=email if email else '',
            password=password
        )
        try:
            Users.objects.create(
                user_name=username,
                email=email if email else '',
                balance=1000,
                trade_link=''
            )
        except Exception as e:
            try:
                Users.objects.create(
                    user_name=username,
                    balance=1000,
                    trade_link=''
                )
            except:
                pass
        login(request, user)
        messages.success(request, 'Регистрация прошла успешно! Вам начислено 1000 ₽')
        return redirect('main')
    
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы.')
    return redirect('main')

@login_required
def profile_view(request):
    try:
        user_profile = Users.objects.get(user_name=request.user.username)
    except Users.DoesNotExist:
        try:
            user_profile = Users.objects.create(
                user_name=request.user.username,
                email=request.user.email if request.user.email else '',
                balance=1000,
                trade_link=''
            )
        except:
            user_profile = None
    except:
        user_profile = None
    
    context = {
        'profile': user_profile,
    }
    
    return render(request, 'profile.html', context)

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
def steam_login(request):
    """
    Перенаправляет пользователя на Steam для авторизации
    """
    steam_api = SteamAPI()
    login_url = steam_api.get_login_url()
    return redirect(login_url)

@csrf_exempt
def steam_callback(request):
    """
    Обрабатывает callback от Steam после авторизации
    """
    steam_api = SteamAPI()
    steam_id = steam_api.validate_steam_response(request)
    
    if not steam_id:
        messages.error(request, 'Ошибка авторизации через Steam')
        return redirect('login')
    player_data = steam_api.get_player_summary(steam_id)
    
    if not player_data:
        messages.error(request, 'Не удалось получить данные из Steam')
        return redirect('login')
    steam_username = player_data.get('personaname', f'steam_user_{steam_id[-6:]}')
    steam_avatar = player_data.get('avatarfull', '')
    steam_profile_url = player_data.get('profileurl', '')
    try:
        user_profile = Users.objects.get(steam_id=steam_id)
        django_user = User.objects.get(username=user_profile.user_name)
    except Users.DoesNotExist:
        base_username = f"steam_{steam_id[-8:]}"
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        django_user = User.objects.create_user(
            username=username,
            password=User.objects.make_random_password(),  
            email=''
        )
        user_profile = Users.objects.create(
            user_name=username,
            email='',
            balance=1000,
            trade_link='',
            is_admin=False,
            steam_id=steam_id,
            steam_avatar=steam_avatar,
            steam_profile_url=steam_profile_url
        )
        
        messages.success(request, f'Добро пожаловать, {steam_username}! Вам начислено 1000 ₽')
    login(request, django_user)
    if user_profile.steam_avatar != steam_avatar:
        user_profile.steam_avatar = steam_avatar
        user_profile.steam_profile_url = steam_profile_url
        user_profile.save()
    
    return redirect('main')

def steam_disconnect(request):
    """
    Отвязывает Steam аккаунт от профиля
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        user_profile = Users.objects.get(user_name=request.user.username)
        user_profile.steam_id = None
        user_profile.steam_avatar = None
        user_profile.steam_profile_url = None
        user_profile.save()
        messages.success(request, 'Steam аккаунт успешно отвязан')
    except Users.DoesNotExist:
        messages.error(request, 'Профиль не найден')
    
    return redirect('profile')
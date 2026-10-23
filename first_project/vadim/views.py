from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Users
from .steam import SteamAPI
import secrets
import string


FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')


@csrf_exempt
def steam_login(request):
    steam_api = SteamAPI()
    return redirect(steam_api.get_login_url())


@csrf_exempt
def steam_callback(request):
    steam_api = SteamAPI()
    steam_id = steam_api.validate_steam_response(request)

    if not steam_id:
        return redirect(FRONTEND_URL + "/?error=auth")

  
    player_data = steam_api.get_player_summary(steam_id)


    if not player_data:
        print("ВНИМАНИЕ: Steam API не ответил. Входим по заглушке.")
        player_data = {
            'personaname': f'Player_{steam_id[-6:]}',
            'avatarfull': '',
            'profileurl': f'https://steamcommunity.com/profiles/{steam_id}',
            'realname': '',
            'loccountrycode': '',
            'timecreated': None,
        }

    steam_username = player_data.get('personaname', f'steam_user_{steam_id[-6:]}')

    try:
        user_profile = Users.objects.get(steam_id=steam_id)
        django_user = user_profile.user

        user_profile.steam_avatar = player_data.get('avatarfull', '')
        user_profile.steam_username = steam_username
        if player_data.get('realname'):
            user_profile.steam_realname = player_data['realname']
        if player_data.get('loccountrycode'):
            user_profile.steam_country = player_data['loccountrycode']
        user_profile.steam_profile_url = player_data.get('profileurl', '')
        user_profile.save()

    except Users.DoesNotExist:
        base_username = f"steam_{steam_id[-8:]}"
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        alphabet = string.ascii_letters + string.digits
        random_password = ''.join(secrets.choice(alphabet) for _ in range(32))

        django_user = User.objects.create_user(
            username=username, password=random_password, email=''
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
            steam_avatar=player_data.get('avatarfull', ''),
            steam_profile_url=player_data.get('profileurl', ''),
            steam_realname=player_data.get('realname', ''),
            steam_country=player_data.get('loccountrycode', ''),
            steam_created_at=player_data.get('timecreated'),
        )
    login(request, django_user)
    request.session.save()

    return redirect(FRONTEND_URL)

@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect(FRONTEND_URL)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction

from .models import Users
from .serializers import UsersSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = (request.data.get('username') or '').strip()
    password = request.data.get('password') or ''
    email    = (request.data.get('email') or '').strip()

    if not username or not password:
        return Response({'error': 'Нужны логин и пароль'}, status=400)
    if len(username) < 3:
        return Response({'error': 'Логин минимум 3 символа'}, status=400)
    if len(password) < 6:
        return Response({'error': 'Пароль минимум 6 символов'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Такой логин уже занят'}, status=400)

    with transaction.atomic():
        dj_user = User.objects.create_user(username=username, password=password, email=email)
        profile = Users.objects.create(
            user=dj_user, user_name=username, email=email,
            balance=1000, trade_link='', is_admin=False,
        )
        token, _ = Token.objects.get_or_create(user=dj_user)

    return Response({'token': token.key, 'user': UsersSerializer(profile).data})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username') or ''
    password = request.data.get('password') or ''
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({'error': 'Неверный логин или пароль'}, status=400)
    profile = getattr(user, 'profile', None)
    if not profile:
        return Response({'error': 'Профиль не найден'}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': UsersSerializer(profile).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    Token.objects.filter(user=request.user).delete()
    return Response({'success': True})
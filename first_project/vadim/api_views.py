from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
import random

from .models import (
    Users, Items, Cases, Contract, Upgrade, Chance,
    CaseOpening, UserInventory
)
from .serializers import (
    UsersSerializer, UsersSelfUpdateSerializer, ItemsSerializer,
    CasesSerializer, CasesListSerializer,
    ChanceSerializer, ContractSerializer, UpgradeSerializer,
    CaseOpeningSerializer, UserInventorySerializer,
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin



class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user_name', 'steam_username', 'steam_id']
    ordering_fields = ['balance', 'created_at']
    filterset_fields = ['is_admin']

    def get_queryset(self):
        qs = Users.objects.all()
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return qs
        profile = getattr(user, 'profile', None)
        if profile and profile.is_admin:
            return qs
        if profile:
            return qs.filter(pk=profile.pk)
        return Users.objects.none()

    def get_serializer_class(self):

        if self.action in ('update', 'partial_update'):
            user = self.request.user
            profile = getattr(user, 'profile', None)
            if not (user.is_staff or (profile and profile.is_admin)):
                return UsersSelfUpdateSerializer
        return UsersSerializer

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'detail': 'Профиль не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        if request.method == 'PATCH':
            serializer = UsersSelfUpdateSerializer(
                profile, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(UsersSerializer(profile).data)

class ItemsViewSet(viewsets.ModelViewSet):
    queryset = Items.objects.all()
    serializer_class = ItemsSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['price', 'name']
    filterset_fields = ['rarity', 'is_stattrack']


class CasesViewSet(viewsets.ModelViewSet):
    queryset = Cases.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name']
    filterset_fields = ['price']

    def get_serializer_class(self):
        if self.action == 'list':
            return CasesListSerializer
        return CasesSerializer

    @action(detail=True, methods=['get'])
    def chances(self, request, pk=None):
        case = self.get_object()
        chances = Chance.objects.filter(cases=case).select_related('item')
        serializer = ChanceSerializer(chances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        case = self.get_object()
        openings = CaseOpening.objects.filter(case=case).select_related(
            'user', 'item'
        ).order_by('-opened_at')[:20]
        serializer = CaseOpeningSerializer(openings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def open(self, request, pk=None):
        case = self.get_object()
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return Response({'error': 'Профиль не найден'}, status=400)

        chances = list(
            Chance.objects.filter(cases=case).select_related('item')
        )
        if not chances:
            return Response({'error': 'В кейсе нет предметов'}, status=400)

        with transaction.atomic():

            profile = Users.objects.select_for_update().get(pk=user_profile.pk)

            if profile.balance < case.price:
                return Response({'error': 'Недостаточно средств'}, status=400)

            total = sum(float(c.chance) for c in chances)
            r = random.uniform(0, total)
            cumulative = 0.0
            chosen = chances[-1].item
            for c in chances:
                cumulative += float(c.chance)
                if r <= cumulative:
                    chosen = c.item
                    break

            profile.balance -= case.price
            profile.save()

            CaseOpening.objects.create(user=profile, case=case, item=chosen)
            inv, created = UserInventory.objects.get_or_create(
                user=profile, item=chosen, defaults={'quantity': 1}
            )
            if not created:
                inv.quantity += 1
                inv.save()

        all_items = [
            ItemsSerializer(c.item).data for c in chances
        ]
        return Response({
            'success': True,
            'item': ItemsSerializer(chosen).data,
            'all_items': all_items,
            'new_balance': float(profile.balance),
        })



class ChanceViewSet(viewsets.ModelViewSet):
    queryset = Chance.objects.select_related('item', 'cases').all()
    serializer_class = ChanceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cases', 'item']


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related('user', 'item').all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'item']
    ordering_fields = ['amount']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        profile = getattr(user, 'profile', None)
        if profile and profile.is_admin:
            return self.queryset
        if profile:
            return self.queryset.filter(user=profile)
        return Contract.objects.none()



class UpgradeViewSet(viewsets.ModelViewSet):
    queryset = Upgrade.objects.select_related('user', 'item').all()
    serializer_class = UpgradeSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'item']
    ordering_fields = ['amount']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        profile = getattr(user, 'profile', None)
        if profile and profile.is_admin:
            return self.queryset
        if profile:
            return self.queryset.filter(user=profile)
        return Upgrade.objects.none()


class CaseOpeningViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CaseOpening.objects.select_related('user', 'case', 'item').all()
    serializer_class = CaseOpeningSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'case', 'item']
    ordering_fields = ['opened_at']



class UserInventoryViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = UserInventory.objects.select_related('user', 'item').all()
    serializer_class = UserInventorySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'item']
    ordering_fields = ['obtained_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        profile = getattr(user, 'profile', None)
        if profile and profile.is_admin:
            return self.queryset
        if profile:
            return self.queryset.filter(user=profile)
        return UserInventory.objects.none()

    @action(detail=True, methods=['post'])
    def sell(self, request, pk=None):

        inv = self.get_object()
        user_profile = inv.user
        sell_price = inv.item.price  

        with transaction.atomic():
            profile = Users.objects.select_for_update().get(pk=user_profile.pk)
            if inv.quantity > 1:
                inv.quantity -= 1
                inv.save()
            else:
                inv.delete()
            profile.balance += int(sell_price)
            profile.save()

        return Response({
            'success': True,
            'sold_price': float(sell_price),
            'new_balance': float(profile.balance),
        })

    @action(detail=False, methods=['post'], url_path='sell-all')
    def sell_all(self, request):

        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return Response({'error': 'Профиль не найден'}, status=400)

        with transaction.atomic():
            profile = Users.objects.select_for_update().get(pk=user_profile.pk)
            items = UserInventory.objects.select_related('item').filter(user=profile)
            total_price = 0
            count = 0
            for inv in items:
                total_price += int(inv.item.price) * inv.quantity
                count += inv.quantity
            items.delete()
            profile.balance += total_price
            profile.save()

        return Response({
            'success': True,
            'items_count': count,
            'total_price': total_price,
            'new_balance': float(profile.balance),
        })

    @action(detail=False, methods=['post'], url_path='upgrade')
    def upgrade(self, request):
        """POST /api/v1/inventory/upgrade/ — апгрейд предмета."""
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return Response({'error': 'Профиль не найден'}, status=400)

        inv_id = request.data.get('inventory_id')
        target_item_id = request.data.get('target_item_id')
        if not inv_id or not target_item_id:
            return Response({'error': 'Нужны inventory_id и target_item_id'}, status=400)

        try:
            target_item = Items.objects.get(id=target_item_id)
        except Items.DoesNotExist:
            return Response({'error': 'Целевой предмет не найден'}, status=404)

        with transaction.atomic():
            try:
                inv = UserInventory.objects.select_for_update().select_related('item').get(
                    id=inv_id, user=user_profile
                )
            except UserInventory.DoesNotExist:
                return Response({'error': 'Предмет не найден в инвентаре'}, status=404)

            inv_price = float(inv.item.price)
            target_price = float(target_item.price)

            if target_price <= inv_price:
                return Response(
                    {'error': 'Целевой предмет должен быть дороже'},
                    status=400
                )

            chance = min((inv_price / target_price) * 100, 90.0)
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

            inventory = UserInventory.objects.filter(
                user=user_profile
            ).select_related('item')

            inv_list = [
                {
                    'id': i.id,
                    'quantity': i.quantity,
                    'item_details': ItemsSerializer(i.item).data,
                }
                for i in inventory
            ]

        return Response({
            'success': True,
            'is_win': is_win,
            'chance': round(chance, 2),
            'new_balance': float(user_profile.balance),
            'inventory': inv_list,
        })
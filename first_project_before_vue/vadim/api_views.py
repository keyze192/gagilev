from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Users, Items, Cases, Contract, Upgrade, Chance,
    CaseOpening, UserInventory
)
from .serializers import (
    UsersSerializer, ItemsSerializer, CasesSerializer, CasesListSerializer,
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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'detail': 'Профиль не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


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


class UserInventoryViewSet(viewsets.ModelViewSet):
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
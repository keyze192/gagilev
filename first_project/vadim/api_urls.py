from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    UsersViewSet, ItemsViewSet, CasesViewSet, ChanceViewSet,
    ContractViewSet, UpgradeViewSet, CaseOpeningViewSet,
    UserInventoryViewSet,
)

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')
router.register(r'items', ItemsViewSet, basename='items')
router.register(r'cases', CasesViewSet, basename='cases')
router.register(r'chances', ChanceViewSet, basename='chances')
router.register(r'contracts', ContractViewSet, basename='contracts')
router.register(r'upgrades', UpgradeViewSet, basename='upgrades')
router.register(r'case-openings', CaseOpeningViewSet, basename='case-openings')
router.register(r'inventory', UserInventoryViewSet, basename='inventory')

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .auth_views import register, login_view, logout_view 

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
    path('auth/register/', register),
    path('auth/login/',    login_view),
    path('auth/logout/',   logout_view),
    path('', include(router.urls)),
]
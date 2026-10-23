from django.urls import path
from . import views, views_api

urlpatterns = [
    path('steam/login/', views.steam_login, name='steam_login'),
    path('steam/callback/', views.steam_callback, name='steam_callback'),
    path('logout/', views.logout_view, name='logout'),
    path('api/open-case/<int:case_id>/', views_api.open_case, name='api_open_case'),
    path('api/case-history/<int:case_id>/', views_api.case_history, name='api_case_history'),
    path('api/sell-item/<int:inventory_id>/', views_api.sell_item, name='api_sell_item'),
    path('api/sell-all-items/', views_api.sell_all_items, name='api_sell_all_items'),
    path('api/all-items/', views_api.get_all_items, name='api_all_items'),
    path('api/do-upgrade/', views_api.do_upgrade, name='api_do_upgrade'),
]
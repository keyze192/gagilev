from django.urls import path
from . import views
from . import views_api

urlpatterns = [
    path('', views.index, name='main'),
    path('upgrade/', views.upgrade_page, name='upgrade'),
    path('contract/', views.contract_page, name='contract'),
    path('case/<int:case_id>/', views.case_detail, name='case_detail'),
    path('filter-cases/', views.filter_cases, name='filter_cases'),
    

    path('steam/login/', views.steam_login, name='steam_login'),
    path('steam/callback/', views.steam_callback, name='steam_callback'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    

    path('login/', views.steam_login, name='login'),
    path('register/', views.steam_login, name='register'),
    

    path('api/open-case/<int:case_id>/', views_api.open_case, name='api_open_case'),
    path('api/case-history/<int:case_id>/', views_api.case_history, name='api_case_history'),
]
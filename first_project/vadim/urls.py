from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main'),
    path('upgrade/', views.upgrade_page, name='upgrade'),
    path('contract/', views.contract_page, name='contract'),
    path('case/<int:case_id>/', views.case_detail, name='case_detail'),
    path('filter-cases/', views.filter_cases, name='filter_cases'),
    

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    path('steam/login/', views.steam_login, name='steam_login'),
    path('steam/callback/', views.steam_callback, name='steam_callback'),
    path('steam/disconnect/', views.steam_disconnect, name='steam_disconnect'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main'),
    path('upgrade/', views.upgrade_page, name='upgrade'),
    path('contract/', views.contract_page, name='contract'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main'),
    path('upgrade/', views.upgrade_page, name='upgrade'),
    path('contract/', views.contract_page, name='contract'),
    path('case/<int:case_id>/', views.case_detail, name='case_detail'),
    path('filter-cases/', views.filter_cases, name='filter_cases'),  
]
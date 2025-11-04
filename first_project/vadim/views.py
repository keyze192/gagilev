from django.shortcuts import render, HttpResponse
from .models import *

def index(request):
    
    return render(request, 'index.html')
def index(request):
    
    return render(request, 'main.html')

def upgrade_page(request):
    
    return render(request, 'upgrade.html')

def contract_page(request):
    return render(request, 'contract.html')
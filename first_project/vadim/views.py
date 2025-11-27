from django.shortcuts import render
from .models import Cases

def index(request):
    all_cases = Cases.objects.all()
    

    print("=" * 50)
    print(f"НАЙДЕНО КЕЙСОВ В БАЗЕ: {all_cases.count()}")
    for case in all_cases:
        print(f"- {case.name}: {case.price} ₽")
    print("=" * 50)
    
 
    popular_cases = all_cases[:100]  

    
    context = {
        'popular_cases': popular_cases,
    }
    
    return render(request, 'main.html', context)

def upgrade_page(request):
    return render(request, 'upgrade.html')

def contract_page(request):
    return render(request, 'contract.html')
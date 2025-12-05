from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Cases, Chance, Items

def index(request):
    all_cases = Cases.objects.all()
    popular_cases = all_cases[:100]  
    
    context = {
        'popular_cases': popular_cases,
    }
    return render(request, 'main.html', context)

def upgrade_page(request):
    return render(request, 'upgrade.html')

def contract_page(request):
    return render(request, 'contract.html')

def case_detail(request, case_id):
    case = get_object_or_404(Cases, id=case_id)
    
    chances = Chance.objects.filter(cases=case).select_related('item')
    
    items_by_rarity = {}
    for chance in chances:
        rarity = chance.item.rarity.lower()
        if rarity not in items_by_rarity:
            items_by_rarity[rarity] = []
        items_by_rarity[rarity].append({
            'item': chance.item,
            'chance': chance.chance,
            'price': chance.item.price,
            'is_stattrack': chance.item.is_stattrack
        })
    
    context = {
        'case': case,
        'chances': chances,
        'items_by_rarity': items_by_rarity,
        'total_items': chances.count(),
    }
    
    return render(request, 'case_detail.html', context)

def filter_cases(request):
    if request.method == 'GET':
        search = request.GET.get('search', '').strip()
        price_filter = request.GET.get('price', 'all')
        rarity_filter = request.GET.get('rarity', 'all')
        sort_by = request.GET.get('sort', 'popular')
        
        cases = Cases.objects.all()
        
        if search:
            cases = cases.filter(name__icontains=search)
        
        if price_filter != 'all':
            if price_filter == '0-500':
                cases = cases.filter(price__lte=500)
            elif price_filter == '500-1000':
                cases = cases.filter(price__gt=500, price__lte=1000)
            elif price_filter == '1000-5000':
                cases = cases.filter(price__gt=1000, price__lte=5000)
            elif price_filter == '5000+':
                cases = cases.filter(price__gt=5000)
        
        if sort_by == 'price-asc':
            cases = cases.order_by('price')
        elif sort_by == 'price-desc':
            cases = cases.order_by('-price')
        elif sort_by == 'name':
            cases = cases.order_by('name')
        
        cases_data = []
        for case in cases:
            case_data = {
                'id': case.id,
                'name': case.name,
                'price': case.price,
                'description': case.description,
                'image_url': case.image.url if case.image else None,
                'url': f'/case/{case.id}/'
            }
            cases_data.append(case_data)
        
        return JsonResponse({
            'success': True,
            'cases': cases_data,
            'count': len(cases_data)
        })
    
    return JsonResponse({'success': False, 'error': 'Метод не разрешен'})
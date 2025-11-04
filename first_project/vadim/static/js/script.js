document.addEventListener('DOMContentLoaded', function() {
    //Элементы поиска
    const searchInput = document.getElementById('caseSearch');
    const clearSearch = document.querySelector('.clear-search');
    const filterReset = document.querySelector('.filter-reset-minimal');
    
    // Элементы фильтров
    const priceFilter = document.getElementById('priceFilter');
    const rarityFilter = document.getElementById('rarityFilter');
    const sortFilter = document.getElementById('sortFilter');
    
    // Контейнер для активных фильтров
    const activeFiltersContainer = document.querySelector('.active-filters-minimal');
    
    // Карточки кейсов
    const caseCards = document.querySelectorAll('.case-card');
    
    // Инициализация
    initFilters();

    // Очистка поиска
    if (searchInput && clearSearch) {
        searchInput.addEventListener('input', function() {
            clearSearch.style.display = this.value ? 'flex' : 'none';
            filterCases();
        });
        
        clearSearch.addEventListener('click', function() {
            searchInput.value = '';
            this.style.display = 'none';
            searchInput.focus();
            filterCases();
        });
    }
    
    // Сброс всех фильтров
    if (filterReset) {
        filterReset.addEventListener('click', function() {
            resetAllFilters();
        });
    }
    
    // Изменение фильтров
    if (priceFilter) {
        priceFilter.addEventListener('change', filterCases);
    }
    
    if (rarityFilter) {
        rarityFilter.addEventListener('change', filterCases);
    }
    
    if (sortFilter) {
        sortFilter.addEventListener('change', sortCases);
    }
    
    function initFilters() {
        updateActiveFilters();
    }
    
    function filterCases() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const priceValue = priceFilter ? priceFilter.value : 'all';
        const rarityValue = rarityFilter ? rarityFilter.value : 'all';
        
        caseCards.forEach(card => {
            const caseName = card.querySelector('.case-name').textContent.toLowerCase();
            const casePrice = parseInt(card.querySelector('.case-price').textContent);
            
            let matchesSearch = !searchTerm || caseName.includes(searchTerm);
            let matchesPrice = true;
            let matchesRarity = true;
            
            // Фильтрация по цене
            if (priceValue !== 'all') {
                switch (priceValue) {
                    case '0-500':
                        matchesPrice = casePrice <= 500;
                        break;
                    case '500-1000':
                        matchesPrice = casePrice > 500 && casePrice <= 1000;
                        break;
                    case '1000-5000':
                        matchesPrice = casePrice > 1000 && casePrice <= 5000;
                        break;
                    case '5000+':
                        matchesPrice = casePrice > 5000;
                        break;
                }
            }
            
            // Фильтрация по редкости (заглушка - можно расширить)
            if (rarityValue !== 'all') {
                // Здесь можно добавить логику для фильтрации по редкости
                // если добавите соответствующие классы или data-атрибуты к карточкам
            }
            
            // Показываем/скрываем карточку
            if (matchesSearch && matchesPrice && matchesRarity) {
                card.style.display = 'block';
                card.classList.add('visible');
                card.classList.remove('hidden');
            } else {
                card.style.display = 'none';
                card.classList.add('hidden');
                card.classList.remove('visible');
            }
        });
        
        updateActiveFilters();
    }
    
    function sortCases() {
        const sortValue = sortFilter.value;
        const casesContainer = document.querySelector('.cases-grid');
        const cards = Array.from(caseCards);
        
        cards.sort((a, b) => {
            const nameA = a.querySelector('.case-name').textContent;
            const nameB = b.querySelector('.case-name').textContent;
            const priceA = parseInt(a.querySelector('.case-price').textContent);
            const priceB = parseInt(b.querySelector('.case-price').textContent);
            
            switch (sortValue) {
                case 'price-asc':
                    return priceA - priceB;
                case 'price-desc':
                    return priceB - priceA;
                case 'name':
                    return nameA.localeCompare(nameB);
                case 'popular':
                default:
                    return 0;
            }
        });
        
        // Очищаем контейнер и добавляем отсортированные карточки
        casesContainer.innerHTML = '';
        cards.forEach(card => {
            casesContainer.appendChild(card);
        });
    }
    
    function updateActiveFilters() {
        if (!activeFiltersContainer) return;
        
        // Очищаем контейнер
        activeFiltersContainer.innerHTML = '';
        
        // Поиск
        if (searchInput && searchInput.value) {
            const searchTag = createFilterTag(`Поиск: "${searchInput.value}"`, () => {
                searchInput.value = '';
                if (clearSearch) clearSearch.style.display = 'none';
                filterCases();
            });
            activeFiltersContainer.appendChild(searchTag);
        }
        
        // Цена
        if (priceFilter && priceFilter.value !== 'all') {
            const priceText = getPriceFilterText(priceFilter.value);
            const priceTag = createFilterTag(`Цена: ${priceText}`, () => {
                priceFilter.value = 'all';
                filterCases();
            });
            activeFiltersContainer.appendChild(priceTag);
        }
        
        // Редкость
        if (rarityFilter && rarityFilter.value !== 'all') {
            const rarityText = rarityFilter.options[rarityFilter.selectedIndex].text;
            const rarityTag = createFilterTag(`Кейсы: ${rarityText}`, () => {
                rarityFilter.value = 'all';
                filterCases();
            });
            activeFiltersContainer.appendChild(rarityTag);
        }
    }
    
    function createFilterTag(text, onClick) {
        const tag = document.createElement('div');
        tag.className = 'filter-tag-minimal';
        
        const textSpan = document.createElement('span');
        textSpan.textContent = text;
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-filter';
        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
        removeBtn.addEventListener('click', onClick);
        
        tag.appendChild(textSpan);
        tag.appendChild(removeBtn);
        
        return tag;
    }
    
    function getPriceFilterText(value) {
        switch (value) {
            case '0-500': return 'до 500 ₽';
            case '500-1000': return '500-1000 ₽';
            case '1000-5000': return '1000-5000 ₽';
            case '5000+': return 'от 5000 ₽';
            default: return '';
        }
    }
    
    function resetAllFilters() {
        // Сброс поиска
        if (searchInput) {
            searchInput.value = '';
        }
        if (clearSearch) {
            clearSearch.style.display = 'none';
        }
        
        // Сброс фильтров
        if (priceFilter) priceFilter.value = 'all';
        if (rarityFilter) rarityFilter.value = 'all';
        if (sortFilter) sortFilter.value = 'popular';
        
        // Применение сброса
        filterCases();
        sortCases();
    }
    
    // Добавляем обработчики для кнопок "Открыть" в карточках
    caseCards.forEach(card => {
        const openBtn = card.querySelector('.btn');
        if (openBtn) {
            openBtn.addEventListener('click', function() {
                const caseName = card.querySelector('.case-name').textContent;
                const casePrice = card.querySelector('.case-price').textContent;
                console.log(`Открываем кейс: ${caseName} за ${casePrice}`);
                // Здесь можно добавить логику открытия кейса
                alert(`Открываем кейс: ${caseName} за ${casePrice}`);
            });
        }
    });
});


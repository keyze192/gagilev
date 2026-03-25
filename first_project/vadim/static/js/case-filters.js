class CaseFilter {
    constructor() {
        this.cases = []; 
        this.filteredCases = []; 
        this.init();
    }

    init() {
        this.cases = Array.from(document.querySelectorAll('.case-card'));
        this.filteredCases = [...this.cases];

        this.bindEvents();

        this.updateCaseCount();
    }

    bindEvents() {
        const searchInput = document.getElementById('caseSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }

        const priceFilter = document.getElementById('priceFilter');
        if (priceFilter) {
            priceFilter.addEventListener('change', (e) => {
                this.handlePriceFilter(e.target.value);
            });
        }

        const rarityFilter = document.getElementById('rarityFilter');
        if (rarityFilter) {
            rarityFilter.addEventListener('change', (e) => {
                this.handleRarityFilter(e.target.value);
            });
        }

        const sortFilter = document.getElementById('sortFilter');
        if (sortFilter) {
            sortFilter.addEventListener('change', (e) => {
                this.handleSort(e.target.value);
            });
        }

        const resetBtn = document.querySelector('.filter-reset-minimal');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetFilters();
            });
        }

        const clearSearch = document.querySelector('.clear-search');
        if (clearSearch) {
            clearSearch.addEventListener('click', () => {
                const searchInput = document.getElementById('caseSearch');
                if (searchInput) {
                    searchInput.value = '';
                    this.handleSearch('');
                }
            });
        }
    }

    handleSearch(query) {
        const searchTerm = query.toLowerCase().trim();
        
        this.filteredCases = this.cases.filter(caseCard => {
            const caseName = caseCard.querySelector('.case-name')?.textContent.toLowerCase() || '';
            return searchTerm === '' || caseName.includes(searchTerm);
        });

        this.applyAllFilters();
    }

    handlePriceFilter(priceRange) {
        this.currentPriceRange = priceRange;
        
        this.filteredCases = this.cases.filter(caseCard => {
            const priceElement = caseCard.querySelector('.case-price');
            const price = parseInt(priceElement?.textContent.replace(/[^0-9]/g, '')) || 0;
            
            switch(priceRange) {
                case '0-500':
                    return price <= 500;
                case '500-1000':
                    return price > 500 && price <= 1000;
                case '1000-5000':
                    return price > 1000 && price <= 5000;
                case '5000+':
                    return price > 5000;
                default:
                    return true;
            }
        });

        this.applyAllFilters();
    }

    handleRarityFilter(rarity) {
        this.currentRarity = rarity;
        
        this.filteredCases = this.cases.filter(caseCard => {
            if (rarity === 'all') return true;

            const caseRarity = caseCard.dataset.rarity || 'common';
            return caseRarity === rarity;
        });

        this.applyAllFilters();
    }

    applyAllFilters() {
        let result = [...this.cases];

        const searchTerm = document.getElementById('caseSearch')?.value.toLowerCase().trim() || '';
        if (searchTerm) {
            result = result.filter(caseCard => {
                const caseName = caseCard.querySelector('.case-name')?.textContent.toLowerCase() || '';
                return caseName.includes(searchTerm);
            });
        }

        if (this.currentPriceRange && this.currentPriceRange !== 'all') {
            result = result.filter(caseCard => {
                const priceElement = caseCard.querySelector('.case-price');
                const price = parseInt(priceElement?.textContent.replace(/[^0-9]/g, '')) || 0;
                
                switch(this.currentPriceRange) {
                    case '0-500':
                        return price <= 500;
                    case '500-1000':
                        return price > 500 && price <= 1000;
                    case '1000-5000':
                        return price > 1000 && price <= 5000;
                    case '5000+':
                        return price > 5000;
                    default:
                        return true;
                }
            });
        }

        if (this.currentRarity && this.currentRarity !== 'all') {
            result = result.filter(caseCard => {
                const caseRarity = caseCard.dataset.rarity || 'common';
                return caseRarity === this.currentRarity;
            });
        }
        
        this.filteredCases = result;

        this.applySort(this.currentSort || 'popular');

        this.renderCases();

        this.updateActiveFilters();
    }

    handleSort(sortType) {
        this.currentSort = sortType;
        this.applySort(sortType);
        this.renderCases();
    }

    applySort(sortType) {
        if (sortType === 'popular') return;
        
        this.filteredCases.sort((a, b) => {
            const priceA = parseInt(a.querySelector('.case-price')?.textContent.replace(/[^0-9]/g, '')) || 0;
            const priceB = parseInt(b.querySelector('.case-price')?.textContent.replace(/[^0-9]/g, '')) || 0;
            const nameA = a.querySelector('.case-name')?.textContent.toLowerCase() || '';
            const nameB = b.querySelector('.case-name')?.textContent.toLowerCase() || '';
            
            switch(sortType) {
                case 'price-asc':
                    return priceA - priceB;
                case 'price-desc':
                    return priceB - priceA;
                case 'name':
                    return nameA.localeCompare(nameB);
                default:
                    return 0;
            }
        });
    }

    renderCases() {
        this.cases.forEach(caseCard => {
            caseCard.classList.add('hidden');
            caseCard.classList.remove('visible');
        });

        this.filteredCases.forEach(caseCard => {
            caseCard.classList.remove('hidden');
            caseCard.classList.add('visible');
        });

        this.showNoResultsMessage();

        this.updateCaseCount();
    }

    showNoResultsMessage() {
        const noResultsDiv = document.getElementById('noResults');
        if (noResultsDiv) {
            if (this.filteredCases.length === 0) {
                noResultsDiv.style.display = 'block';
            } else {
                noResultsDiv.style.display = 'none';
            }
        }
    }

    updateCaseCount() {
        const countElement = document.querySelector('.cases-count');
        if (countElement) {
            countElement.textContent = this.filteredCases.length;
        }
    }

    updateActiveFilters() {
        const activeFiltersContainer = document.querySelector('.active-filters-minimal');
        if (!activeFiltersContainer) return;
        
        activeFiltersContainer.innerHTML = '';
        
        const searchTerm = document.getElementById('caseSearch')?.value.trim();
        if (searchTerm) {
            this.addFilterTag('Поиск: ' + searchTerm, 'search');
        }
        
        if (this.currentPriceRange && this.currentPriceRange !== 'all') {
            let priceText = '';
            switch(this.currentPriceRange) {
                case '0-500': priceText = 'До 500 ₽'; break;
                case '500-1000': priceText = '500-1000 ₽'; break;
                case '1000-5000': priceText = '1000-5000 ₽'; break;
                case '5000+': priceText = 'От 5000 ₽'; break;
            }
            this.addFilterTag('Цена: ' + priceText, 'price');
        }
        
        if (this.currentRarity && this.currentRarity !== 'all') {
            let rarityText = '';
            switch(this.currentRarity) {
                case 'common': rarityText = 'Обычные'; break;
                case 'rare': rarityText = 'Редкие'; break;
                case 'epic': rarityText = 'Эпические'; break;
                case 'legendary': rarityText = 'Легендарные'; break;
                case 'ancient': rarityText = 'Древние'; break;
            }
            this.addFilterTag('Редкость: ' + rarityText, 'rarity');
        }
    }

    addFilterTag(text, type) {
        const container = document.querySelector('.active-filters-minimal');
        if (!container) return;
        
        const tag = document.createElement('div');
        tag.className = 'filter-tag-minimal';
        tag.innerHTML = `
            ${text}
            <button class="remove-filter" data-filter-type="${type}">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        const removeBtn = tag.querySelector('.remove-filter');
        removeBtn.addEventListener('click', () => {
            this.removeFilter(type);
        });
        
        container.appendChild(tag);
    }

    removeFilter(type) {
        switch(type) {
            case 'search':
                const searchInput = document.getElementById('caseSearch');
                if (searchInput) searchInput.value = '';
                this.handleSearch('');
                break;
            case 'price':
                const priceFilter = document.getElementById('priceFilter');
                if (priceFilter) priceFilter.value = 'all';
                this.handlePriceFilter('all');
                break;
            case 'rarity':
                const rarityFilter = document.getElementById('rarityFilter');
                if (rarityFilter) rarityFilter.value = 'all';
                this.handleRarityFilter('all');
                break;
        }
    }

    resetFilters() {
        const searchInput = document.getElementById('caseSearch');
        if (searchInput) searchInput.value = '';
        
        const priceFilter = document.getElementById('priceFilter');
        if (priceFilter) priceFilter.value = 'all';
        
        const rarityFilter = document.getElementById('rarityFilter');
        if (rarityFilter) rarityFilter.value = 'all';
        
        const sortFilter = document.getElementById('sortFilter');
        if (sortFilter) sortFilter.value = 'popular';
        

        this.currentPriceRange = 'all';
        this.currentRarity = 'all';
        this.currentSort = 'popular';
        

        this.filteredCases = [...this.cases];
        this.renderCases();

        const activeFiltersContainer = document.querySelector('.active-filters-minimal');
        if (activeFiltersContainer) {
            activeFiltersContainer.innerHTML = '';
        }
    }
}
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.cases-grid')) {
        new CaseFilter();
    }
});
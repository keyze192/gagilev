// Настройки сайта - валюты и темы
class SiteSettings {
    constructor() {
        // Курсы валют (относительно RUB)
        this.exchangeRates = {
            'RUB': 1,
            'USD': 0.011,    // 1 RUB = 0.011 USD
            'EUR': 0.010,    // 1 RUB = 0.010 EUR
            'CNY': 0.079,    // 1 RUB = 0.079 CNY
            'BTC': 0.00000012, // Биткоин
            'ETH': 0.0000018,  // Эфириум
            'TON': 0.0009      // Toncoin
        };
        
        // Символы валют
        this.currencySymbols = {
            'RUB': '₽',
            'USD': '$',
            'EUR': '€',
            'CNY': '¥',
            'BTC': '₿',
            'ETH': 'Ξ',
            'TON': '⍎'
        };
        
        // Названия валют
        this.currencyNames = {
            'RUB': 'Рубль',
            'USD': 'Доллар',
            'EUR': 'Евро',
            'CNY': 'Юань',
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'TON': 'Toncoin'
        };
        
        // Текущие настройки
        this.currentCurrency = localStorage.getItem('selectedCurrency') || 'RUB';
        this.currentTheme = localStorage.getItem('siteTheme') || 'dark';
        
        this.init();
    }
    
    init() {
        this.loadExchangeRates();
        this.applyTheme();
        this.setupCurrencySelector();
        this.setupThemeToggle();
        this.convertAllPrices();
        
        // Слушаем изменения на странице (для динамически добавляемых элементов)
        this.observeDOMChanges();
    }
    
    // Загрузка актуальных курсов валют (опционально)
    async loadExchangeRates() {
        try {
            // Можно использовать бесплатное API для курсов
            // Например: https://api.exchangerate-api.com/v4/latest/RUB
            const response = await fetch('https://api.exchangerate-api.com/v4/latest/RUB');
            if (response.ok) {
                const data = await response.json();
                if (data.rates) {
                    this.exchangeRates['USD'] = data.rates.USD || 0.011;
                    this.exchangeRates['EUR'] = data.rates.EUR || 0.010;
                    this.exchangeRates['CNY'] = data.rates.CNY || 0.079;
                }
            }
        } catch (error) {
            console.log('Использую локальные курсы валют');
        }
    }
    
    // Конвертация цены
    convertPrice(priceRUB) {
        const rate = this.exchangeRates[this.currentCurrency];
        if (!rate) return priceRUB;
        return (priceRUB * rate).toFixed(2);
    }
    
    // Получить символ валюты
    getCurrencySymbol() {
        return this.currencySymbols[this.currentCurrency] || '₽';
    }
    
    // Конвертация всех цен на странице
    convertAllPrices() {
        const priceElements = document.querySelectorAll('.case-price, .item-price, .balance-amount, .preview-price, .button-price, .detail-value, .history-item-price, .item-price-large');
        
        priceElements.forEach(element => {
            // Парсим текущее значение
            let originalValue = element.getAttribute('data-rub-value');
            
            if (!originalValue) {
                const text = element.textContent;
                const match = text.match(/(\d+(?:\.\d+)?)/);
                if (match) {
                    originalValue = parseFloat(match[1]);
                    element.setAttribute('data-rub-value', originalValue);
                }
            }
            
            if (originalValue) {
                const converted = this.convertPrice(parseFloat(originalValue));
                const symbol = this.getCurrencySymbol();
                
                // Сохраняем оригинальное значение в атрибуте
                if (!element.hasAttribute('data-rub-value')) {
                    element.setAttribute('data-rub-value', originalValue);
                }
                
                // Обновляем отображение
                const oldText = element.textContent;
                const newText = oldText.replace(/[\d\.,]+(?:\s*[₽$€¥₿Ξ⍎]?)/, `${converted} ${symbol}`);
                element.textContent = newText;
            }
        });
    }
    
    // Смена валюты
    setCurrency(currencyCode) {
        this.currentCurrency = currencyCode;
        localStorage.setItem('selectedCurrency', currencyCode);
        this.convertAllPrices();
        this.updateCurrencyDisplay();
    }
    
    // Обновление отображения выбранной валюты в UI
    updateCurrencyDisplay() {
        const currencyBtn = document.querySelector('.currency-btn span');
        if (currencyBtn) {
            currencyBtn.textContent = this.currentCurrency;
        }
        
        // Обновляем любые другие элементы, показывающие валюту
        document.querySelectorAll('.currency-display').forEach(el => {
            el.textContent = this.currentCurrency;
        });
    }
    
    // Создание выпадающего меню выбора валюты
    setupCurrencySelector() {
        // Проверяем, не добавлено ли уже меню
        if (document.querySelector('.currency-selector')) return;
        
        const userActions = document.querySelector('.user-actions');
        if (!userActions) return;
        
        // Создаем контейнер для выбора валюты
        const currencyContainer = document.createElement('div');
        currencyContainer.className = 'currency-selector';
        currencyContainer.innerHTML = `
            <button class="currency-btn">
                <i class="fas fa-coins"></i>
                <span>${this.currentCurrency}</span>
                <i class="fas fa-chevron-down"></i>
            </button>
            <div class="currency-dropdown">
                <div class="currency-search">
                    <input type="text" placeholder="Поиск валюты..." id="currencySearch">
                </div>
                <div class="currency-list">
                    ${Object.keys(this.currencyNames).map(code => `
                        <div class="currency-option" data-currency="${code}">
                            <span class="currency-symbol">${this.currencySymbols[code]}</span>
                            <span class="currency-code">${code}</span>
                            <span class="currency-name">${this.currencyNames[code]}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Вставляем перед меню пользователя
        const balance = document.querySelector('.balance');
        if (balance) {
            balance.parentNode.insertBefore(currencyContainer, balance);
        } else {
            userActions.prepend(currencyContainer);
        }
        
        // Добавляем обработчики
        const currencyBtn = currencyContainer.querySelector('.currency-btn');
        const dropdown = currencyContainer.querySelector('.currency-dropdown');
        
        currencyBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('show');
        });
        
        // Поиск валют
        const searchInput = currencyContainer.querySelector('#currencySearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                const options = currencyContainer.querySelectorAll('.currency-option');
                options.forEach(option => {
                    const text = option.textContent.toLowerCase();
                    option.style.display = text.includes(searchTerm) ? 'flex' : 'none';
                });
            });
        }
        
        // Выбор валюты
        const options = currencyContainer.querySelectorAll('.currency-option');
        options.forEach(option => {
            option.addEventListener('click', () => {
                const currency = option.dataset.currency;
                this.setCurrency(currency);
                dropdown.classList.remove('show');
            });
        });
        
        // Закрытие при клике вне
        document.addEventListener('click', (e) => {
            if (!currencyContainer.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    }
    
    // ТЕМЫ
    applyTheme() {
        if (this.currentTheme === 'light') {
            document.body.classList.add('light-theme');
        } else {
            document.body.classList.remove('light-theme');
        }
    }
    
    setTheme(theme) {
        this.currentTheme = theme;
        localStorage.setItem('siteTheme', theme);
        this.applyTheme();
        this.updateThemeDisplay();
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }
    
    updateThemeDisplay() {
        const themeBtn = document.querySelector('.theme-toggle');
        if (themeBtn) {
            const icon = themeBtn.querySelector('i');
            if (this.currentTheme === 'dark') {
                icon.className = 'fas fa-moon';
                themeBtn.querySelector('span').textContent = 'Тёмная';
            } else {
                icon.className = 'fas fa-sun';
                themeBtn.querySelector('span').textContent = 'Светлая';
            }
        }
    }
    
    setupThemeToggle() {
        if (document.querySelector('.theme-toggle')) return;
        
        const userActions = document.querySelector('.user-actions');
        if (!userActions) return;
        
        const themeContainer = document.createElement('div');
        themeContainer.className = 'theme-toggle-container';
        themeContainer.innerHTML = `
            <button class="theme-toggle">
                <i class="fas ${this.currentTheme === 'dark' ? 'fa-moon' : 'fa-sun'}"></i>
                <span>${this.currentTheme === 'dark' ? 'Тёмная' : 'Светлая'}</span>
            </button>
        `;
        
        const currencySelector = document.querySelector('.currency-selector');
        if (currencySelector) {
            currencySelector.after(themeContainer);
        } else {
            userActions.prepend(themeContainer);
        }
        
        const themeBtn = themeContainer.querySelector('.theme-toggle');
        themeBtn.addEventListener('click', () => {
            this.toggleTheme();
        });
    }
    
    // Наблюдатель за изменениями DOM (для динамически добавляемых цен)
    observeDOMChanges() {
        const observer = new MutationObserver((mutations) => {
            let shouldConvert = false;
            mutations.forEach(mutation => {
                if (mutation.addedNodes.length) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1) { // Элемент
                            if (node.querySelector && node.querySelector('.case-price, .item-price')) {
                                shouldConvert = true;
                            }
                        }
                    });
                }
            });
            if (shouldConvert) {
                setTimeout(() => this.convertAllPrices(), 100);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.siteSettings = new SiteSettings();
});
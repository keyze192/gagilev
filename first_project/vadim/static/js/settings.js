class SiteSettings {
    constructor() {
        this.exchangeRates = {
            'RUB': 1,
            'USD': 0.011,
            'EUR': 0.010,
            'CNY': 0.079,
            'BTC': 0.00000012,
            'ETH': 0.0000018,
            'TON': 0.0009
        };

        this.currencySymbols = {
            'RUB': '₽',
            'USD': '$',
            'EUR': '€',
            'CNY': '¥',
            'BTC': '₿',
            'ETH': 'Ξ',
            'TON': '⍎'
        };

        this.currencyNames = {
            'RUB': 'Рубль',
            'USD': 'Доллар',
            'EUR': 'Евро',
            'CNY': 'Юань',
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'TON': 'Toncoin'
        };

        this.currentCurrency = localStorage.getItem('selectedCurrency') || 'RUB';
        this.currentTheme = localStorage.getItem('siteTheme') || 'dark';

        this.init();
    }

    init() {
        this.applyTheme();
        this.setupCurrencySelector();
        this.setupThemeToggle();
        this.convertAllPrices();
        this.observeDOMChanges();
    }

    convertPrice(priceRUB) {
        const rate = this.exchangeRates[this.currentCurrency];
        if (!rate || this.currentCurrency === 'RUB') {
            return Math.round(priceRUB);
        }
        return (priceRUB * rate).toFixed(2);
    }

    getCurrencySymbol() {
        return this.currencySymbols[this.currentCurrency] || '₽';
    }

    convertAllPrices() {
        const priceElements = document.querySelectorAll(
            '.case-price, .item-price, .balance-amount, .preview-price, .button-price, .detail-value, .history-item-price, .item-price-large, #userBalance, .case-price-large, #winNewBalance'
        );

        priceElements.forEach(el => {
            let original = el.getAttribute('data-rub-value');

            if (original === null) {
                const text = el.textContent;
                const match = text.match(/(\d+(?:\.\d+)?)/);
                if (match) {
                    original = parseFloat(match[1]);
                    el.setAttribute('data-rub-value', original);
                }
            }

            if (original !== null) {
                const val = parseFloat(original);
                const converted = this.convertPrice(val);
                el.textContent = `${converted} ${this.getCurrencySymbol()}`;
            }
        });
    }

    setCurrency(code) {
        this.currentCurrency = code;
        localStorage.setItem('selectedCurrency', code);
        this.convertAllPrices();
        this.updateCurrencyDisplay();
    }

    updateCurrencyDisplay() {
        const btn = document.querySelector('.currency-btn span');
        if (btn) btn.textContent = this.currentCurrency;
    }

    setupCurrencySelector() {
        if (document.querySelector('.currency-selector')) return;

        const userActions = document.querySelector('.user-actions');
        if (!userActions) return;

        const container = document.createElement('div');
        container.className = 'currency-selector';
        container.innerHTML = `
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

        const balance = document.querySelector('.balance');
        if (balance) {
            balance.parentNode.insertBefore(container, balance);
        } else {
            userActions.prepend(container);
        }

        const btn = container.querySelector('.currency-btn');
        const dropdown = container.querySelector('.currency-dropdown');

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('show');
        });

        const search = container.querySelector('#currencySearch');
        if (search) {
            search.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase();
                container.querySelectorAll('.currency-option').forEach(opt => {
                    opt.style.display = opt.textContent.toLowerCase().includes(term) ? 'flex' : 'none';
                });
            });
        }

        container.querySelectorAll('.currency-option').forEach(opt => {
            opt.addEventListener('click', () => {
                this.setCurrency(opt.dataset.currency);
                dropdown.classList.remove('show');
            });
        });

        document.addEventListener('click', (e) => {
            if (!container.contains(e.target)) dropdown.classList.remove('show');
        });
    }

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
        this.setTheme(this.currentTheme === 'dark' ? 'light' : 'dark');
    }

    updateThemeDisplay() {
        const btn = document.querySelector('.theme-toggle');
        if (!btn) return;
        const icon = btn.querySelector('i');
        const span = btn.querySelector('span');
        if (this.currentTheme === 'dark') {
            icon.className = 'fas fa-moon';
            span.textContent = 'Тёмная';
        } else {
            icon.className = 'fas fa-sun';
            span.textContent = 'Светлая';
        }
    }

    setupThemeToggle() {
        if (document.querySelector('.theme-toggle')) return;

        const userActions = document.querySelector('.user-actions');
        if (!userActions) return;

        const container = document.createElement('div');
        container.className = 'theme-toggle-container';
        container.innerHTML = `
            <button class="theme-toggle">
                <i class="fas ${this.currentTheme === 'dark' ? 'fa-moon' : 'fa-sun'}"></i>
                <span>${this.currentTheme === 'dark' ? 'Тёмная' : 'Светлая'}</span>
            </button>
        `;

        const selector = document.querySelector('.currency-selector');
        if (selector) {
            selector.after(container);
        } else {
            userActions.prepend(container);
        }

        container.querySelector('.theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });
    }

    observeDOMChanges() {
        const observer = new MutationObserver(() => {
            setTimeout(() => this.convertAllPrices(), 100);
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.siteSettings = new SiteSettings();
}); 
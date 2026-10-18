(function () {
    'use strict';

    const ROULETTE_ITEMS = 40;
    const WINNER_INDEX = 32;
    const ITEM_WIDTH = 150;
    const ANIM_DURATION = 6000;

    let isOpening = false;

    function init() {
        document.querySelectorAll('[data-open-case]').forEach(btn => {
            btn.addEventListener('click', onOpenClick);
        });
        document.querySelectorAll('[data-close-overlay]').forEach(btn => {
            btn.addEventListener('click', closeOverlay);
        });
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') closeOverlay();
        });
    }

    function onOpenClick(e) {
        const btn = e.currentTarget;
        const caseId = btn.dataset.caseId;
        const casePrice = parseInt(btn.dataset.casePrice) || 0;
        openCase(caseId, casePrice, btn);
    }

    async function openCase(caseId, casePrice, btn) {
        if (isOpening) return;
        isOpening = true;

        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Открываем...';

        try {
            const res = await fetch(`/api/open-case/${caseId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken') || '',
                    'Content-Type': 'application/json'
                }
            });

            const data = await res.json();

            if (!data.success) {
                if (data.need_auth) {
                    showToast(data.error, 'error');
                    setTimeout(() => window.location.href = '/steam/login/', 1200);
                } else {
                    showToast(data.error || 'Ошибка открытия', 'error');
                }
                return;
            }

            openOverlay();
            await runRoulette(data.all_items, data.item);
            showResult(data.item, data.new_balance);

            if (data.item.rarity === 'legendary' || data.item.rarity === 'ancient') {
                spawnConfetti();
            }

            updateAllBalances(data.new_balance);
            refreshHistory(caseId);

        } catch (err) {
            console.error(err);
            showToast('Произошла ошибка. Попробуйте позже.', 'error');
        } finally {
            isOpening = false;
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }

    function openOverlay() {
        const overlay = document.getElementById('caseOpeningOverlay');
        if (!overlay) return;
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        document.getElementById('rouletteStage').style.display = '';
        document.getElementById('winStage').classList.remove('active');
    }

    function closeOverlay() {
        const overlay = document.getElementById('caseOpeningOverlay');
        if (!overlay) return;
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    function runRoulette(allItems, winner) {
        return new Promise(resolve => {
            const track = document.getElementById('rouletteTrack');
            track.innerHTML = '';
            track.style.transition = 'none';
            track.style.transform = 'translateX(0)';

            if (!allItems || allItems.length === 0) return resolve();

            for (let i = 0; i < ROULETTE_ITEMS; i++) {
                const item = (i === WINNER_INDEX)
                    ? winner
                    : allItems[Math.floor(Math.random() * allItems.length)];
                track.appendChild(buildRouletteItem(item));
            }

            const stage = document.getElementById('rouletteStage');
            const stageWidth = stage.offsetWidth;
            const centerOffset = stageWidth / 2 - ITEM_WIDTH / 2;
            const shift = (Math.random() - 0.5) * (ITEM_WIDTH * 0.55);
            const finalX = -(WINNER_INDEX * ITEM_WIDTH) + centerOffset + shift;

            void track.offsetWidth;

            track.style.transition = `transform ${ANIM_DURATION}ms cubic-bezier(0.12, 0.8, 0.2, 1)`;
            track.style.transform = `translateX(${finalX}px)`;

            setTimeout(() => {
                const winnerEl = track.children[WINNER_INDEX];
                if (winnerEl) winnerEl.classList.add('winner-glow');
                setTimeout(resolve, 500);
            }, ANIM_DURATION);
        });
    }

    function buildRouletteItem(item) {
        const el = document.createElement('div');
        el.className = `roulette-item ${item.rarity_class || 'common'}`;
        el.innerHTML = `
            <div class="roulette-item-icon"><i class="fas ${item.icon || 'fa-cube'}"></i></div>
            <div class="roulette-item-name">${item.name}</div>
            <div class="roulette-item-price">${item.price} ₽</div>
        `;
        return el;
    }

    function showResult(item, newBalance) {
        const stage = document.getElementById('rouletteStage');
        const win = document.getElementById('winStage');
        if (!stage || !win) return;

        stage.style.display = 'none';

        document.getElementById('winItemIcon').className = `win-item-icon bg-${item.rarity_class}`;
        document.getElementById('winItemIcon').innerHTML = `<i class="fas ${item.icon || 'fa-cube'}"></i>`;

        const nameEl = document.getElementById('winItemName');
        nameEl.innerHTML = item.name + (item.is_stattrack
            ? ' <span class="stattrack-badge">StatTrak™</span>'
            : '');

        document.getElementById('winItemPrice').textContent = `${item.price} ₽`;
        document.getElementById('winItemRarity').textContent = item.rarity_name;
        document.getElementById('winItemRarity').className = `win-item-rarity ${item.rarity_class}`;

        win.classList.add('active');

        const card = win.querySelector('.win-card');
        if (card) card.classList.add('reveal');

        const balEl = document.getElementById('winNewBalance');
        if (balEl && newBalance !== undefined) balEl.textContent = `${newBalance} ₽`;
    }

    function updateAllBalances(newBalance) {
        document.querySelectorAll('.balance-amount, #userBalance, [data-balance]').forEach(el => {
            el.setAttribute('data-rub-value', newBalance);
            el.textContent = newBalance;
            if (window.siteSettings) {
                try { window.siteSettings.convertAllPrices(); } catch (e) {}
            }
        });
    }

    function refreshHistory(caseId) {
        const list = document.getElementById('historyList');
        if (!list || !caseId) return;
        loadCaseHistory(caseId);
    }

    async function loadCaseHistory(caseId) {
        const list = document.getElementById('historyList');
        if (!list) return;
        try {
            const res = await fetch(`/api/case-history/${caseId}/`);
            const data = await res.json();
            if (data.success && data.history.length) {
                list.innerHTML = data.history.map(h => `
                    <div class="history-item ${h.rarity}">
                        <div class="history-user">
                            <i class="fas fa-user-circle"></i>
                            <span>${h.username}</span>
                        </div>
                        <div class="history-item-info">
                            <span class="history-item-name">${h.item_name}</span>
                            <span class="history-item-price">${h.item_price} ₽</span>
                        </div>
                        <div class="history-time">
                            <i class="fas fa-clock"></i> ${h.time_ago}
                        </div>
                    </div>
                `).join('');
            } else {
                list.innerHTML = '<div class="no-history">Пока нет открытий этого кейса</div>';
            }
        } catch (e) {
            console.error(e);
        }
    }

    function spawnConfetti() {
        const colors = ['#ff4655', '#4cd964', '#f1c40f', '#9b59b6', '#e74c3c', '#ffd700'];
        const box = document.createElement('div');
        box.className = 'confetti';
        document.body.appendChild(box);

        for (let i = 0; i < 120; i++) {
            const p = document.createElement('div');
            p.className = 'confetti-piece';
            p.style.left = Math.random() * 100 + '%';
            p.style.background = colors[Math.floor(Math.random() * colors.length)];
            p.style.width = (Math.random() * 8 + 4) + 'px';
            p.style.height = (Math.random() * 14 + 8) + 'px';
            p.style.animationDelay = (Math.random() * 0.9) + 's';
            p.style.animationDuration = (Math.random() * 2 + 2.5) + 's';
            box.appendChild(p);
        }
        setTimeout(() => box.remove(), 5000);
    }

    function showToast(msg, type) {
        let container = document.querySelector('.messages-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'messages-container';
            document.body.appendChild(container);
        }
        const el = document.createElement('div');
        el.className = `alert alert-${type}`;
        el.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            ${msg}
            <button class="close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        container.appendChild(el);
        setTimeout(() => el.remove(), 4000);
    }

    function getCookie(name) {
        let v = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(c => {
                const t = c.trim();
                if (t.startsWith(name + '=')) v = decodeURIComponent(t.slice(name.length + 1));
            });
        }
        return v;
    }

    document.addEventListener('DOMContentLoaded', () => {
        init();
        const hist = document.getElementById('historyList');
        const caseIdFromPage = document.body.dataset.caseId
            || document.querySelector('[data-open-case]')?.dataset.caseId;
        if (hist && caseIdFromPage) loadCaseHistory(caseIdFromPage);
    });

    window.CaseOpening = { openCase, closeOverlay, loadCaseHistory };
})();
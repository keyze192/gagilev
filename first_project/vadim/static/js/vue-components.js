(function () {
    'use strict';

    function init() {
        if (typeof Vue === 'undefined') return;

        const { createApp, ref, computed } = Vue;

        document.querySelectorAll('[data-vue-balance]').forEach(el => {
            const initialBalance = parseFloat(el.dataset.balance) || 0;

            const app = createApp({
                setup() {
                    const balance = ref(initialBalance);

                    const formatted = computed(() => {
                        return Math.round(balance.value).toLocaleString('ru-RU');
                    });

                    window.addEventListener('balance-updated', (e) => {
                        console.log('Vue получил событие, balance =', e.detail.balance);
                        balance.value = e.detail.balance;
                    });

                    return { balance, formatted };
                },
                template: `
                    <i class="fas fa-coins"></i>
                    <span class="balance-amount" :data-rub-value="balance">{{ formatted }} ₽</span>
                `,
            });

            app.mount(el);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
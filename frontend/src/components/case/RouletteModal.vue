<template>
  <transition name="modal">
    <div v-if="visible" class="overlay" @click.self="close">
      <div class="modal-inner">
        <div v-if="stage === 'spinning'" class="roulette">
          <div class="roulette-mask">
            <div class="roulette-track" :style="trackStyle">
              <div
                v-for="(item, i) in items"
                :key="i"
                :class="['r-item', `r-${item.rarity_class}`]"
              >
                <i :class="['fas', item.icon]"></i>
                <span class="r-name">{{ item.name }}</span>
                <span class="r-price">{{ item.price }} ₽</span>
              </div>
            </div>
            <div class="pointer"></div>
            <div class="fade-left"></div>
            <div class="fade-right"></div>
          </div>
        </div>

        <!-- Победа -->
        <div v-else-if="stage === 'win'" class="win-card">
          <div class="win-title">🎉 Поздравляем!</div>
          <div :class="['win-icon', `r-${winner.rarity_class}`]">
            <i :class="['fas', winner.icon]"></i>
          </div>
          <h2 class="win-name">{{ winner.name }}</h2>
          <div class="win-price">{{ winner.price }} ₽</div>
          <span :class="['badge', `badge-${winner.rarity_class}`]">
            {{ winner.rarity_name }}
          </span>
          <p class="win-balance">Баланс: <span class="price">{{ newBalance }} ₽</span></p>
          <div class="win-actions">
            <button class="btn btn-ghost" @click="close">
              <i class="fas fa-times"></i> Закрыть
            </button>
            <button class="btn btn-primary" @click="reopen">
              <i class="fas fa-redo"></i> Ещё раз
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  visible: Boolean,
  allItems: { type: Array, default: () => [] },
  winner: { type: Object, default: null },
  newBalance: { type: [Number, String], default: 0 },
})
const emit = defineEmits(['close', 'reopen'])

const stage = ref('spinning')
const items = ref([])
const offset = ref(0)
const ITEM_W = 140 // ширина одного блока (120 + gap 20)
const WINNER_INDEX = 32

const trackStyle = computed(() => ({
  transform: `translateX(-${offset.value}px)`,
  transition: stage.value === 'spinning' ? 'transform 6s cubic-bezier(0.12, 0.8, 0.2, 1)' : 'none',
}))

watch(() => props.visible, async (v) => {
  if (v && props.winner) {
    stage.value = 'spinning'
    items.value = []
    offset.value = 0
    await nextTick()
    startRoulette()
  }
})

function startRoulette() {
  // Заполняем 40 слотов, победитель на позиции WINNER_INDEX
  const pool = props.allItems.length ? props.allItems : [props.winner]
  const arr = []
  for (let i = 0; i < 40; i++) {
    arr.push(i === WINNER_INDEX ? props.winner : pool[Math.floor(Math.random() * pool.length)])
  }
  items.value = arr

  nextTick(() => {
    // Центрируем рулетку
    const viewportCenter = window.innerWidth / 2
    const target = WINNER_INDEX * ITEM_W - viewportCenter + ITEM_W / 2
    const jitter = (Math.random() - 0.5) * ITEM_W * 0.5
    setTimeout(() => {
      offset.value = target + jitter
    }, 50)

    setTimeout(() => {
      stage.value = 'win'
    }, 6300)
  })
}

function close() { emit('close') }
function reopen() { emit('reopen') }
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 9000;
  background: rgba(2, 4, 8, 0.92);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.modal-inner {
  width: min(1200px, 96vw);
  animation: fadeIn 0.3s ease;
}


.roulette-mask {
  position: relative;
  height: 220px;
  background: linear-gradient(180deg, #060b14 0%, #0f1923 50%, #060b14 100%);
  border: 1px solid var(--glass-border-hover);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: inset 0 0 80px rgba(0, 0, 0, 0.8), 0 0 60px var(--primary-glow);
}
.roulette-track {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 0;
  height: 100%;
  will-change: transform;
  position: absolute;
  left: 50%;
}
.r-item {
  flex: 0 0 120px;
  height: 170px;
  background: rgba(20, 25, 40, 0.7);
  border-radius: 12px;
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
}
.r-item i { font-size: 40px; color: #fff; }
.r-name {
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
  line-height: 1.2;
  max-height: 28px;
  overflow: hidden;
}
.r-price { font-size: 12px; color: var(--gold); font-weight: 800; }

.r-common { border-color: rgba(148, 163, 184, 0.5); }
.r-rare { border-color: rgba(16, 185, 129, 0.7); box-shadow: 0 0 15px rgba(16, 185, 129, 0.3); }
.r-epic { border-color: rgba(168, 85, 247, 0.7); box-shadow: 0 0 15px rgba(168, 85, 247, 0.4); }
.r-legendary { border-color: rgba(251, 191, 36, 0.9); box-shadow: 0 0 20px rgba(251, 191, 36, 0.5); }
.r-ancient { border-color: rgba(239, 68, 68, 0.9); box-shadow: 0 0 25px rgba(239, 68, 68, 0.6); }

.pointer {
  position: absolute;
  top: 0; bottom: 0; left: 50%;
  width: 3px;
  transform: translateX(-50%);
  background: linear-gradient(180deg, transparent, var(--primary), transparent);
  box-shadow: 0 0 20px var(--primary), 0 0 40px var(--primary);
  z-index: 5;
  pointer-events: none;
}
.pointer::before, .pointer::after {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
}
.pointer::before { top: -2px; border-top: 16px solid var(--primary); }
.pointer::after { bottom: -2px; border-bottom: 16px solid var(--primary); }

.fade-left, .fade-right {
  position: absolute;
  top: 0; bottom: 0;
  width: 140px;
  pointer-events: none;
  z-index: 4;
}
.fade-left { left: 0; background: linear-gradient(90deg, #05070d, transparent); }
.fade-right { right: 0; background: linear-gradient(-90deg, #05070d, transparent); }


.win-card {
  background: var(--glass);
  border: 1px solid var(--glass-border-hover);
  border-radius: var(--radius-lg);
  padding: 48px 32px;
  max-width: 500px;
  margin: 0 auto;
  text-align: center;
  backdrop-filter: blur(20px);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.7), 0 0 80px var(--primary-glow);
  animation: fadeInUp 0.5s ease;
  position: relative;
}
.win-title { font-size: 14px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 24px; }
.win-icon {
  width: 160px; height: 160px;
  margin: 0 auto 24px;
  border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: 72px;
  color: #fff;
}
.win-icon.r-common { background: linear-gradient(135deg, #94a3b8, #64748b); }
.win-icon.r-rare { background: linear-gradient(135deg, #10b981, #047857); box-shadow: 0 0 60px rgba(16, 185, 129, 0.6); }
.win-icon.r-epic { background: linear-gradient(135deg, #a855f7, #7e22ce); box-shadow: 0 0 60px rgba(168, 85, 247, 0.6); }
.win-icon.r-legendary { background: linear-gradient(135deg, #fbbf24, #d97706); box-shadow: 0 0 80px rgba(251, 191, 36, 0.7); }
.win-icon.r-ancient { background: linear-gradient(135deg, #ef4444, #b91c1c); box-shadow: 0 0 90px rgba(239, 68, 68, 0.8); }
.win-name { font-size: 24px; font-weight: 800; margin-bottom: 12px; }
.win-price { font-size: 28px; color: var(--gold); font-weight: 900; margin-bottom: 12px; text-shadow: 0 0 20px var(--gold-glow); }
.win-balance { color: var(--text-muted); margin: 20px 0; }
.win-actions { display: flex; gap: 12px; justify-content: center; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.3s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
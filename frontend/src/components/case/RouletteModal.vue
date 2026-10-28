<template>
  <transition name="modal">
    <div v-if="visible" class="overlay" @click.self="close">
      <div class="modal-inner">
        
        <div v-if="stage === 'spinning'" class="multi-roulette" :class="{ single: winners.length === 1 }">
          <div v-for="(winner, index) in winners" :key="index" class="roulette-row">
            <div class="roulette-mask">
              <div class="roulette-track" :style="getTrackStyle(index)">
                <div v-for="(item, i) in itemsArray[index]" :key="i" :class="['r-item', `r-${item.rarity_class || 'common'}`]">
                  <img v-if="item.image_url" :src="item.image_url" class="r-img" alt="" />
                  <i v-else :class="['fas', item.icon || 'fa-cube']"></i>
                  <span class="r-name">{{ item.name }}</span>
                </div>
              </div>
              <div class="pointer"></div>
              <div class="fade-left"></div>
              <div class="fade-right"></div>
            </div>
          </div>
        </div>

        <div v-else-if="stage === 'win'" class="win-card" :class="{ 'multi': winners.length > 1 }">
          <div class="win-title">🎉 Поздравляем!</div>

          <template v-if="winners.length === 1">
            <div :class="['win-icon', `r-${winners[0].rarity_class || 'common'}`, { 'has-image': winners[0].image_url }]">
              <img v-if="winners[0].image_url" :src="winners[0].image_url" class="win-img" alt="" />
              <i v-else :class="['fas', winners[0].icon || 'fa-cube']"></i>
            </div>
            <h2 class="win-name">{{ winners[0].name }}</h2>
            <div class="win-price">{{ formatMoney(winners[0].price) }}</div>
            <span :class="['badge', `badge-${winners[0].rarity_class || 'common'}`]">
              {{ winners[0].rarity_name || 'Обычный' }}
            </span>
          </template>

          <div v-else class="multi-grid">
            <div v-for="(item, i) in winners" :key="i" :class="['multi-item', `r-${item.rarity_class || 'common'}`]">
              <img v-if="item.image_url" :src="item.image_url" alt="" />
              <i v-else :class="['fas', item.icon || 'fa-cube']"></i>
              <div class="multi-price">{{ formatMoney(item.price) }}</div>
            </div>
          </div>

          <p class="win-balance">
            Баланс: <span class="price">{{ formatMoney(newBalance) }}</span>
          </p>

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
  winners: { type: Array, default: () => [] },
  newBalance: { type: [Number, String], default: 0 },
})

const emit = defineEmits(['close', 'reopen'])

const stage = ref('spinning')
const itemsArray = ref([]) 
const offsets = ref([]) 

const ITEM_W = 140
const WINNER_INDEX = 32
const TRACK_LENGTH = 40

const formatMoney = (n) => new Intl.NumberFormat('ru-RU').format(Math.round(Number(n) || 0)) + ' ₽'

watch(() => props.visible, async (v) => {
  if (!v || !props.winners.length) return
  stage.value = 'spinning'
  itemsArray.value = []
  offsets.value = Array(props.winners.length).fill(0)
  await nextTick()
  startMultiRoulette()
})

function getTrackStyle(index) {
  const isSpinning = stage.value === 'spinning'

  const duration = 5 + index * 0.3
  return {
    transform: `translateX(-${offsets.value[index]}px)`,
    transition: isSpinning ? `transform ${duration}s cubic-bezier(0.12, 0.8, 0.2, 1)` : 'none',
  }
}

function startMultiRoulette() {
  const pool = props.allItems.length ? props.allItems : props.winners

  props.winners.forEach((winnerItem, rowIndex) => {
    const arr = []
    for (let i = 0; i < TRACK_LENGTH; i++) {
      arr.push(i === WINNER_INDEX ? winnerItem : pool[Math.floor(Math.random() * pool.length)])
    }
    itemsArray.value.push(arr)
  })

  nextTick(() => {
    props.winners.forEach((_, rowIndex) => {
      const jitter = (Math.random() - 0.5) * 60
      const target = WINNER_INDEX * ITEM_W + ITEM_W / 2 + jitter
      
      setTimeout(() => {
        offsets.value[rowIndex] = target
      }, 50 + rowIndex * 100)
    })

    // Максимальное время анимации + запас
    const maxDuration = (5 + props.winners.length * 0.3) * 1000 + 500
    setTimeout(() => { stage.value = 'win' }, maxDuration)
  })
}

function close() { emit('close') }
function reopen() { emit('reopen') }
</script>

<style scoped>
.overlay { position: fixed; inset: 0; z-index: 9000; background: rgba(2, 4, 8, 0.92); backdrop-filter: blur(12px); display: flex; align-items: center; justify-content: center; padding: 20px; overflow-y: auto; }
.modal-inner { width: min(1200px, 96vw); animation: fadeIn 0.3s ease; margin: auto; }

.multi-roulette {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.multi-roulette.single .roulette-mask { height: 220px; }
.multi-roulette:not(.single) .roulette-mask { height: 90px; }

.roulette-mask { position: relative; width: 100%; background: linear-gradient(180deg, #060b14 0%, #0f1923 50%, #060b14 100%); border: 1px solid var(--glass-border-hover); border-radius: var(--radius); overflow: hidden; box-shadow: inset 0 0 80px rgba(0, 0, 0, 0.8), 0 0 60px var(--primary-glow); }
.roulette-track { display: flex; align-items: center; gap: 20px; padding: 10px 0; height: 100%; will-change: transform; position: absolute; left: 50%; }

.r-item { flex: 0 0 120px; height: 100%; background: rgba(20, 25, 40, 0.7); border-radius: 12px; border: 2px solid transparent; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; padding: 6px; }
.r-item i { font-size: 30px; color: #fff; }
.r-img { max-width: 95%; max-height: 50px; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5)); }
.r-name { font-size: 10px; color: var(--text-muted); text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }

.r-common { border-color: rgba(148, 163, 184, 0.5); }
.r-rare { border-color: rgba(16, 185, 129, 0.7); box-shadow: 0 0 15px rgba(16, 185, 129, 0.3); }
.r-epic { border-color: rgba(168, 85, 247, 0.7); box-shadow: 0 0 15px rgba(168, 85, 247, 0.4); }
.r-legendary { border-color: rgba(251, 191, 36, 0.9); box-shadow: 0 0 20px rgba(251, 191, 36, 0.5); }
.r-ancient { border-color: rgba(239, 68, 68, 0.9); box-shadow: 0 0 25px rgba(239, 68, 68, 0.6); }

.pointer { position: absolute; top: 0; bottom: 0; left: 50%; width: 3px; transform: translateX(-50%); background: linear-gradient(180deg, transparent, var(--primary), transparent); box-shadow: 0 0 20px var(--primary), 0 0 40px var(--primary); z-index: 5; pointer-events: none; }
.pointer::before, .pointer::after { content: ''; position: absolute; left: 50%; transform: translateX(-50%); border-left: 10px solid transparent; border-right: 10px solid transparent; }
.pointer::before { top: -2px; border-top: 16px solid var(--primary); }
.pointer::after { bottom: -2px; border-bottom: 16px solid var(--primary); }

.fade-left, .fade-right { position: absolute; top: 0; bottom: 0; width: 140px; pointer-events: none; z-index: 4; }
.fade-left { left: 0; background: linear-gradient(90deg, #05070d, transparent); }
.fade-right { right: 0; background: linear-gradient(-90deg, #05070d, transparent); }

.win-card { background: var(--glass); border: 1px solid var(--glass-border-hover); border-radius: var(--radius-lg); padding: 40px 32px; max-width: 500px; margin: 0 auto; text-align: center; backdrop-filter: blur(20px); box-shadow: 0 24px 80px rgba(0, 0, 0, 0.7), 0 0 80px var(--primary-glow); animation: fadeInUp 0.5s ease; position: relative; }
.win-card.multi { max-width: 800px; }
.win-title { font-size: 14px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 24px; }

.win-icon { width: 160px; height: 160px; margin: 0 auto 24px; border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 72px; color: #fff; transition: var(--transition); }
.win-icon.has-image { background: rgba(0, 0, 0, 0.2) !important; box-shadow: 0 0 60px rgba(255, 255, 255, 0.1) !important; border: 1px solid var(--glass-border); }
.win-img { max-width: 140px; max-height: 110px; object-fit: contain; filter: drop-shadow(0 10px 20px rgba(0,0,0,0.6)); }
.win-icon.r-common { background: linear-gradient(135deg, #94a3b8, #64748b); }
.win-icon.r-rare { background: linear-gradient(135deg, #10b981, #047857); box-shadow: 0 0 60px rgba(16, 185, 129, 0.6); }
.win-icon.r-epic { background: linear-gradient(135deg, #a855f7, #7e22ce); box-shadow: 0 0 60px rgba(168, 85, 247, 0.6); }
.win-icon.r-legendary { background: linear-gradient(135deg, #fbbf24, #d97706); box-shadow: 0 0 80px rgba(251, 191, 36, 0.7); }
.win-icon.r-ancient { background: linear-gradient(135deg, #ef4444, #b91c1c); box-shadow: 0 0 90px rgba(239, 68, 68, 0.8); }

.win-name { font-size: 24px; font-weight: 800; margin-bottom: 12px; }
.win-price { font-size: 28px; color: var(--gold); font-weight: 900; margin-bottom: 12px; text-shadow: 0 0 20px var(--gold-glow); }
.win-balance { color: var(--text-muted); margin: 20px 0; }
.win-actions { display: flex; gap: 12px; justify-content: center; }

.multi-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 12px; margin-bottom: 24px; }
.multi-item { background: rgba(0,0,0,0.3); border: 2px solid transparent; border-radius: 12px; padding: 12px; display: flex; flex-direction: column; align-items: center; gap: 8px; }
.multi-item img { height: 60px; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5)); }
.multi-item i { font-size: 32px; color: #fff; }
.multi-price { font-size: 13px; color: var(--gold); font-weight: 800; }
.multi-item.r-common { border-color: rgba(148, 163, 184, 0.5); }
.multi-item.r-rare { border-color: rgba(16, 185, 129, 0.7); }
.multi-item.r-epic { border-color: rgba(168, 85, 247, 0.7); }
.multi-item.r-legendary { border-color: rgba(251, 191, 36, 0.9); }
.multi-item.r-ancient { border-color: rgba(239, 68, 68, 0.9); }

.modal-enter-active, .modal-leave-active { transition: opacity 0.3s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
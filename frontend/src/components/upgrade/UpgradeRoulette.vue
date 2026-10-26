<template>
  <transition name="modal">
    <div v-if="visible" class="overlay">
      <div class="modal-inner">
        
        <div v-if="stage === 'spinning'" class="roulette-wrap">
          <h2 class="spin-title">Крутим удачу...</h2>
          <div class="roulette">
            <div class="track" :style="trackStyle">
              <div v-for="(item, i) in items" :key="i" :class="['r-item', `r-${item.rarity}`]">
                <i :class="['fas', item.icon]"></i>
              </div>
            </div>
            <div class="pointer"></div>
            <div class="fade-left"></div>
            <div class="fade-right"></div>
          </div>
        </div>

        <div v-else-if="stage === 'result'" class="result-card">
          <div :class="['result-icon', isWin ? 'win' : 'lose']">
            <i :class="['fas', isWin ? 'fa-trophy' : 'fa-times']"></i>
          </div>
          <h2 :style="{ color: isWin ? 'var(--success)' : 'var(--danger)' }">
            {{ isWin ? 'Апгрейд успешен!' : 'Не повезло!' }}
          </h2>
          <p class="result-desc">
            {{ isWin ? 'Вы получили предмет:' : 'Предмет сгорел.' }}
          </p>
          <div v-if="isWin" class="win-item">
            <span class="price">{{ winnerItem.name }}</span>
            <span class="price" style="font-size: 20px;">{{ winnerItem.price }} ₽</span>
          </div>
          <button class="btn btn-primary mt-4" @click="$emit('close')">Забрать</button>
        </div>

      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  visible: Boolean,
  isWin: Boolean,
  targetItem: Object,
  sourceItem: Object
})
const emit = defineEmits(['close'])

const stage = ref('spinning')
const items = ref([])
const offset = ref(0)
const ITEM_W = 120
const WINNER_INDEX = 35

const winnerItem = computed(() => props.isWin ? props.targetItem : props.sourceItem)

const trackStyle = computed(() => ({
  transform: `translateX(-${offset.value}px)`,
  transition: stage.value === 'spinning' ? 'transform 5s cubic-bezier(0.1, 0.8, 0.2, 1)' : 'none',
}))

watch(() => props.visible, async (v) => {
  if (v) {
    stage.value = 'spinning'
    items.value = []
    offset.value = 0
    await nextTick()
    startRoulette()
  }
})

function startRoulette() {

  const pool = [props.targetItem, props.sourceItem]
  const arr = []
  for (let i = 0; i < 40; i++) {

    arr.push(i === WINNER_INDEX ? winnerItem.value : pool[Math.floor(Math.random() * pool.length)])
  }
  items.value = arr

  nextTick(() => {
    const viewportCenter = window.innerWidth / 2
    const target = WINNER_INDEX * ITEM_W - viewportCenter + ITEM_W / 2
    const jitter = (Math.random() - 0.5) * ITEM_W * 0.4
    
    setTimeout(() => {
      offset.value = target + jitter
    }, 50)

    setTimeout(() => {
      stage.value = 'result'
    }, 5300)
  })
}
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0; z-index: 9000;
  background: rgba(2, 4, 8, 0.92); backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.modal-inner { width: min(1000px, 96vw); text-align: center; animation: fadeIn 0.3s ease; }
.spin-title { font-size: 24px; margin-bottom: 20px; font-weight: 800; }
.roulette {
  position: relative; height: 180px;
  background: linear-gradient(180deg, #060b14, #0f1923);
  border: 1px solid var(--glass-border-hover);
  border-radius: var(--radius); overflow: hidden;
  box-shadow: inset 0 0 80px rgba(0,0,0,0.8), 0 0 60px var(--primary-glow);
}
.track { display: flex; align-items: center; gap: 10px; height: 100%; position: absolute; left: 50%; will-change: transform; }
.r-item {
  flex: 0 0 110px; height: 140px;
  background: rgba(20,25,40,0.7); border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 40px; border: 2px solid transparent;
}
.r-item.r-common { border-color: rgba(148,163,184,0.5); }
.r-item.r-rare { border-color: rgba(16,185,129,0.7); box-shadow: 0 0 15px rgba(16,185,129,0.3); }
.r-item.r-epic { border-color: rgba(168,85,247,0.7); box-shadow: 0 0 15px rgba(168,85,247,0.4); }
.r-item.r-legendary { border-color: rgba(251,191,36,0.9); box-shadow: 0 0 20px rgba(251,191,36,0.5); }
.r-item.r-ancient { border-color: rgba(239,68,68,0.9); box-shadow: 0 0 25px rgba(239,68,68,0.6); }
.r-item i { color: #fff; }

.pointer {
  position: absolute; top: 0; bottom: 0; left: 50%; width: 3px;
  transform: translateX(-50%); background: linear-gradient(180deg, transparent, var(--primary), transparent);
  box-shadow: 0 0 20px var(--primary), 0 0 40px var(--primary); z-index: 5; pointer-events: none;
}
.pointer::before, .pointer::after {
  content: ''; position: absolute; left: 50%; transform: translateX(-50%);
  border-left: 10px solid transparent; border-right: 10px solid transparent;
}
.pointer::before { top: -2px; border-top: 16px solid var(--primary); }
.pointer::after { bottom: -2px; border-bottom: 16px solid var(--primary); }
.fade-left, .fade-right { position: absolute; top: 0; bottom: 0; width: 140px; pointer-events: none; z-index: 4; }
.fade-left { left: 0; background: linear-gradient(90deg, #05070d, transparent); }
.fade-right { right: 0; background: linear-gradient(-90deg, #05070d, transparent); }

.result-card { background: var(--glass); border: 1px solid var(--glass-border-hover); border-radius: var(--radius-lg); padding: 40px; max-width: 400px; margin: 0 auto; backdrop-filter: blur(20px); animation: fadeInUp 0.4s ease; }
.result-icon { width: 100px; height: 100px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 44px; color: #fff; }
.result-icon.win { background: linear-gradient(135deg, var(--success), #047857); box-shadow: 0 0 50px rgba(16,185,129,0.5); }
.result-icon.lose { background: linear-gradient(135deg, var(--danger), #b91c1c); box-shadow: 0 0 50px rgba(239,68,68,0.5); }
.result-desc { color: var(--text-muted); margin-bottom: 20px; font-size: 15px; }
.win-item { background: rgba(0,0,0,0.3); padding: 15px; border-radius: 12px; border: 1px solid var(--glass-border); }
.win-item .price { display: block; color: var(--gold); font-weight: 800; margin-bottom: 5px; text-shadow: 0 0 20px var(--gold-glow); }

.modal-enter-active, .modal-leave-active { transition: opacity 0.3s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
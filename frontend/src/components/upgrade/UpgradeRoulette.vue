<template>
  <transition name="modal">
    <div v-if="visible" class="overlay">
      <div class="modal-inner">

        <div v-if="stage === 'spinning'" class="spin-wrap">
          <h2 class="spin-title">Крутим удачу...</h2>

          <div class="wheel-container">
            <div class="pointer"></div>
            <div class="wheel" :style="wheelStyle">

              <div class="wheel-segments" :style="segmentStyle"></div>
              <div class="wheel-center">
                <strong>{{ chance }}%</strong>
                <span>Шанс</span>
              </div>
            </div>
          </div>

          <div class="legend">
            <span class="legend-item win">
              <span class="dot"></span> Победа ({{ chance }}%)
            </span>
            <span class="legend-item lose">
              <span class="dot"></span> Проигрыш ({{ (100 - chance).toFixed(1) }}%)
            </span>
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
          <div v-if="isWin && targetItem" class="win-item">
            <span class="win-name">{{ targetItem.name }}</span>
            <span class="price">{{ formatMoney(targetItem.price) }}</span>
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
  chance: { type: Number, default: 0 },  
  targetItem: Object,
  sourceItem: Object,
})
defineEmits(['close'])

const stage = ref('spinning')
const rotation = ref(0)
const spinning = ref(false)

const formatMoney = (n) => new Intl.NumberFormat('ru-RU').format(Math.round(Number(n) || 0)) + ' ₽'


const winAngle = computed(() => Math.max(0.5, Math.min(props.chance, 90)) * 3.6)


const segmentStyle = computed(() => ({
  background: `conic-gradient(
    from 0deg,
    var(--success) 0deg ${winAngle.value}deg,
    var(--danger) ${winAngle.value}deg 360deg
  )`,
}))


const wheelStyle = computed(() => ({
  transform: `rotate(${rotation.value}deg)`,
  transition: spinning.value
    ? 'transform 5s cubic-bezier(0.15, 0.85, 0.2, 1)'
    : 'none',
}))

watch(() => props.visible, async (v) => {
  if (!v) return
  // Сброс перед новым запуском
  spinning.value = false
  stage.value = 'spinning'
  rotation.value = 0
  await nextTick()
  

  setTimeout(() => {
    spinning.value = true
    startSpin()
  }, 50)
})

function startSpin() {

  const w = winAngle.value
  let A
  
  if (props.isWin) {

    A = w * (0.15 + Math.random() * 0.7)
  } else {

    const lose = 360 - w
    A = w + lose * (0.05 + Math.random() * 0.9)
  }
  

  const spins = 5 + Math.floor(Math.random() * 2)
  rotation.value = spins * 360 + (360 - A)


  setTimeout(() => { 
    stage.value = 'result' 
  }, 5200)
}
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0; z-index: 9000;
  background: rgba(2, 4, 8, 0.92); backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.modal-inner { width: min(600px, 96vw); text-align: center; animation: fadeIn 0.3s ease; }
.spin-title { font-size: 24px; margin-bottom: 30px; font-weight: 800; }


.wheel-container {
  position: relative;
  width: 320px; height: 320px;
  margin: 0 auto 30px;
}

.pointer {
  position: absolute;
  top: -14px; left: 50%;
  transform: translateX(-50%);
  width: 0; height: 0;
  border-left: 14px solid transparent;
  border-right: 14px solid transparent;
  border-top: 30px solid var(--gold);
  filter: drop-shadow(0 0 14px var(--gold-glow));
  z-index: 3;
}

.wheel {
  width: 100%; height: 100%;
  border-radius: 50%;
  position: relative;
  box-shadow: 0 0 60px var(--primary-glow), inset 0 0 30px rgba(0,0,0,0.5);
  border: 6px solid rgba(255,255,255,0.08);
  overflow: hidden;
}

.wheel-segments { position: absolute; inset: 0; border-radius: 50%; }

.wheel-center {
  position: absolute;
  top: 50%; left: 50%;
  width: 130px; height: 130px;
  margin: -65px 0 0 -65px;
  border-radius: 50%;
  background: var(--bg-elevated);
  border: 3px solid var(--primary);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  z-index: 2;
  box-shadow: 0 0 30px var(--primary-glow);
}
.wheel-center strong { font-size: 30px; font-weight: 900; color: var(--gold); }
.wheel-center span { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; }

.legend {
  display: flex; gap: 24px; justify-content: center;
  margin-top: 20px; font-size: 13px;
}
.legend-item { display: flex; align-items: center; gap: 8px; color: var(--text-muted); }
.legend-item .dot { width: 12px; height: 12px; border-radius: 50%; }
.legend-item.win .dot { background: var(--success); box-shadow: 0 0 10px var(--success); }
.legend-item.lose .dot { background: var(--danger); box-shadow: 0 0 10px var(--danger); }


.result-card {
  background: var(--glass); border: 1px solid var(--glass-border-hover);
  border-radius: var(--radius-lg); padding: 40px; max-width: 400px;
  margin: 0 auto; backdrop-filter: blur(20px);
  animation: fadeInUp 0.4s ease;
}
.result-icon {
  width: 100px; height: 100px; border-radius: 50%;
  margin: 0 auto 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: 44px; color: #fff;
}
.result-icon.win { background: linear-gradient(135deg, var(--success), #047857); box-shadow: 0 0 50px rgba(16,185,129,0.5); }
.result-icon.lose { background: linear-gradient(135deg, var(--danger), #b91c1c); box-shadow: 0 0 50px rgba(239,68,68,0.5); }
.result-desc { color: var(--text-muted); margin-bottom: 20px; font-size: 15px; }
.win-item {
  background: rgba(0,0,0,0.3); padding: 15px; border-radius: 12px;
  border: 1px solid var(--glass-border);
  display: flex; flex-direction: column; gap: 6px;
}
.win-name { color: var(--text); font-weight: 800; font-size: 16px; }
.win-item .price { font-size: 22px; color: var(--gold); font-weight: 900; text-shadow: 0 0 20px var(--gold-glow); }

.modal-enter-active, .modal-leave-active { transition: opacity 0.3s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
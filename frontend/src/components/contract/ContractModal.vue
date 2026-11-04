<template>
  <transition name="modal">
    <div v-if="visible" class="overlay" @click.self="close">
      <div class="modal-inner">
        <div class="win-card">
          <div class="win-title">🎉 Контракт выполнен!</div>
          
          <div :class="['win-icon', `r-${wonItem.rarity_class || 'common'}`, { 'has-image': wonItem.image_url }]">
            <img v-if="wonItem.image_url" :src="wonItem.image_url" class="win-img" alt="" />
            <i v-else :class="['fas', wonItem.icon || 'fa-cube']"></i>
          </div>
          
          <h2 class="win-name">{{ wonItem.name }}</h2>
          <div class="win-price">{{ formatMoney(wonItem.price) }}</div>
          <span :class="['badge', `badge-${wonItem.rarity_class || 'common'}`]">
            {{ wonItem.rarity_name || 'Обычный' }}
          </span>

          <div class="win-actions">
            <button class="btn btn-primary" @click="close">
              <i class="fas fa-check"></i> Забрать
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  visible: Boolean,
  wonItem: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['close'])

const formatMoney = (n) => new Intl.NumberFormat('ru-RU').format(Math.round(Number(n) || 0)) + ' ₽'
const close = () => emit('close')
</script>

<style scoped>
.overlay { position: fixed; inset: 0; z-index: 9000; background: rgba(2, 4, 8, 0.92); backdrop-filter: blur(12px); display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-inner { width: min(500px, 96vw); animation: fadeIn 0.3s ease; }
.win-card { background: var(--glass); border: 1px solid var(--glass-border-hover); border-radius: var(--radius-lg); padding: 40px 32px; text-align: center; backdrop-filter: blur(20px); box-shadow: 0 24px 80px rgba(0, 0, 0, 0.7), 0 0 80px var(--primary-glow); animation: fadeInUp 0.5s ease; }
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
.win-actions { display: flex; gap: 12px; justify-content: center; margin-top: 24px; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.3s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
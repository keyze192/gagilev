<template>
  <div class="case-card">
    <div class="glow"></div>
    <div class="case-img">
      <img v-if="caseData.image_url" :src="caseData.image_url" :alt="caseData.name" />
      <i v-else class="fas fa-box"></i>
    </div>
    <h3 class="case-name">{{ caseData.name }}</h3>
    <div class="price-row">
      <span class="label">Цена</span>
      <span class="price">{{ formatMoney(caseData.price) }}</span>
    </div>
    <router-link :to="`/case/${caseData.id}`" class="btn btn-primary w-full">
      <i class="fas fa-gift"></i> Открыть
    </router-link>
  </div>
</template>

<script setup>
defineProps({ caseData: { type: Object, required: true } })

const formatMoney = (n) => new Intl.NumberFormat('ru-RU').format(Math.round(n)) + ' ₽'
</script>

<style scoped>
.case-card {
  position: relative;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  padding: 20px;
  backdrop-filter: blur(20px);
  transition: var(--transition);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.case-card:hover {
  transform: translateY(-6px);
  border-color: var(--glass-border-hover);
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.6), 0 0 40px var(--primary-glow);
}
.glow {
  position: absolute;
  top: -60px; left: 50%;
  transform: translateX(-50%);
  width: 240px; height: 240px;
  background: radial-gradient(circle, var(--primary-glow) 0%, transparent 70%);
  opacity: 0;
  transition: var(--transition);
  pointer-events: none;
}
.case-card:hover .glow { opacity: 1; }
.case-img {
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
  color: var(--primary-light);
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
  transition: var(--transition);
}
.case-card:hover .case-img { transform: scale(1.06); }
.case-img img {
  max-height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 12px 24px var(--primary-glow));
}
.case-name {
  font-size: 16px;
  font-weight: 800;
  text-align: center;
  margin-bottom: 16px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}
.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: rgba(251, 191, 36, 0.08);
  border: 1px solid rgba(251, 191, 36, 0.2);
  border-radius: 10px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}
.label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
}
.price {
  font-size: 17px;
  font-weight: 900;
  color: var(--gold);
  text-shadow: 0 0 16px var(--gold-glow);
}
</style>
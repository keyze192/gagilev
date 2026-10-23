<template>
  <div class="page">
    <div class="container">
      <router-link to="/" class="back-btn btn btn-ghost">
        <i class="fas fa-arrow-left"></i> Назад
      </router-link>

      <div v-if="loading" class="loading-center">
        <div class="loader loader-lg"></div>
        <span>Загрузка...</span>
      </div>

      <div v-else-if="!caseData" class="empty">
        <i class="fas fa-box-open"></i>
        <h3>Кейс не найден</h3>
      </div>

      <template v-else>
        <!-- Hero -->
        <div class="hero">
          <div class="hero-glow"></div>
          <div class="hero-content">
            <div class="case-image">
              <img v-if="caseData.image_url" :src="caseData.image_url" :alt="caseData.name" />
              <i v-else class="fas fa-box"></i>
            </div>
            <div class="case-info">
              <h1 class="case-title gradient-text">{{ caseData.name }}</h1>
              <div class="price-badge">
                <i class="fas fa-tag"></i> {{ formatMoney(caseData.price) }}
              </div>
              <p class="description">{{ caseData.description || 'Откройте кейс и получите скин CS:GO!' }}</p>

              <div v-if="userStore.isAuth" class="balance-row">
                <i class="fas fa-wallet"></i>
                <span>Ваш баланс</span>
                <strong class="price">{{ formatMoney(userStore.balance) }}</strong>
              </div>

              <button
                v-if="userStore.isAuth"
                class="open-btn btn btn-primary btn-lg"
                :disabled="opening"
                @click="handleOpen"
              >
                <template v-if="opening">
                  <div class="loader" style="width: 20px; height: 20px;"></div>
                  Открываем...
                </template>
                <template v-else>
                  <i class="fas fa-gift"></i> Открыть за {{ formatMoney(caseData.price) }}
                </template>
              </button>

              <a v-else href="/steam/login/" class="open-btn btn btn-primary btn-lg">
                <i class="fab fa-steam"></i> Войти через Steam
              </a>
            </div>
          </div>
        </div>

        <!-- Содержимое -->
        <div class="mt-4">
          <h2 class="section-title">Содержимое <span class="gradient">кейса</span></h2>
          <div class="chances-grid">
            <div
              v-for="c in chances"
              :key="c.id"
              :class="['chance-card', `r-${rarityClass(c.item_details?.rarity || c.item?.rarity || 'common')}`]"
            >
              <div class="chance-head">
                <i :class="['fas', getItemIcon(c.item_name || c.item_details?.name)]"></i>
                <span class="chance-value">{{ c.chance }}%</span>
              </div>
              <div class="chance-name">{{ c.item_name || c.item_details?.name || 'Предмет' }}</div>
            </div>
          </div>
        </div>

        <!-- История -->
        <div class="mt-4">
          <h2 class="section-title">Последние <span class="gradient">открытия</span></h2>
          <div v-if="historyLoading" class="loading-center">
            <div class="loader"></div>
          </div>
          <div v-else-if="history.length === 0" class="empty-history">
            Пока нет открытий этого кейса
          </div>
          <div v-else class="history-list">
            <div
              v-for="(h, i) in history"
              :key="i"
              :class="['history-item', `r-${h.rarity}`]"
            >
              <div class="h-user"><i class="fas fa-user-circle"></i> {{ h.username }}</div>
              <div class="h-item">{{ h.item_name }}</div>
              <div class="h-price price">{{ h.item_price }} ₽</div>
              <div class="h-time">{{ h.time_ago }}</div>
            </div>
          </div>
        </div>
      </template>

      <RouletteModal
        :visible="modalVisible"
        :all-items="wonData?.all_items || []"
        :winner="wonData?.item || null"
        :new-balance="wonData?.new_balance || 0"
        @close="modalVisible = false"
        @reopen="handleOpen"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import RouletteModal from '../components/case/RouletteModal.vue'
import { getCase, getCaseChances, openCase, getCaseHistory, getItemIcon, rarityClass } from '../api'
import { useUserStore } from '../stores/user'
import { useToastStore } from '../stores/toast'

const route = useRoute()
const userStore = useUserStore()
const toast = useToastStore()

const caseData = ref(null)
const chances = ref([])
const history = ref([])
const loading = ref(true)
const historyLoading = ref(false)
const opening = ref(false)
const modalVisible = ref(false)
const wonData = ref(null)

const formatMoney = (n) => new Intl.NumberFormat('ru-RU').format(Math.round(n)) + ' ₽'

async function loadHistory() {
  if (!route.params.id) return
  historyLoading.value = true
  try {
    const data = await getCaseHistory(route.params.id)
    history.value = data.history || []
  } catch (e) { console.error(e) }
  finally { historyLoading.value = false }
}

async function handleOpen() {
  if (opening.value || !userStore.isAuth) return
  if (userStore.balance < caseData.value.price) {
    toast.error('Недостаточно средств')
    return
  }

  opening.value = true
  try {
    const data = await openCase(caseData.value.id)
    if (!data.success) {
      if (data.need_auth) {
        toast.error('Войдите через Steam')
        setTimeout(() => window.location.href = '/steam/login/', 1000)
      } else {
        toast.error(data.error || 'Ошибка открытия')
      }
      return
    }
    wonData.value = data
    modalVisible.value = true
    userStore.setBalance(data.new_balance)
    loadHistory()
  } catch (e) {
    console.error(e)
    toast.error('Ошибка сети')
  } finally {
    opening.value = false
  }
}

onMounted(async () => {
  try {
    caseData.value = await getCase(route.params.id)
    chances.value = await getCaseChances(route.params.id)
    loadHistory()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.back-btn { margin-bottom: 24px; }

.hero {
  position: relative;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 40px;
  backdrop-filter: blur(20px);
  overflow: hidden;
  margin-bottom: 40px;
}
.hero-glow {
  position: absolute;
  top: -150px; right: -150px;
  width: 500px; height: 500px;
  background: radial-gradient(circle, var(--primary-glow) 0%, transparent 70%);
  pointer-events: none;
  animation: float 8s ease-in-out infinite;
}
.hero-content {
  display: flex;
  gap: 40px;
  align-items: center;
  position: relative;
  z-index: 1;
}
.case-image {
  flex-shrink: 0;
  width: 200px; height: 200px;
  border-radius: var(--radius);
  background: radial-gradient(circle, var(--primary-glow) 0%, transparent 70%);
  display: flex; align-items: center; justify-content: center;
  font-size: 90px;
  color: var(--primary-light);
}
.case-image img { max-height: 100%; object-fit: contain; filter: drop-shadow(0 20px 40px var(--primary-glow)); }
.case-info { flex: 1; }
.gradient-text {
  font-size: clamp(28px, 4vw, 42px);
  font-weight: 900;
  background: linear-gradient(135deg, #fff 0%, var(--primary-light) 60%, var(--accent-light) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 16px;
  line-height: 1.15;
}
.price-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 18px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.15), rgba(251, 191, 36, 0.05));
  border: 1px solid rgba(251, 191, 36, 0.4);
  color: var(--gold);
  font-weight: 800;
  font-size: 16px;
  margin-bottom: 16px;
}
.description {
  color: var(--text-muted);
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 24px;
}
.balance-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-radius: 14px;
  background: rgba(251, 191, 36, 0.06);
  border: 1px solid rgba(251, 191, 36, 0.2);
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--text-muted);
}
.balance-row i { color: var(--gold); }
.balance-row strong { margin-left: auto; font-size: 20px; }
.open-btn { width: 100%; }

.chances-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}
.chance-card {
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 14px;
  transition: var(--transition);
}
.chance-card:hover { transform: translateY(-2px); }
.chance-card.r-common    { border-color: rgba(148, 163, 184, 0.35); }
.chance-card.r-rare      { border-color: rgba(16, 185, 129, 0.45); }
.chance-card.r-epic      { border-color: rgba(168, 85, 247, 0.45); }
.chance-card.r-legendary { border-color: rgba(251, 191, 36, 0.55); }
.chance-card.r-ancient   { border-color: rgba(239, 68, 68, 0.65); }
.chance-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.chance-head i { font-size: 20px; color: var(--text-muted); }
.chance-value { font-weight: 900; color: var(--primary-light); font-size: 14px; }
.chance-name { font-size: 13px; font-weight: 700; }

.history-list { display: flex; flex-direction: column; gap: 8px; }
.history-item {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr;
  gap: 16px;
  align-items: center;
  padding: 12px 18px;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  font-size: 14px;
  transition: var(--transition);
}
.history-item:hover { border-color: var(--glass-border-hover); transform: translateX(4px); }
.history-item.r-legendary { border-left: 3px solid var(--r-legendary); }
.history-item.r-ancient { border-left: 3px solid var(--r-ancient); }
.history-item.r-epic { border-left: 3px solid var(--r-epic); }
.history-item.r-rare { border-left: 3px solid var(--r-rare); }
.h-user { color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
.h-item { font-weight: 700; }
.h-time { color: var(--text-dim); font-size: 12px; text-align: right; }
.empty-history { padding: 40px; text-align: center; color: var(--text-muted); }
.empty { text-align: center; padding: 80px 20px; color: var(--text-muted); }
.empty i { font-size: 56px; color: var(--primary); opacity: 0.5; margin-bottom: 16px; }

@media (max-width: 768px) {
  .hero-content { flex-direction: column; text-align: center; }
  .history-item { grid-template-columns: 1fr 1fr; }
}
</style>
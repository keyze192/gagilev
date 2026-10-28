<template>
  <div class="page">
    <div class="container">
      <h1 class="title">Апгрейд <span class="gradient">Предметов</span></h1>

      <div class="upgrade-layout">

        <div class="glass-card inventory-panel">
          <h3 class="panel-title"><i class="fas fa-box"></i> Мой инвентарь</h3>
          <div v-if="inventory.length === 0" class="empty-msg">Инвентарь пуст</div>
          <div v-else class="items-grid">
            <div 
              v-for="inv in inventory" 
              :key="inv.id" 
              :class="['item-card', `r-${itemRarity(inv)}`, { active: sourceItem?.id === inv.id }]"
              @click="sourceItem = inv"
            >
              <div v-if="inv.quantity > 1" class="qty">x{{ inv.quantity }}</div>
              
              <div class="item-img-wrap">
                <img v-if="inv.item_details?.image_url" :src="inv.item_details.image_url" alt="" />
                <i v-else :class="['fas', itemIcon(inv)]"></i>
              </div>

              <span class="name">{{ inv.item_details?.name }}</span>
              <span class="price">{{ formatMoney(inv.item_details?.price) }}</span>
            </div>
          </div>
        </div>


        <div class="center-panel">
          <div class="chance-circle">
            <svg viewBox="0 0 100 100" class="circle-svg">
              <circle cx="50" cy="50" r="45" class="circle-bg"></circle>
              <circle cx="50" cy="50" r="45" class="circle-fill" :style="circleStyle"></circle>
            </svg>
            <div class="chance-text">
              <strong>{{ chance }}%</strong>
              <span>Шанс</span>
            </div>
          </div>

          <button class="btn btn-primary btn-lg upgrade-btn" :disabled="!canUpgrade || upgrading" @click="handleUpgrade">
            <div v-if="upgrading" class="loader"></div>
            <i v-else class="fas fa-arrow-up"></i>
            Апгрейд
          </button>
        </div>

  
        <div class="glass-card target-panel">
          <h3 class="panel-title"><i class="fas fa-crosshairs"></i> Желаемый предмет</h3>
          
          <div class="filters">
            <input v-model="searchQuery" class="input search-input" placeholder="Поиск по названию..." />
            <div class="filter-row">
              <select v-model="filterRarity" class="input select">
                <option value="all">Все редкости</option>
                <option value="common">Обычные</option>
                <option value="rare">Редкие</option>
                <option value="epic">Эпические</option>
                <option value="legendary">Легендарные</option>
                <option value="ancient">Древние</option>
              </select>
              <select v-model="sortBy" class="input select">
                <option value="price_asc">Цена ↑</option>
                <option value="price_desc">Цена ↓</option>
                <option value="name">По названию</option>
              </select>
            </div>
          </div>

          <div v-if="filteredTargets.length === 0" class="empty-msg">Ничего не найдено</div>
          <div v-else class="items-grid">
            <div 
              v-for="item in filteredTargets" 
              :key="item.id" 
              :class="['item-card', `r-${itemRarity(item)}`, { active: targetItem?.id === item.id, disabled: isTargetDisabled(item) }]"
              @click="selectTarget(item)"
            >
              <div class="item-img-wrap">
                <img v-if="item.image_url" :src="item.image_url" alt="" />
                <i v-else :class="['fas', itemIcon(item)]"></i>
              </div>
              <span class="name">{{ item.name }}</span>
              <span class="price">{{ formatMoney(item.price) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>


    <UpgradeRoulette 
      :visible="modalVisible" 
      :is-win="lastResult.isWin"
      :chance="Number(chance)"
      :target-item="targetItem" 
      :source-item="sourceItem?.item_details" 
      @close="closeModal" 
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import UpgradeRoulette from '../components/upgrade/UpgradeRoulette.vue'
import { getInventory, getAllItems, doUpgrade, getItemIcon } from '../api'
import { useUserStore } from '../stores/user'
import { useToastStore } from '../stores/toast'

const userStore = useUserStore()
const toast = useToastStore()

const inventory = ref([])
const allItems = ref([])
const sourceItem = ref(null) 
const targetItem = ref(null) 

const searchQuery = ref('')
const filterRarity = ref('all')
const sortBy = ref('price_asc')

const upgrading = ref(false)
const modalVisible = ref(false)
const lastResult = ref({ isWin: false })

const formatMoney = (n) => new Intl.NumberFormat('ru-RU').format(Math.round(Number(n) || 0)) + ' ₽'

function itemRarity(invOrItem) {
  const details = invOrItem.item_details || invOrItem;
  return details.rarity_class || details.rarity || 'common';
}
function itemIcon(invOrItem) {
  const details = invOrItem.item_details || invOrItem;
  return details.icon || getItemIcon(details.name);
}

const chance = computed(() => {
  if (!sourceItem.value || !targetItem.value) return 0
  const srcPrice = Number(sourceItem.value.item_details?.price || 0)
  const tgtPrice = Number(targetItem.value.price || 0)
  if (tgtPrice <= srcPrice) return 0
  const c = (srcPrice / tgtPrice) * 100
  return Math.min(c, 90).toFixed(1)
})

const canUpgrade = computed(() => sourceItem.value && targetItem.value && chance.value > 0)

const circleStyle = computed(() => {
  const c = Number(chance.value)
  const dashoffset = 282.7 - (282.7 * c) / 100
  return {
    strokeDasharray: 282.7,
    strokeDashoffset: dashoffset,
    stroke: c > 50 ? 'var(--success)' : (c > 20 ? 'var(--gold)' : 'var(--danger)')
  }
})

const filteredTargets = computed(() => {
  let result = allItems.value

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    result = result.filter(i => i.name.toLowerCase().includes(q))
  }

  if (filterRarity.value !== 'all') {
    result = result.filter(i => itemRarity(i) === filterRarity.value)
  }

  result = [...result].sort((a, b) => {
    if (sortBy.value === 'price_asc') return Number(a.price) - Number(b.price)
    if (sortBy.value === 'price_desc') return Number(b.price) - Number(a.price)
    if (sortBy.value === 'name') return a.name.localeCompare(b.name)
    return 0
  })

  return result
})

function isTargetDisabled(item) {
  if (!sourceItem.value) return false
  return Number(item.price) <= Number(sourceItem.value.item_details?.price)
}

function selectTarget(item) {
  if (isTargetDisabled(item)) {
    toast.info('Целевой предмет должен быть дороже выбранного')
    return
  }
  targetItem.value = item
}

async function loadData() {
  try {
    inventory.value = await getInventory()
    const res = await getAllItems()
    if (res.success) allItems.value = res.items
  } catch (e) {
    toast.error('Ошибка загрузки данных')
  }
}

async function handleUpgrade() {
  if (!canUpgrade.value) return
  upgrading.value = true
  
  try {
    const res = await doUpgrade(sourceItem.value.id, targetItem.value.id)
    if (res.success) {
      lastResult.value.isWin = res.is_win
      modalVisible.value = true
      inventory.value = res.inventory
    } else {
      toast.error(res.error)
    }
  } catch (e) {
    toast.error(e.response?.data?.error || 'Ошибка сети')
  } finally {
    upgrading.value = false
  }
}

function closeModal() {
  modalVisible.value = false
  if (lastResult.value.isWin) {
    sourceItem.value = null
    targetItem.value = null
  } else {
    sourceItem.value = null
  }
}

onMounted(async () => {
  if (!userStore.loaded) await userStore.fetchUser()
  if (!userStore.isAuth) {
    toast.error('Войдите, чтобы делать апгрейды')
    return
  }
  await loadData()
})
</script>

<style scoped>
.upgrade-layout {
  display: grid;
  grid-template-columns: 1fr 240px 1fr;
  gap: 24px;
  align-items: start;
}

.panel-title {
  font-size: 16px;
  font-weight: 800;
  margin-bottom: 16px;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 8px;
}
.panel-title i { color: var(--primary-light); }

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 12px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.item-card {
  position: relative;
  background: rgba(0,0,0,0.3);
  border: 2px solid var(--glass-border);
  border-radius: 12px;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: var(--transition);
}
.item-card:hover { background: rgba(255,255,255,0.05); }
.item-card.active { border-color: var(--primary); box-shadow: 0 0 20px var(--primary-glow); background: rgba(168,85,247,0.1); }
.item-card.disabled { opacity: 0.3; cursor: not-allowed; filter: grayscale(1); }

.item-img-wrap {
  height: 60px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}
.item-img-wrap img {
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5));
}
.item-img-wrap i {
  font-size: 32px; 
  color: #fff; 
  opacity: 0.9;
}

.item-card .name { font-size: 11px; text-align: center; font-weight: 700; line-height: 1.2; height: 26px; overflow: hidden; }
.item-card .price { font-size: 12px; color: var(--gold); font-weight: 800; }
.qty { position: absolute; top: 4px; right: 4px; background: #000; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: 800; z-index: 2; }

.item-card.r-common { border-color: rgba(148,163,184,0.3); }
.item-card.r-rare { border-color: rgba(16,185,129,0.4); }
.item-card.r-epic { border-color: rgba(168,85,247,0.5); }
.item-card.r-legendary { border-color: rgba(251,191,36,0.6); }
.item-card.r-ancient { border-color: rgba(239,68,68,0.7); }

.center-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 30px;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  padding: 30px 20px;
  position: sticky;
  top: 100px;
}

.chance-circle {
  position: relative;
  width: 140px;
  height: 140px;
}
.circle-svg { transform: rotate(-90deg); width: 100%; height: 100%; }
.circle-bg { fill: none; stroke: rgba(255,255,255,0.05); stroke-width: 8; }
.circle-fill { fill: none; stroke-width: 8; stroke-linecap: round; transition: stroke-dashoffset 0.5s ease, stroke 0.5s; }

.chance-text {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.chance-text strong { font-size: 28px; font-weight: 900; }
.chance-text span { font-size: 11px; color: var(--text-muted); text-transform: uppercase; }

.upgrade-btn { width: 100%; height: 60px; font-size: 18px; }

.empty-msg { text-align: center; color: var(--text-muted); padding: 20px; font-size: 14px; }

.filters {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}
.search-input { padding: 10px 14px; }
.filter-row {
  display: flex;
  gap: 8px;
}
.filter-row .select { flex: 1; padding: 10px 14px; }

@media (max-width: 992px) {
  .upgrade-layout { grid-template-columns: 1fr; }
  .center-panel { position: static; order: -1; }
  .items-grid { max-height: 400px; }
}
</style>
<template>
  <div class="page">
    <div class="container">
      <h1 class="title">Мой <span class="gradient">Профиль</span></h1>

      <div v-if="userStore.loading" class="loading-center">
        <div class="loader loader-lg"></div>
      </div>


      <div v-else-if="!userStore.isAuth" class="auth-required glass-card">
        <i class="fas fa-user-lock"></i>
        <h3>Войдите, чтобы увидеть профиль</h3>
        <p class="auth-hint">Нет аккаунта? Зарегистрируйтесь за 10 секунд</p>
        <div class="auth-actions">
          <router-link to="/login" class="btn btn-primary">
            <i class="fas fa-sign-in-alt"></i> Войти
          </router-link>
          <router-link to="/register" class="btn btn-ghost">
            <i class="fas fa-user-plus"></i> Регистрация
          </router-link>
        </div>
      </div>


      <template v-else>

        <div class="profile-card glass-card">
          <div class="profile-hero">
            <div class="avatar-wrap">
              <div class="avatar-placeholder">
                <i class="fas fa-user"></i>
              </div>
              <div class="online-badge"></div>
            </div>
            <div class="profile-info">
              <h2 class="nickname">{{ userStore.displayName }}</h2>
              <div class="status-badge">
                <span class="dot"></span> Аккаунт активен
              </div>
              <p v-if="userStore.user?.email" class="sub">
                <i class="fas fa-envelope"></i> {{ userStore.user.email }}
              </p>
              <p v-if="userStore.user?.trade_link" class="sub">
                <i class="fas fa-exchange-alt"></i> Trade-ссылка привязана
              </p>
            </div>
          </div>

          <div class="stats-grid">
            <div class="stat-box gold">
              <i class="fas fa-coins"></i>
              <div class="stat-val">{{ formatMoney(userStore.balance) }}</div>
              <div class="stat-lbl">Баланс</div>
            </div>
            <div class="stat-box">
              <i class="fas fa-box-open"></i>
              <div class="stat-val">{{ inventory.length }}</div>
              <div class="stat-lbl">Предметов</div>
            </div>
            <div class="stat-box">
              <i class="fas fa-gem"></i>
              <div class="stat-val">{{ formatMoney(totalValue) }}</div>
              <div class="stat-lbl">Стоимость</div>
            </div>
          </div>
        </div>

  
        <div class="inv-section">
          <div class="inv-header">
            <h2 class="section-title">Мой <span class="gradient">Инвентарь</span></h2>
            <button
              v-if="inventory.length > 0"
              class="btn btn-gold"
              :disabled="sellingAll"
              @click="handleSellAll"
            >
              <i v-if="sellingAll" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-fire"></i>
              {{ sellingAll ? 'Продаём...' : `Продать всё за ${formatMoney(totalValue)}` }}
            </button>
          </div>


          <div v-if="inventory.length === 0" class="empty-inv glass-card">
            <i class="fas fa-box-open"></i>
            <h3>Инвентарь пуст</h3>
            <p>Открывайте кейсы, чтобы получить скины</p>
            <router-link to="/" class="btn btn-primary">
              <i class="fas fa-dice"></i> К кейсам
            </router-link>
          </div>

          <div v-else class="inv-grid">
            <div
              v-for="inv in inventory"
              :key="inv.id"
              :class="['inv-card', `r-${rarityClass(inv)}`]"
            >
              <div v-if="inv.quantity > 1" class="qty-badge">x{{ inv.quantity }}</div>

              <div :class="['inv-icon', `bg-${rarityClass(inv)}`]">
                <img 
                  v-if="inv.item_details?.image_url" 
                  :src="inv.item_details.image_url" 
                  style="max-height: 80%; max-width: 80%; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5));" 
                />
                <i v-else :class="['fas', itemIcon(inv)]"></i>
              </div>

              <div class="inv-name">{{ inv.item_details?.name }}</div>

              <div class="inv-rarity">{{ rarityName(inv) }}</div>

              <div class="inv-price price">{{ formatMoney(inv.item_details?.price) }}</div>

              <button
                class="btn btn-ghost sell-btn"
                :disabled="sellingIds.has(inv.id)"
                @click="handleSell(inv)"
              >
                <i v-if="sellingIds.has(inv.id)" class="fas fa-spinner fa-spin"></i>
                <i v-else class="fas fa-coins"></i>
                {{ sellingIds.has(inv.id) ? '...' : 'Продать' }}
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { useToastStore } from '../stores/toast'
import { getInventory, sellItem, sellAllItems, getItemIcon, rarityName as getRarityName } from '../api'

const userStore = useUserStore()
const toast = useToastStore()

const inventory = ref([])
const sellingIds = ref(new Set())
const sellingAll = ref(false)

const totalValue = computed(() =>
  inventory.value.reduce(
    (sum, inv) => sum + Number(inv.item_details?.price || 0) * inv.quantity,
    0
  )
)

const formatMoney = (n) =>
  new Intl.NumberFormat('ru-RU').format(Math.round(Number(n) || 0)) + ' ₽'

// Берём редкость из бэка (после Блока 2.1 она приходит прямо в item_details)
function rarityClass(inv) {
  return (inv.item_details?.rarity_class || inv.item_details?.rarity || 'common').toLowerCase()
}
function rarityName(inv) {
  return inv.item_details?.rarity_name || getRarityName(inv.item_details?.rarity)
}
// Берём иконку из бэка, fallback — локальная функция по имени
function itemIcon(inv) {
  return inv.item_details?.icon || getItemIcon(inv.item_details?.name)
}

async function loadInventory() {
  try {
    inventory.value = await getInventory()
  } catch (e) {
    console.error(e)
  }
}

async function handleSell(inv) {
  if (!confirm(`Продать "${inv.item_details.name}" за ${formatMoney(inv.item_details.price)}?`)) {
    return
  }
  sellingIds.value.add(inv.id)
  try {
    const data = await sellItem(inv.id)
    if (data.success) {
      toast.success(`Продано за ${formatMoney(data.sold_price)}`)
      userStore.setBalance(data.new_balance)
      await loadInventory()
    } else {
      toast.error(data.error || 'Ошибка продажи')
    }
  } catch (e) {
    toast.error(e.response?.data?.error || 'Ошибка сети')
  } finally {
    sellingIds.value.delete(inv.id)
  }
}

async function handleSellAll() {
  if (!confirm(`Продать ВСЕ предметы за ${formatMoney(totalValue.value)}?`)) return
  sellingAll.value = true
  try {
    const data = await sellAllItems()
    if (data.success) {
      toast.success(
        `Продано ${data.items_count} предметов за ${formatMoney(data.total_price)}`
      )
      userStore.setBalance(data.new_balance)
      await loadInventory()
    } else {
      toast.error(data.error || 'Ошибка')
    }
  } catch (e) {
    toast.error(e.response?.data?.error || 'Ошибка сети')
  } finally {
    sellingAll.value = false
  }
}

onMounted(async () => {
  if (!userStore.loaded) await userStore.fetchUser()
  if (userStore.isAuth) await loadInventory()
})
</script>

<style scoped>

.auth-required {
  text-align: center;
  padding: 60px 30px;
  max-width: 520px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.auth-required > i {
  font-size: 64px;
  color: var(--primary);
  margin-bottom: 12px;
}
.auth-required h3 {
  font-size: 22px;
  margin-bottom: 4px;
}
.auth-hint {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 12px;
}
.auth-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.profile-card {
  padding: 40px;
  margin-bottom: 40px;
}
.profile-hero {
  display: flex;
  align-items: center;
  gap: 32px;
  margin-bottom: 32px;
}
.avatar-wrap {
  position: relative;
  flex-shrink: 0;
}
.avatar-placeholder {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  border: 4px solid var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 56px;
  color: #fff;
  box-shadow: 0 0 40px var(--primary-glow);
}
.online-badge {
  position: absolute;
  bottom: 6px;
  right: 6px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--success);
  border: 4px solid var(--bg);
  box-shadow: 0 0 12px var(--success);
  animation: pulse 2s infinite;
}

.profile-info {
  flex: 1;
  min-width: 0;
}
.nickname {
  font-size: 32px;
  font-weight: 900;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #fff, var(--primary-light));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 20px;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: var(--success);
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success);
  box-shadow: 0 0 10px var(--success);
  animation: pulse 2s infinite;
}
.sub {
  color: var(--text-muted);
  font-size: 14px;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.sub i {
  width: 16px;
  color: var(--primary-light);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.stat-box {
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  text-align: center;
  transition: var(--transition);
}
.stat-box:hover {
  transform: translateY(-3px);
  border-color: var(--glass-border-hover);
}
.stat-box i {
  font-size: 22px;
  color: var(--primary-light);
  margin-bottom: 8px;
}
.stat-box.gold i {
  color: var(--gold);
}
.stat-val {
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 4px;
}
.stat-box.gold .stat-val {
  color: var(--gold);
  text-shadow: 0 0 20px var(--gold-glow);
}
.stat-lbl {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

 
.inv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.inv-header .section-title {
  margin: 0;
}

.inv-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}
.inv-card {
  position: relative;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  transition: var(--transition);
}
.inv-card:hover {
  transform: translateY(-4px);
}
.inv-card.r-common {
  border-color: rgba(148, 163, 184, 0.4);
}
.inv-card.r-rare {
  border-color: rgba(16, 185, 129, 0.55);
}
.inv-card.r-rare:hover {
  box-shadow: 0 12px 32px rgba(16, 185, 129, 0.25);
}
.inv-card.r-epic {
  border-color: rgba(168, 85, 247, 0.6);
}
.inv-card.r-epic:hover {
  box-shadow: 0 12px 32px rgba(168, 85, 247, 0.3);
}
.inv-card.r-legendary {
  border-color: rgba(251, 191, 36, 0.7);
}
.inv-card.r-legendary:hover {
  box-shadow: 0 12px 32px rgba(251, 191, 36, 0.35);
}
.inv-card.r-ancient {
  border-color: rgba(239, 68, 68, 0.75);
}
.inv-card.r-ancient:hover {
  box-shadow: 0 12px 32px rgba(239, 68, 68, 0.4);
}

.qty-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 3px 8px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.7);
  font-size: 11px;
  font-weight: 800;
  border: 1px solid rgba(255, 255, 255, 0.15);
  z-index: 2;
}
.inv-icon {
  width: 100%;
  height: 110px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 42px;
  color: #fff;
  margin-bottom: 12px;
}
.bg-common {
  background: linear-gradient(135deg, #94a3b8, #64748b);
}
.bg-rare {
  background: linear-gradient(135deg, #10b981, #047857);
}
.bg-epic {
  background: linear-gradient(135deg, #a855f7, #7e22ce);
}
.bg-legendary {
  background: linear-gradient(135deg, #fbbf24, #d97706);
}
.bg-ancient {
  background: linear-gradient(135deg, #ef4444, #b91c1c);
}

.inv-name {
  font-size: 13px;
  font-weight: 700;
  text-align: center;
  min-height: 34px;
  margin-bottom: 4px;
}
.inv-rarity {
  font-size: 11px;
  text-align: center;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}
.inv-price {
  text-align: center;
  margin-bottom: 12px;
  font-size: 16px;
}
.sell-btn {
  width: 100%;
  padding: 8px;
  font-size: 13px;
}

.empty-inv {
  text-align: center;
  padding: 60px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.empty-inv i {
  font-size: 64px;
  color: var(--primary);
  opacity: 0.5;
  margin-bottom: 8px;
}
.empty-inv h3 {
  margin-bottom: 4px;
}
.empty-inv p {
  color: var(--text-muted);
  margin-bottom: 16px;
}

</style>
<template>
  <div class="page">
    <div class="container">
      <h1 class="title">Контракты <span class="gradient">CS:GO</span></h1>

      <div class="contract-layout">
        
        <div class="glass-card selected-panel">
          <h3 class="panel-title">
            <i class="fas fa-handshake"></i> Ваш контракт
            <span class="counter" :class="{ ready: selectedItems.length >= 3 }">
              {{ selectedItems.length }} / 10
            </span>
          </h3>
          
          <div class="selected-grid">
            <div 
              v-for="(inv, index) in selectedItems" 
              :key="inv._uid" 
              :class="['selected-slot', `r-${rarityClass(inv)}`]"
              @click="removeItem(index)"
            >
              <div class="slot-img">
                <img v-if="inv.item_details?.image_url" :src="inv.item_details.image_url" alt="" />
                <i v-else :class="['fas', itemIcon(inv)]"></i>
              </div>
              <span class="slot-price">{{ formatMoney(inv.item_details?.price) }}</span>
              <div class="remove-icon"><i class="fas fa-times"></i></div>
            </div>
            

            <div v-for="n in Math.max(0, 3 - selectedItems.length)" :key="`empty-${n}`" class="selected-slot empty">
              <i class="fas fa-plus"></i>
            </div>
            <div v-for="n in Math.max(0, 10 - Math.max(3, selectedItems.length))" :key="`dashed-${n}`" class="selected-slot dashed">
              <i class="fas fa-plus"></i>
            </div>
          </div>

          <div class="contract-info">
            <div class="info-row">
              <span>Сумма контракта:</span>
              <strong class="price">{{ formatMoney(totalSelectedPrice) }}</strong>
            </div>
            <div class="chances-info">
              <div class="chance-line"><span class="dot low"></span> 60% — предмет до {{ formatMoney(totalSelectedPrice) }}</div>
              <div class="chance-line"><span class="dot mid"></span> 30% — предмет до {{ formatMoney(totalSelectedPrice * 1.5) }}</div>
              <div class="chance-line"><span class="dot high"></span> 10% — предмет до {{ formatMoney(totalSelectedPrice * 3) }}</div>
            </div>
          </div>

          <button 
            class="btn btn-primary btn-lg w-full" 
            :disabled="selectedItems.length < 3 || selectedItems.length > 10 || processing"
            @click="handleContract"
          >
            <div v-if="processing" class="loader"></div>
            <i v-else class="fas fa-magic"></i>
            {{ processing ? 'Заключаем...' : 'Заключить контракт' }}
          </button>
        </div>


        <div class="glass-card inventory-panel">
          <h3 class="panel-title"><i class="fas fa-box"></i> Мой инвентарь</h3>
          
          <div v-if="inventory.length === 0" class="empty-msg">
            <i class="fas fa-box-open"></i>
            <p>Инвентарь пуст</p>
            <router-link to="/" class="btn btn-primary mt-3">К кейсам</router-link>
          </div>
          
          <div v-else class="items-grid">
            <div 
              v-for="inv in availableItems" 
              :key="inv.id" 
              :class="['item-card', `r-${rarityClass(inv)}`]"
              @click="addItem(inv)"
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

      </div>
    </div>

    <ContractModal 
      :visible="modalVisible" 
      :won-item="wonItem" 
      @close="closeModal" 
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ContractModal from '../components/contract/ContractModal.vue'
import { getInventory, doContract, getItemIcon, rarityClass as getRarityClass } from '../api'
import { useUserStore } from '../stores/user'
import { useToastStore } from '../stores/toast'

const userStore = useUserStore()
const toast = useToastStore()

const inventory = ref([])
const selectedItems = ref([]) 
const processing = ref(false)
const modalVisible = ref(false)
const wonItem = ref(null)

const formatMoney = (n) => new Intl.NumberFormat('ru-RU').format(Math.round(Number(n) || 0)) + ' ₽'

function rarityClass(inv) {
  return getRarityClass(inv.item_details?.rarity_class || inv.item_details?.rarity)
}
function itemIcon(inv) {
  return inv.item_details?.icon || getItemIcon(inv.item_details?.name)
}

const totalSelectedPrice = computed(() => {
  return selectedItems.value.reduce((sum, inv) => sum + Number(inv.item_details?.price || 0), 0)
})


const availableItems = computed(() => {
  return inventory.value.map(inv => {
    const inContractCount = selectedItems.value.filter(s => s.inventoryId === inv.id).length
    return {
      ...inv,
      availableQuantity: inv.quantity - inContractCount
    }
  }).filter(inv => inv.availableQuantity > 0)
})

function addItem(inv) {
  if (selectedItems.value.length >= 10) {
    toast.info('Максимум 10 предметов')
    return
  }

  selectedItems.value.push({
    ...inv,
    inventoryId: inv.id, 
    _uid: Date.now() + Math.random() 
  })
}

function removeItem(index) {
  selectedItems.value.splice(index, 1)
}

async function loadInventory() {
  try {
    inventory.value = await getInventory()
  } catch (e) {
    toast.error('Ошибка загрузки инвентаря')
  }
}

async function handleContract() {
  if (selectedItems.value.length < 3) return
  processing.value = true
  
  try {

    const ids = selectedItems.value.map(inv => inv.inventoryId)
    
    const res = await doContract(ids)
    if (res.success) {
      wonItem.value = res.won_item
      inventory.value = res.inventory
      selectedItems.value = []
      modalVisible.value = true
      toast.success('Контракт выполнен!')
    } else {
      toast.error(res.error)
    }
  } catch (e) {
    toast.error(e.response?.data?.error || 'Ошибка сети')
  } finally {
    processing.value = false
  }
}

function closeModal() {
  modalVisible.value = false
}

onMounted(async () => {
  if (!userStore.loaded) await userStore.fetchUser()
  if (!userStore.isAuth) {
    toast.error('Войдите, чтобы заключать контракты')
    return
  }
  await loadInventory()
})
</script>

<style scoped>
.contract-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

/* ЛЕВАЯ ПАНЕЛЬ */
.selected-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-title {
  font-size: 18px;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 8px;
}
.panel-title i { color: var(--primary-light); }

.counter {
  margin-left: auto;
  font-size: 14px;
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(255,255,255,0.05);
  color: var(--text-muted);
}
.counter.ready {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.selected-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  min-height: 120px;
}

.selected-slot {
  position: relative;
  aspect-ratio: 1;
  background: rgba(0,0,0,0.4);
  border: 2px solid var(--glass-border);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
}
.selected-slot:hover { background: rgba(239, 68, 68, 0.1); border-color: var(--danger); }
.selected-slot.empty {
  border-color: var(--glass-border);
  opacity: 0.5;
  cursor: default;
}
.selected-slot.empty:hover { background: rgba(0,0,0,0.4); border-color: var(--glass-border); }
.selected-slot.dashed {
  border-style: dashed;
  opacity: 0.3;
  cursor: default;
}
.selected-slot.dashed:hover { background: rgba(0,0,0,0.4); border-color: var(--glass-border); }

.selected-slot.empty i, .selected-slot.dashed i {
  font-size: 20px;
  color: var(--text-muted);
}

.slot-img {
  width: 100%;
  height: 60%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.slot-img img { max-width: 90%; max-height: 100%; object-fit: contain; }
.slot-img i { font-size: 24px; color: #fff; }

.slot-price {
  font-size: 11px;
  color: var(--gold);
  font-weight: 800;
  margin-top: 4px;
}

.remove-icon {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  background: var(--danger);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  opacity: 0;
  transition: var(--transition);
}
.selected-slot:hover .remove-icon { opacity: 1; }

/* Рамки редкостей для слотов */
.selected-slot.r-common { border-color: rgba(148, 163, 184, 0.5); }
.selected-slot.r-rare { border-color: rgba(16, 185, 129, 0.7); }
.selected-slot.r-epic { border-color: rgba(168, 85, 247, 0.7); }
.selected-slot.r-legendary { border-color: rgba(251, 191, 36, 0.9); }
.selected-slot.r-ancient { border-color: rgba(239, 68, 68, 0.9); }

.contract-info {
  background: rgba(0,0,0,0.2);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid var(--glass-border);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 15px;
}
.info-row .price { font-size: 20px; }

.chances-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
  color: var(--text-muted);
}
.chance-line {
  display: flex;
  align-items: center;
  gap: 8px;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.dot.low { background: var(--text-muted); }
.dot.mid { background: var(--gold); }
.dot.high { background: var(--danger); box-shadow: 0 0 10px var(--danger); }

/* ПРАВАЯ ПАНЕЛЬ */
.inventory-panel {
  max-height: 700px;
  display: flex;
  flex-direction: column;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 12px;
  overflow-y: auto;
  padding-right: 8px;
}

.item-card {
  position: relative;
  background: rgba(0,0,0,0.3);
  border: 2px solid var(--glass-border);
  border-radius: 12px;
  padding: 10px 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: var(--transition);
}
.item-card:hover { background: rgba(255,255,255,0.05); transform: translateY(-2px); }

.item-img-wrap {
  height: 50px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.item-img-wrap img { max-height: 100%; max-width: 100%; object-fit: contain; }
.item-img-wrap i { font-size: 28px; color: #fff; opacity: 0.9; }

.item-card .name { font-size: 11px; text-align: center; font-weight: 700; line-height: 1.2; height: 26px; overflow: hidden; }
.item-card .price { font-size: 12px; color: var(--gold); font-weight: 800; }
.qty { position: absolute; top: 4px; right: 4px; background: #000; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: 800; z-index: 2; }

.item-card.r-common { border-color: rgba(148,163,184,0.3); }
.item-card.r-rare { border-color: rgba(16,185,129,0.4); }
.item-card.r-epic { border-color: rgba(168,85,247,0.5); }
.item-card.r-legendary { border-color: rgba(251,191,36,0.6); }
.item-card.r-ancient { border-color: rgba(239,68,68,0.7); }

.empty-msg {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 20px;
}
.empty-msg i { font-size: 48px; opacity: 0.3; margin-bottom: 12px; }

@media (max-width: 992px) {
  .contract-layout { grid-template-columns: 1fr; }
  .selected-grid { grid-template-columns: repeat(5, 1fr); }
}
@media (max-width: 600px) {
  .selected-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
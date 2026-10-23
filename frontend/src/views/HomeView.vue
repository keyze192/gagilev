<template>
  <div class="page">
    <div class="container">
      <h1 class="title">
        Популярные <span class="gradient">Кейсы</span>
      </h1>

      <!-- Фильтры -->
      <div class="filters">
        <div class="search-wrap">
          <i class="fas fa-search"></i>
          <input
            v-model="search"
            class="input"
            placeholder="Поиск кейсов..."
          />
          <button v-if="search" class="clear" @click="search = ''">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <select v-model="priceRange" class="input select">
          <option value="all">Любая цена</option>
          <option value="0-500">До 500 ₽</option>
          <option value="500-1000">500–1000 ₽</option>
          <option value="1000-5000">1000–5000 ₽</option>
          <option value="5000+">От 5000 ₽</option>
        </select>
        <select v-model="sortBy" class="input select">
          <option value="popular">По популярности</option>
          <option value="price-asc">Цена ↑</option>
          <option value="price-desc">Цена ↓</option>
          <option value="name">По названию</option>
        </select>
      </div>

      <div v-if="loading" class="loading-center">
        <div class="loader loader-lg"></div>
        <span>Загрузка кейсов...</span>
      </div>

      <div v-else-if="filtered.length === 0" class="empty">
        <i class="fas fa-search"></i>
        <h3>Кейсы не найдены</h3>
        <p>Попробуйте изменить фильтры</p>
      </div>

      <div v-else class="cases-grid">
        <CaseCard
          v-for="c in filtered"
          :key="c.id"
          :case-data="c"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CaseCard from '../components/case/CaseCard.vue'
import { getCases } from '../api'

const cases = ref([])
const loading = ref(true)
const search = ref('')
const priceRange = ref('all')
const sortBy = ref('popular')

const filtered = computed(() => {
  let result = [...cases.value]

  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    result = result.filter(c => c.name.toLowerCase().includes(q))
  }

  if (priceRange.value !== 'all') {
    result = result.filter(c => {
      const p = Number(c.price)
      switch (priceRange.value) {
        case '0-500': return p <= 500
        case '500-1000': return p > 500 && p <= 1000
        case '1000-5000': return p > 1000 && p <= 5000
        case '5000+': return p > 5000
        default: return true
      }
    })
  }

  if (sortBy.value === 'price-asc') result.sort((a, b) => a.price - b.price)
  if (sortBy.value === 'price-desc') result.sort((a, b) => b.price - a.price)
  if (sortBy.value === 'name') result.sort((a, b) => a.name.localeCompare(b.name))

  return result
})

onMounted(async () => {
  try {
    cases.value = await getCases()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}
.search-wrap {
  flex: 1;
  min-width: 240px;
  position: relative;
  display: flex;
  align-items: center;
}
.search-wrap > i {
  position: absolute;
  left: 16px;
  color: var(--text-muted);
  font-size: 14px;
}
.search-wrap .input { padding-left: 42px; padding-right: 42px; }
.clear {
  position: absolute;
  right: 10px;
  width: 24px; height: 24px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.clear:hover { background: var(--glass); color: var(--text); }
.select { min-width: 160px; }
.cases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}
.empty {
  text-align: center;
  padding: 100px 20px;
  color: var(--text-muted);
}
.empty i { font-size: 56px; margin-bottom: 16px; color: var(--primary); opacity: 0.5; }
.empty h3 { color: var(--text); font-size: 20px; margin-bottom: 8px; }
</style>
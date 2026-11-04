<template>
  <div class="page container">
    <h1 class="title">Список <span class="gradient">Пользователей</span></h1>

    <div v-if="loading" class="loading-center">
      <div class="loader loader-lg"></div>
    </div>

    <div v-else-if="error" class="empty glass-card">
      <i class="fas fa-exclamation-triangle"></i>
      <h3>Не удалось загрузить пользователей</h3>
      <p>{{ error }}</p>
      <button class="btn btn-primary mt-3" @click="loadUsers">
        <i class="fas fa-redo"></i> Повторить
      </button>
    </div>

    <div v-else class="glass-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Никнейм</th>
            <th>Steam ID</th>
            <th>Баланс</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>
              <div class="user-info">
                <img v-if="user.steam_avatar" :src="user.steam_avatar" class="mini-avatar" alt="" />
                <span>{{ user.display_name || user.user_name || '—' }}</span>
              </div>
            </td>
            <td>{{ user.steam_id || 'Нет' }}</td>
            <td class="price">{{ formatMoney(user.balance) }}</td>
            <td>
              <button
                class="btn btn-ghost btn-sm"
                @click="deleteUserItem(user.id)"
                title="Удалить"
                :disabled="deletingIds.has(user.id)"
              >
                <i v-if="deletingIds.has(user.id)" class="fas fa-spinner fa-spin"></i>
                <i v-else class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="5" class="empty-row">Пользователей пока нет</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getUsers, deleteUser } from '../api'
import { useToastStore } from '../stores/toast'

const toast = useToastStore()

const users = ref([])
const loading = ref(true)
const error = ref('')
const deletingIds = ref(new Set())

const formatMoney = (n) =>
  new Intl.NumberFormat('ru-RU').format(Math.round(Number(n) || 0)) + ' ₽'

const loadUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    users.value = await getUsers()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка сети'
  } finally {
    loading.value = false
  }
}

const deleteUserItem = async (id) => {
  if (!confirm('Удалить пользователя?')) return
  deletingIds.value.add(id)
  try {
    await deleteUser(id)
    toast.success('Пользователь удалён')
    await loadUsers()
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Ошибка удаления (нужны права админа)')
  } finally {
    deletingIds.value.delete(id)
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.empty {
  text-align: center;
  padding: 60px 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
}
.empty i {
  font-size: 56px;
  color: var(--danger);
  opacity: 0.6;
  margin-bottom: 8px;
}
.empty h3 {
  color: var(--text);
  margin-bottom: 4px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
.data-table th, .data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--glass-border);
}
.data-table th {
  background: rgba(255, 255, 255, 0.05);
  font-weight: 700;
  color: var(--text-muted);
}
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.mini-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}
.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}
.empty-row {
  text-align: center;
  color: var(--text-muted);
  padding: 30px;
}
</style>
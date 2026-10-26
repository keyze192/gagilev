<template>
  <div class="page container">
    <h1 class="title">Список <span class="gradient">Пользователей</span></h1>

    <div v-if="loading" class="loading-center">
      <div class="loader loader-lg"></div>
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
                <img v-if="user.steam_avatar" :src="user.steam_avatar" class="mini-avatar" />
                <span>{{ user.display_name }}</span>
              </div>
            </td>
            <td>{{ user.steam_id || 'Нет' }}</td>
            <td class="price">{{ user.balance }} ₽</td>
            <td>
              <button class="btn btn-ghost btn-sm" @click="deleteUserItem(user.id)" title="Удалить">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getUsers, deleteUser } from '../api'

const users = ref([])
const loading = ref(true)

const loadUsers = async () => {
  loading.value = true
  try {
    users.value = await getUsers()
  } catch (e) {
    console.error('Ошибка загрузки:', e)
  } finally {
    loading.value = false
  }
}

const deleteUserItem = async (id) => {
  if (!confirm('Удалить пользователя?')) return
  try {
    await deleteUser(id)
    loadUsers() 
  } catch (e) {
    alert('Ошибка удаления (нужны права админа)')
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
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
}
.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}
</style>
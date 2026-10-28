<template>
  <div class="page">
    <div class="container">
      <div class="auth-card glass-card">
        <h1 class="title">Регистрация</h1>
        <form @submit.prevent="submit">
          <input v-model="username" class="input" placeholder="Логин" />
          <input v-model="email" type="email" class="input" placeholder="Email (необязательно)" />
          <input v-model="password" type="password" class="input" placeholder="Пароль (мин. 6 символов)" />
          <button class="btn btn-primary w-full" :disabled="loading">
            <i class="fas fa-user-plus"></i> {{ loading ? '...' : 'Создать аккаунт' }}
          </button>
        </form>
        <p class="alt">Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useToastStore } from '../stores/toast'

const router = useRouter()
const userStore = useUserStore()
const toast = useToastStore()

const username = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)

async function submit() {
  if (!username.value || !password.value) {
    toast.error('Заполните логин и пароль'); return
  }
  loading.value = true
  try {
    await userStore.register(username.value.trim(), password.value, email.value.trim())
    toast.success('Аккаунт создан!')
    router.push('/')
  } catch (e) {
    toast.error(e.response?.data?.error || 'Ошибка регистрации')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-card { max-width: 420px; margin: 40px auto; display: flex; flex-direction: column; gap: 14px; }
.auth-card .input { padding: 14px 16px; }
.alt { text-align: center; color: var(--text-muted); font-size: 14px; }
.alt a { color: var(--primary-light); font-weight: 700; }
</style>
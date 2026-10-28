<template>
  <div class="page">
    <div class="container">
      <div class="auth-card glass-card">
        <h1 class="title">Вход</h1>
        <form @submit.prevent="submit">
          <input v-model="username" class="input" placeholder="Логин" autocomplete="username" />
          <input v-model="password" type="password" class="input" placeholder="Пароль" autocomplete="current-password" />
          <button class="btn btn-primary w-full" :disabled="loading">
            <i class="fas fa-sign-in-alt"></i> {{ loading ? 'Вход...' : 'Войти' }}
          </button>
        </form>
        <p class="alt">Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useToastStore } from '../stores/toast'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const toast = useToastStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function submit() {
  if (!username.value || !password.value) {
    toast.error('Заполните все поля')
    return
  }
  loading.value = true
  try {
    await userStore.login(username.value.trim(), password.value)
    toast.success('Добро пожаловать!')
    router.push(route.query.redirect || '/')
  } catch (e) {
    toast.error(e.response?.data?.error || 'Ошибка входа')
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
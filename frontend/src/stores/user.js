import { defineStore } from 'pinia'
import { getCurrentUser, apiLogin, apiRegister, apiLogout } from '../api'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('auth_token') || null,
    loading: false,
    loaded: false,
  }),
  getters: {
    isAuth: (s) => !!s.user,
    balance: (s) => s.user?.balance ?? 0,
    displayName: (s) => s.user?.display_name || s.user?.user_name || 'Гость',
    avatar: () => null,
  },
  actions: {
    async fetchUser() {
      if (!this.token) { this.loaded = true; return }
      this.loading = true
      try {
        this.user = await getCurrentUser()
      } catch (e) {
        this.user = null
        this.token = null
        localStorage.removeItem('auth_token')
      } finally {
        this.loading = false
        this.loaded = true
      }
    },
    async login(username, password) {
      const data = await apiLogin(username, password)
      this.token = data.token
      this.user = data.user
      localStorage.setItem('auth_token', data.token)
    },
    async register(username, password, email) {
      const data = await apiRegister(username, password, email)
      this.token = data.token
      this.user = data.user
      localStorage.setItem('auth_token', data.token)
    },
    async logout() {
      try { await apiLogout() } catch {}
      this.user = null
      this.token = null
      localStorage.removeItem('auth_token')
    },
    setBalance(newBalance) {
      if (this.user) this.user.balance = newBalance
    },
  },
})
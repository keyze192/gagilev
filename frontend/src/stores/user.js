import { defineStore } from 'pinia'
import { getCurrentUser } from '../api'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    loading: false,
    loaded: false,
  }),
  getters: {
    isAuth: (s) => !!s.user,
    balance: (s) => s.user?.balance ?? 0,
    displayName: (s) => s.user?.display_name || s.user?.steam_username || 'Гость',
    avatar: (s) => s.user?.steam_avatar || null,
  },
  actions: {
    async fetchUser() {
      this.loading = true
      try {
        this.user = await getCurrentUser()
      } catch (e) {
        console.error(e)
        this.user = null
      } finally {
        this.loading = false
        this.loaded = true
      }
    },
    setBalance(newBalance) {
      if (this.user) this.user.balance = newBalance
    },
    logout() {
      this.user = null
      window.location.href = '/logout/'
    },
  },
})
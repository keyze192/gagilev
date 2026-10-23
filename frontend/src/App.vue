<template>
  <AppHeader />
  <main>
    <router-view />
  </main>
  <AppFooter />
  <ToastContainer />
</template>

<script setup>
import { onMounted } from 'vue'
import AppHeader from './components/layout/AppHeader.vue'
import AppFooter from './components/layout/AppFooter.vue'
import ToastContainer from './components/layout/ToastContainer.vue'
import { useUserStore } from './stores/user'

const userStore = useUserStore()
onMounted(() => userStore.fetchUser())
</script>
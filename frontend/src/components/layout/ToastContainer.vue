<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div
        v-for="t in toastStore.toasts"
        :key="t.id"
        :class="['toast', `toast-${t.type}`]"
        @click="toastStore.remove(t.id)"
      >
        <i :class="['fas', iconFor(t.type)]"></i>
        <span>{{ t.message }}</span>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToastStore } from '../../stores/toast'
const toastStore = useToastStore()

const iconFor = (type) => ({
  success: 'fa-check-circle',
  error: 'fa-exclamation-circle',
  info: 'fa-info-circle',
}[type] || 'fa-info-circle')
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 100px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 380px;
  pointer-events: none;
}
.toast {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: rgba(15, 20, 32, 0.95);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  backdrop-filter: blur(20px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
}
.toast:hover { transform: translateX(-4px); }
.toast i { font-size: 18px; }
.toast-success { border-color: rgba(16, 185, 129, 0.4); color: var(--success); }
.toast-error { border-color: rgba(239, 68, 68, 0.4); color: var(--danger); }
.toast-info { border-color: var(--glass-border-hover); color: var(--primary-light); }

.toast-enter-active, .toast-leave-active { transition: all 0.35s ease; }
.toast-enter-from { opacity: 0; transform: translateX(40px); }
.toast-leave-to { opacity: 0; transform: translateX(40px); }
</style>
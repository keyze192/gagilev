<template>
  <header class="header">
    <div class="container header-inner">
      <router-link to="/" class="logo">
        <div class="logo-icon">
          <i class="fas fa-dice"></i>
        </div>
        <span class="logo-text">LUCK<span class="gradient">BATTLE</span></span>
      </router-link>

      <nav class="nav">
        <router-link to="/users" class="nav-link">
          <i class="fas fa-users"></i> Юзеры
        </router-link>
        <router-link to="/" class="nav-link">
          <i class="fas fa-home"></i> Главная
        </router-link>
        <router-link to="/upgrade" class="nav-link">
          <i class="fas fa-arrow-up"></i> Апгрейд
        </router-link>
        <router-link to="/contract" class="nav-link">
          <i class="fas fa-handshake"></i> Контракт
        </router-link>
        <router-link to="/profile" class="nav-link">
          <i class="fas fa-user"></i> Профиль
        </router-link>
      </nav>

      <div class="header-right">
        <template v-if="userStore.loading">
          <div class="loader"></div>
        </template>
        <template v-else-if="userStore.isAuth">
          <div class="balance-badge">
            <i class="fas fa-coins"></i>
            <span>{{ formatMoney(userStore.balance) }}</span>
          </div>
          <div class="user-menu">
            <button class="user-btn" @click="toggleMenu">
              <img v-if="userStore.avatar" :src="userStore.avatar" class="avatar" alt="" />
              <i v-else class="fas fa-user-circle"></i>
              <span class="username">{{ userStore.displayName }}</span>
              <i class="fas fa-chevron-down caret"></i>
            </button>
            <transition name="drop">
              <div v-if="menuOpen" class="dropdown" @click="menuOpen = false">
                <router-link to="/profile" class="dropdown-item">
                  <i class="fas fa-id-card"></i> Профиль
                </router-link>
                <div class="divider"></div>
                <button class="dropdown-item danger" @click="userStore.logout()">
                  <i class="fas fa-sign-out-alt"></i> Выйти
                </button>
              </div>
            </transition>
          </div>
        </template>
        <template v-else>
          <a href="/steam/login/" class="btn btn-primary steam-btn">
            <i class="fab fa-steam"></i> Войти
          </a>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const menuOpen = ref(false)

function toggleMenu(e) {
  e.stopPropagation()
  menuOpen.value = !menuOpen.value
}
function closeMenu() { menuOpen.value = false }
function formatMoney(n) {
  return new Intl.NumberFormat('ru-RU').format(Math.round(n)) + ' ₽'
}

onMounted(() => document.addEventListener('click', closeMenu))
onUnmounted(() => document.removeEventListener('click', closeMenu))
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(5, 7, 13, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-bottom: 1px solid var(--glass-border);
}
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 76px;
  gap: 24px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 900;
  font-size: 18px;
  letter-spacing: -0.02em;
}
.logo-icon {
  width: 40px; height: 40px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
  color: #fff;
  font-size: 18px;
  box-shadow: 0 8px 24px var(--primary-glow);
  transition: var(--transition);
}
.logo:hover .logo-icon { transform: rotate(-10deg) scale(1.05); }
.logo-text { font-size: 18px; }
.logo-text .gradient {
  background: linear-gradient(135deg, var(--primary-light), var(--accent-light));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.nav {
  display: flex;
  gap: 4px;
  flex: 1;
  justify-content: center;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  color: var(--text-muted);
  font-weight: 600;
  font-size: 14px;
  transition: var(--transition);
  position: relative;
}
.nav-link:hover { color: var(--text); background: var(--glass); }
.nav-link.router-link-active {
  color: var(--text);
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(6, 182, 212, 0.1));
  border: 1px solid var(--glass-border-hover);
}
.nav-link.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -1px; left: 20%; right: 20%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.balance-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.15), rgba(251, 191, 36, 0.05));
  border: 1px solid rgba(251, 191, 36, 0.3);
  font-weight: 800;
  font-size: 15px;
  color: var(--gold);
  box-shadow: 0 0 20px rgba(251, 191, 36, 0.15);
}
.balance-badge i { font-size: 14px; }
.user-menu { position: relative; }
.user-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px 6px 6px;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: 30px;
  color: var(--text);
  font-weight: 600;
  font-size: 14px;
  transition: var(--transition);
}
.user-btn:hover { border-color: var(--glass-border-hover); background: var(--glass-hover); }
.avatar { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; }
.user-btn > i.fa-user-circle { font-size: 24px; color: var(--primary-light); }
.username { max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.caret { font-size: 10px; color: var(--text-muted); }
.dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  min-width: 200px;
  background: rgba(15, 20, 32, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 6px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.7);
}
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  border-radius: 8px;
  color: var(--text);
  font-weight: 600;
  font-size: 14px;
  background: none;
  border: none;
  text-align: left;
  transition: var(--transition);
}
.dropdown-item:hover { background: var(--glass); color: var(--primary-light); }
.dropdown-item.danger:hover { background: rgba(239, 68, 68, 0.1); color: var(--danger); }
.dropdown-item i { width: 16px; color: var(--primary-light); }
.dropdown-item.danger i { color: var(--danger); }
.divider { height: 1px; background: var(--glass-border); margin: 4px 0; }
.steam-btn { padding: 10px 20px; }
.drop-enter-active, .drop-leave-active { transition: var(--transition); }
.drop-enter-from, .drop-leave-to { opacity: 0; transform: translateY(-8px); }

@media (max-width: 900px) {
  .nav { display: none; }
  .username { display: none; }
}
</style>
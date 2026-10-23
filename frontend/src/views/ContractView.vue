<template>
  <div class="page">
    <div class="container">
      <h1 class="title">Контракты <span class="gradient">CS:GO</span></h1>
      <div class="coming glass-card">
        <div class="coming-icon"><i class="fas fa-handshake"></i></div>
        <h2>Скоро будет доступно</h2>
        <p>Обменивайте 10 предметов на 1 более ценный</p>
        <router-link to="/" class="btn btn-primary mt-3">
          <i class="fas fa-arrow-left"></i> На главную
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.coming { text-align: center; padding: 80px 40px; max-width: 600px; margin: 0 auto; }
.coming-icon {
  width: 100px; height: 100px; margin: 0 auto 24px;
  border-radius: 24px;
  background: linear-gradient(135deg, var(--accent), var(--primary));
  display: flex; align-items: center; justify-content: center;
  font-size: 44px; color: #fff;
  box-shadow: 0 20px 60px var(--accent-glow);
  animation: float 3s ease-in-out infinite;
}
.coming h2 { font-size: 24px; margin-bottom: 8px; }
.coming p { color: var(--text-muted); margin-bottom: 8px; }
</style>
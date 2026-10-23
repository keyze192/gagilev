<template>
  <div class="page">
    <div class="container">
      <div class="nf">
        <div class="nf-404">404</div>
        <h2>Страница не найдена</h2>
        <p>Возможно, она была перемещена или удалена</p>
        <router-link to="/" class="btn btn-primary mt-3">
          <i class="fas fa-home"></i> На главную
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.nf { text-align: center; padding: 100px 20px; }
.nf-404 {
  font-size: 120px;
  font-weight: 900;
  background: linear-gradient(135deg, var(--primary-light), var(--accent-light));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 20px;
  text-shadow: 0 0 80px var(--primary-glow);
}
.nf h2 { font-size: 24px; margin-bottom: 8px; }
.nf p { color: var(--text-muted); margin-bottom: 8px; }
</style>
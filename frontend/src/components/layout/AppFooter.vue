<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          <div class="logo">
            <div class="logo-icon"><i class="fas fa-dice"></i></div>
            <span>LUCK<span class="gradient">BATTLE</span></span>
          </div>
          <p class="footer-desc">Открывай кейсы, выигрывай скины CS:GO</p>
        </div>
        <div>
          <h4>Платформа</h4>
          <ul>
            <li><router-link to="/">Главная</router-link></li>
            <li><router-link to="/upgrade">Апгрейд</router-link></li>
            <li><router-link to="/contract">Контракт</router-link></li>
            <li><router-link to="/profile">Профиль</router-link></li>
          </ul>
        </div>
        <div>
          <h4>Поддержка</h4>
          <ul>
            <li><a href="#">FAQ</a></li>
            <li><a href="#">Правила</a></li>
            <li><a href="#">Контакты</a></li>
          </ul>
        </div>
        <div>
          <h4>Сообщество</h4>
          <ul>
            <li><a href="#"><i class="fab fa-steam"></i> Steam</a></li>
            <li><a href="#"><i class="fab fa-discord"></i> Discord</a></li>
            <li><a href="#"><i class="fab fa-telegram"></i> Telegram</a></li>
          </ul>
        </div>
      </div>
      <div class="copyright">
        © 2026 LUCK-BATTLE · Все права защищены
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  border-top: 1px solid var(--glass-border);
  background: rgba(5, 7, 13, 0.6);
  backdrop-filter: blur(20px);
  padding: 60px 0 30px;
  margin-top: 80px;
}
.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 900;
  font-size: 18px;
  margin-bottom: 12px;
}
.logo-icon {
  width: 36px; height: 36px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #fff;
}
.gradient {
  background: linear-gradient(135deg, var(--primary-light), var(--accent-light));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.footer-desc { color: var(--text-muted); font-size: 14px; max-width: 280px; }
h4 { font-size: 13px; font-weight: 800; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text); }
ul { display: flex; flex-direction: column; gap: 10px; }
a { color: var(--text-muted); font-size: 14px; transition: var(--transition); display: inline-flex; align-items: center; gap: 8px; }
a:hover { color: var(--primary-light); }
.copyright {
  border-top: 1px solid var(--glass-border);
  padding-top: 24px;
  text-align: center;
  color: var(--text-dim);
  font-size: 13px;
}
@media (max-width: 768px) {
  .footer-grid { grid-template-columns: 1fr 1fr; gap: 30px; }
}
</style>
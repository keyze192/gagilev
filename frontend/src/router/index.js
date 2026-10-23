import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CaseView from '../views/CaseView.vue'
import ProfileView from '../views/ProfileView.vue'
import UpgradeView from '../views/UpgradeView.vue'
import ContractView from '../views/ContractView.vue'
import NotFoundView from '../views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/case/:id', name: 'case', component: CaseView },
    { path: '/profile', name: 'profile', component: ProfileView },
    { path: '/upgrade', name: 'upgrade', component: UpgradeView },
    { path: '/contract', name: 'contract', component: ContractView },
    { path: '/:pathMatch(.*)*', name: 'notfound', component: NotFoundView },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
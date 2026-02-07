import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '../store/userStore';

// 路由组件懒加载
const Home = () => import('../views/Home.vue');
const Login = () => import('../views/Login.vue');
const Register = () => import('../views/Register.vue');
const DiagnosticTool = () => import('../views/DiagnosticTool.vue');
const History = () => import('../views/History.vue');
const Dashboard = () => import('../views/Dashboard.vue');
const DiagnosisResult = () => import('../views/DiagnosisResult.vue');
const NotFound = () => import('../views/NotFound.vue');

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页 - MediCheck AI' }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录 - MediCheck AI', guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: '注册 - MediCheck AI', guest: true }
  },
  {
    path: '/diagnostic',
    name: 'DiagnosticTool',
    component: DiagnosticTool,
    meta: { title: '诊断工具 - MediCheck AI' }
  },
  {
    path: '/diagnostic/result/:id',
    name: 'DiagnosisResult',
    component: DiagnosisResult,
    meta: { title: '诊断结果 - MediCheck AI', requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: History,
    meta: { title: '诊断历史 - MediCheck AI', requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: '个人仪表盘 - MediCheck AI', requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: '页面未找到 - MediCheck AI' }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  // 页面滚动行为
  scrollBehavior() {
    return { top: 0 };
  }
});

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 页面标题
  document.title = to.meta.title || 'MediCheck AI';
  
  const userStore = useUserStore();
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const isAuthRoute = to.matched.some(record => record.meta.guest);
  
  // 需要认证的路由，但用户未登录，自动跳转到路由页面
  if (requiresAuth && !userStore.isAuthenticated) {
    next('/login');
  } 
  // 访客路由（如登录页），但用户已登录
  else if (isAuthRoute && userStore.isAuthenticated) {
    next('/dashboard');
  } 
  // 其他情况正常导航
  else {
    next();
  }
});

export default router;

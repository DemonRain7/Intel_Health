<template>
  <div class="app-wrapper">
    <header class="bg-blue-600 text-white shadow-md">
      <nav class="container mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center">
          <router-link to="/" class="text-xl font-bold text-white brand-logo">MediCheck AI</router-link>
        </div>
        
        <div class="hidden md:flex space-x-4">
          <router-link to="/" class="nav-link" :class="[$route.path === '/' ? 'nav-link-active' : 'nav-link-inactive']">
            首页
          </router-link>
          <router-link to="/diagnostic" class="nav-link" :class="[$route.path === '/diagnostic' ? 'nav-link-active' : 'nav-link-inactive']">
            诊断工具
          </router-link>
          <router-link v-if="userStore.isAuthenticated" to="/history" class="nav-link" :class="[$route.path === '/history' ? 'nav-link-active' : 'nav-link-inactive']">
            诊断历史
          </router-link>
          <router-link v-if="userStore.isAuthenticated" to="/dashboard" class="nav-link" :class="[$route.path === '/dashboard' ? 'nav-link-active' : 'nav-link-inactive']">
            个人中心
          </router-link>
        </div>
        
        <div class="hidden md:block">
          <template v-if="userStore.isAuthenticated">
            <span class="mr-2">{{ userStore.username }}</span>
            <button @click="logout" class="btn border-2 border-white text-white bg-transparent hover:bg-blue-500">
              退出
            </button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn border-2 border-white text-white bg-transparent hover:bg-blue-500 mr-2">
              登录
            </router-link>
            <router-link to="/register" class="btn btn-primary bg-white text-blue-600 hover:bg-gray-100">
              注册
            </router-link>
          </template>
        </div>
        
        <!-- 移动端菜单按钮 -->
        <div class="md:hidden">
          <button @click="toggleMobileMenu" class="text-white focus:outline-none">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </nav>
      
      <!-- 移动端菜单 -->
      <div v-if="mobileMenuOpen" class="md:hidden bg-blue-600 pb-4 px-4">
        <router-link to="/" class="block py-2 text-white" @click="closeMobileMenu">首页</router-link>
        <router-link to="/diagnostic" class="block py-2 text-white" @click="closeMobileMenu">诊断工具</router-link>
        <router-link v-if="userStore.isAuthenticated" to="/history" class="block py-2 text-white" @click="closeMobileMenu">诊断历史</router-link>
        <router-link v-if="userStore.isAuthenticated" to="/dashboard" class="block py-2 text-white" @click="closeMobileMenu">个人中心</router-link>
        
        <div class="mt-4 pt-4 border-t border-blue-500">
          <template v-if="userStore.isAuthenticated">
            <div class="text-white mb-2">{{ userStore.username }}</div>
            <button @click="logout" class="btn border-2 border-white text-white bg-transparent hover:bg-blue-500 w-full">
              退出
            </button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn border-2 border-white text-white bg-transparent hover:bg-blue-500 w-full block mb-2" @click="closeMobileMenu">
              登录
            </router-link>
            <router-link to="/register" class="btn btn-primary bg-white text-blue-600 hover:bg-gray-100 w-full block" @click="closeMobileMenu">
              注册
            </router-link>
          </template>
        </div>
      </div>
    </header>
    
    <!-- 根据路由动态切换页面组件，并在切换过程中使用名为 fade 的动画，确保旧组件退出后新组件再进入。 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <footer class="bg-gray-800 text-white py-8">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between">
          <div class="mb-6 md:mb-0">
            <h3 class="text-xl font-bold mb-4 text-white brand-logo-footer">MediCheck AI</h3>
            <p class="text-gray-400 max-w-md">
              一款基于AI的医疗诊断工具，帮助用户初步了解可能的健康状况。
              请注意，本工具不能替代专业医生的诊断。
            </p>
          </div>
          
          <div>
            <h4 class="text-lg font-bold text-white">快速链接</h4>
            <ul>
              <li class="mb-2">
                <router-link to="/" class="text-gray-400 hover:text-white">首页</router-link>
              </li>
              <li class="mb-2">
                <router-link to="/diagnostic" class="text-gray-400 hover:text-white">诊断工具</router-link>
              </li>
              <li class="mb-2">
                <router-link to="/" class="text-gray-400 hover:text-white">关于我们</router-link>
              </li>
              <li>
                <router-link to="/"  class="text-gray-400 hover:text-white">隐私政策</router-link>
              </li>
            </ul>
          </div>
        </div>
        
        <div class="mt-8 pt-8 border-t border-gray-700 text-center text-gray-400">
          <p>&copy; {{ new Date().getFullYear() }} <span class="brand-logo-footer">MediCheck AI</span>. 保留所有权利。</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from './store/userStore';

export default {
  name: 'App',
  setup() {
    const mobileMenuOpen = ref(false);
    const userStore = useUserStore();
    const router = useRouter();
    
    // 切换移动菜单显示状态
    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value;
    };
    
    // 关闭移动菜单
    const closeMobileMenu = () => {
      mobileMenuOpen.value = false;
    };
    
    // 退出登录
    const logout = () => {
      userStore.logout();
      closeMobileMenu();
      router.push('/');
    };
    
    // 组件挂载时初始化用户认证状态
    onMounted(() => {
      userStore.initAuth();
    });
    
    return {
      mobileMenuOpen,
      userStore,
      toggleMobileMenu,
      closeMobileMenu,
      logout
    };
  }
};
</script>

<style>
.app-wrapper {
  margin: 0;
  padding: 0;
}

.brand-logo {
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
  position: relative;
  font-size: 1.5rem;
}

.brand-logo::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #ffffff;
  opacity: 0.7;
}

.brand-logo-footer {
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
  position: relative;
  display: inline-block;
}

.brand-logo-footer::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #ffffff;
  opacity: 0.7;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

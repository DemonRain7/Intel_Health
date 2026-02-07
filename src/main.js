import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import naive from 'naive-ui'
import './assets/styles.css'; // 使用新的CSS入口文件

// 创建Pinia状态管理实例
const pinia = createPinia();

// 创建Vue应用实例
const app = createApp(App);

// 注册全局功能
app.use(pinia);
app.use(router);
app.use(naive);

// 挂载应用
app.mount('#app');
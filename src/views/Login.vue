<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 class="text-center text-3xl font-extrabold text-gray-900">
        登录您的账户
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        或
        <router-link to="/register" class="font-medium text-blue-600 hover:text-blue-500">
          注册新账户
        </router-link>
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              邮箱
            </label>
            <div class="mt-1">
              <input 
                id="email" 
                name="email" 
                type="email" 
                required
                v-model="form.email"
                class="form-input" 
                :class="{'border-red-500': errors.email}"
              />
              <p v-if="errors.email" class="error-text">{{ errors.email }}</p>
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              密码
            </label>
            <div class="mt-1">
              <input 
                id="password" 
                name="password" 
                type="password" 
                required
                v-model="form.password"
                class="form-input"
                :class="{'border-red-500': errors.password}"
              />
              <p v-if="errors.password" class="error-text">{{ errors.password }}</p>
            </div>
          </div>

          <div>
            <button 
              type="submit" 
              class="w-full btn btn-primary"
              :disabled="loading"
            >
              <span v-if="loading" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                正在登录...
              </span>
              <span v-else>登录</span>
            </button>
          </div>
          
          <div v-if="loginError" class="p-4 bg-red-50 border border-red-200 rounded-md">
            <p class="text-sm text-red-600">{{ loginError }}</p>
          </div>
        </form>

        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-gray-500">
                或者使用
              </span>
            </div>
          </div>

          <div class="mt-6 grid grid-cols-2 gap-3">
            <div>
              <a href="#" class="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm-2.917 16.083c-2.258 0-4.083-1.825-4.083-4.083s1.825-4.083 4.083-4.083c1.103 0 2.024.402 2.735 1.067l-1.107 1.068c-.304-.292-.834-.63-1.628-.63-1.394 0-2.531 1.155-2.531 2.579 0 1.424 1.138 2.579 2.531 2.579 1.616 0 2.224-1.162 2.316-1.762h-2.316v-1.4h3.855c.036.204.064.408.064.677.001 2.332-1.563 3.988-3.919 3.988zm9.917-3.5h-1.75v1.75h-1.167v-1.75h-1.75v-1.166h1.75v-1.75h1.167v1.75h1.75v1.166z"/>
                </svg>
              </a>
            </div>

            <div>
              <a href="#" class="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm-2.994 16.5h-2.506v-6h2.506v6zm-1.253-7.793c-.8 0-1.447-.647-1.447-1.447s.647-1.442 1.447-1.442c.8 0 1.447.647 1.447 1.447 0 .795-.647 1.442-1.447 1.442zm8.247 7.793h-2.5v-3.658c0-2.506-3-2.321-3 0v3.658h-2.496v-6h2.496v1.47c1.105-2.053 5.5-2.209 5.5 1.971v2.559z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/userStore';

export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter();
    const userStore = useUserStore();
    
    // 表单数据
    const form = reactive({
      email: '',
      password: ''
    });
    
    // 表单错误和状态
    const errors = reactive({
      email: '',
      password: ''
    });
    const loginError = ref('');
    const loading = ref(false);
    
    // 表单验证
    const validateForm = () => {
      let isValid = true;
      
      // 清除之前的错误
      errors.email = '';
      errors.password = '';
      
      if (!form.email) {
        errors.email = '请输入邮箱';
        isValid = false;
      } else {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(form.email)) {
          errors.email = '请输入有效的邮箱地址';
          isValid = false;
        }
      }
      
      if (!form.password) {
        errors.password = '请输入密码';
        isValid = false;
      } else if (form.password.length < 6) {
        errors.password = '密码必须至少6个字符';
        isValid = false;
      }
      
      return isValid;
    };
    
    // 提交表单
    const handleSubmit = async () => {
      if (!validateForm()) return;
      
      loading.value = true;
      loginError.value = '';
      
      try {
        const result = await userStore.login(form);
        
        if (result.success) {
          router.push('/dashboard');
        } else {
          loginError.value = result.message;
        }
      } catch (error) {
        loginError.value = '登录过程中发生错误，请稍后再试';
        console.error('Login error:', error);
      } finally {
        loading.value = false;
      }
    };
    
    return {
      form,
      errors,
      loginError,
      loading,
      handleSubmit
    };
  }
};
</script>

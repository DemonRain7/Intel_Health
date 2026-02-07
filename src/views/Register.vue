<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 class="text-center text-3xl font-extrabold text-gray-900">
        创建新账户
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        或
        <router-link to="/login" class="font-medium text-blue-600 hover:text-blue-500">
          登录现有账户
        </router-link>
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">
              用户名
            </label>
            <div class="mt-1">
              <input 
                id="username" 
                name="username" 
                type="text" 
                autocomplete="username"
                required
                v-model="form.username"
                class="form-input"
                :class="{'border-red-500': errors.username}"
              />
              <p v-if="errors.username" class="error-text">{{ errors.username }}</p>
            </div>
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              电子邮箱
            </label>
            <div class="mt-1">
              <input 
                id="email" 
                name="email" 
                type="email" 
                autocomplete="email"
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
                autocomplete="new-password"
                required
                v-model="form.password"
                class="form-input"
                :class="{'border-red-500': errors.password}"
              />
              <p v-if="errors.password" class="error-text">{{ errors.password }}</p>
            </div>
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
              确认密码
            </label>
            <div class="mt-1">
              <input 
                id="confirmPassword" 
                name="confirmPassword" 
                type="password" 
                autocomplete="new-password"
                required
                v-model="form.confirmPassword"
                class="form-input"
                :class="{'border-red-500': errors.confirmPassword}"
              />
              <p v-if="errors.confirmPassword" class="error-text">{{ errors.confirmPassword }}</p>
            </div>
          </div>

          <div class="flex items-center">
            <input 
              id="terms" 
              name="terms" 
              type="checkbox" 
              required
              v-model="form.terms"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              :class="{'border-red-500': errors.terms}"
            />
            <label for="terms" class="ml-2 block text-sm text-gray-900">
              我已阅读并同意<a href="#" class="text-blue-600 hover:text-blue-500">服务条款</a>和<a href="#" class="text-blue-600 hover:text-blue-500">隐私政策</a>
            </label>
          </div>
          <p v-if="errors.terms" class="error-text">{{ errors.terms }}</p>

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
                正在注册...
              </span>
              <span v-else>注册</span>
            </button>
          </div>
          
          <div v-if="registerError" class="p-4 bg-red-50 border border-red-200 rounded-md">
            <p class="text-sm text-red-600">{{ registerError }}</p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/userStore';

export default {
  name: 'RegisterPage',
  setup() {
    const router = useRouter();
    const userStore = useUserStore();
    
    // 表单数据
    const form = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      terms: false
    });
    
    // 表单错误和状态
    const errors = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      terms: ''
    });
    const registerError = ref('');
    const loading = ref(false);
    
    // 验证表单
    const validateForm = () => {
      let isValid = true;
      
      // 清除之前的错误
      Object.keys(errors).forEach(key => {
        errors[key] = '';
      });
      
      // 用户名验证
      if (!form.username) {
        errors.username = '请输入用户名';
        isValid = false;
      } else if (form.username.length < 3) {
        errors.username = '用户名必须至少3个字符';
        isValid = false;
      }
      
      // 邮箱验证
      if (!form.email) {
        errors.email = '请输入电子邮箱';
        isValid = false;
      } else {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(form.email)) {
          errors.email = '请输入有效的电子邮箱地址';
          isValid = false;
        }
      }
      
      // 密码验证
      if (!form.password) {
        errors.password = '请输入密码';
        isValid = false;
      } else if (form.password.length < 6) {
        errors.password = '密码必须至少6个字符';
        isValid = false;
      }
      
      // 确认密码验证
      if (!form.confirmPassword) {
        errors.confirmPassword = '请确认密码';
        isValid = false;
      } else if (form.password !== form.confirmPassword) {
        errors.confirmPassword = '两次输入的密码不一致';
        isValid = false;
      }
      
      // 条款验证
      if (!form.terms) {
        errors.terms = '您必须同意服务条款和隐私政策';
        isValid = false;
      }
      
      return isValid;
    };
    
    // 提交表单
    const handleSubmit = async () => {
      if (!validateForm()) return;
      
      loading.value = true;
      registerError.value = '';
      
      try {
        const userData = {
          username: form.username,
          email: form.email,
          password: form.password
        };
        
        const result = await userStore.register(userData);
        
        if (result.success) {
          router.push('/dashboard');
        } else {
          registerError.value = result.message;
        }
      } catch (error) {
        registerError.value = '注册过程中发生错误，请稍后再试';
        console.error('Registration error:', error);
      } finally {
        loading.value = false;
      }
    };
    
    return {
      form,
      errors,
      registerError,
      loading,
      handleSubmit
    };
  }
};
</script>
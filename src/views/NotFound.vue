<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <h1 class="text-9xl font-bold text-blue-600">404</h1>
        <h2 class="text-3xl font-extrabold text-gray-900 mt-4">
          页面未找到
        </h2>
        <p class="mt-4 text-lg text-gray-600">
          很抱歉，您请求的页面不存在或已被移除。
        </p>
        
        <div class="mt-8">
          <router-link to="/" class="btn btn-primary">
            返回首页
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundPage'
};
</script>
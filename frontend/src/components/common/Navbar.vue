<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push({ name: 'Login' })
}
</script>

<template>
  <nav class="bg-white shadow-sm">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <div class="flex items-center space-x-4">
          <router-link to="/" class="text-xl font-bold text-blue-600">
            Carry Trade Helper
          </router-link>
          <div class="flex space-x-2">
            <router-link 
              to="/dashboard" 
              class="px-3 py-2 rounded hover:bg-gray-100 transition"
              active-class="bg-blue-50 text-blue-600"
            >
              Dashboard
            </router-link>
            <router-link 
              to="/chat" 
              class="px-3 py-2 rounded hover:bg-gray-100 transition"
              active-class="bg-blue-50 text-blue-600"
            >
              AI Chat
            </router-link>
            <router-link 
              to="/settings" 
              class="px-3 py-2 rounded hover:bg-gray-100 transition"
              active-class="bg-blue-50 text-blue-600"
            >
              Settings
            </router-link>
          </div>
        </div>
        
        <div class="flex items-center space-x-4">
          <span class="text-gray-600 text-sm">{{ authStore.user?.email }}</span>
          <button 
            @click="logout" 
            class="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 transition"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>
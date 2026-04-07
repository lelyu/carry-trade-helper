<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full text-center">
      <div v-if="loading" class="space-y-4">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="text-gray-600">Verifying magic link...</p>
      </div>
      
      <div v-else-if="error" class="space-y-4">
        <div class="rounded-md bg-red-50 p-4">
          <p class="text-red-800">{{ error }}</p>
        </div>
        <router-link to="/login" class="text-blue-600 hover:underline">
          Try again
        </router-link>
      </div>
      
      <div v-else class="space-y-4">
        <div class="rounded-md bg-green-50 p-4">
          <p class="text-green-800">Successfully signed in!</p>
        </div>
        <p class="text-gray-600">Redirecting to dashboard...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')

onMounted(async () => {
  const token = route.query.token as string
  
  if (!token) {
    error.value = 'No token provided'
    loading.value = false
    return
  }
  
  const result = await authStore.verifyToken(token)
  
  loading.value = false
  
  if (result.success) {
    setTimeout(() => {
      router.push({ name: 'Dashboard' })
    }, 1000)
  } else {
    error.value = 'Invalid or expired token'
  }
})
</script>
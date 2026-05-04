<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/common/Navbar.vue'
import AppFooter from '@/components/common/AppFooter.vue'

const authStore = useAuthStore()

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await authStore.fetchUser()
  }
})
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50 flex flex-col">
    <Navbar />
    <main class="flex-1 container mx-auto px-4 py-8">
      <router-view />
    </main>
    <AppFooter />
  </div>
</template>
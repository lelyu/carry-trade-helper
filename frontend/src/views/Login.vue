<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const email = ref('')
const loading = ref(false)
const message = ref('')
const isError = ref(false)

const messageClass = computed(() => ({
  'bg-green-50 text-green-800': !isError.value,
  'bg-red-50 text-red-800': isError.value
}))

const handleSubmit = async () => {
  if (!email.value) return
  
  loading.value = true
  message.value = ''
  
  const result = await authStore.login(email.value)
  
  loading.value = false
  
  if (result.success) {
    message.value = 'Magic link sent! Check your email.'
    isError.value = false
  } else {
    message.value = 'Failed to send magic link. Please try again.'
    isError.value = true
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Sign in to Carry Trade Helper
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Enter your email address and we'll send you a magic link
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email-address" class="sr-only">Email address</label>
            <input
              id="email-address"
              v-model="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="appearance-none rounded relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Email address"
            />
          </div>
        </div>

        <div v-if="message" class="rounded-md p-4" :class="messageClass">
          <p class="text-sm">{{ message }}</p>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading || !email"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Sending...' : 'Send Magic Link' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/services/api'
import { cn } from '@/utils/utils'
import type { Session } from '@/types'

const settingsStore = useSettingsStore()
const authStore = useAuthStore()

const availablePairs = [
	'EUR/USD',
	'GBP/USD',
	'USD/JPY',
	'USD/CHF',
	'AUD/USD',
	'USD/CAD',
	'NZD/USD',
	'USD/CNY',
	'USD/HKD',
]

const selectedPairs = ref<string[]>([])
const localFrequency = ref('daily')
const isActive = ref(true)
const thresholds = ref({
	rate_change: 0.5,
	spread: 10,
})

const message = ref('')
const isError = ref(false)
const sessions = ref<Session[]>([])
const sessionsLoading = ref(false)

const messageClass = computed(() => {
	const classes: Record<string, boolean> = {
		['bg-green-50']: !isError.value,
		['text-green-800']: !isError.value,
		['bg-red-50']: isError.value,
		['text-red-800']: isError.value,
	}
	return cn(...Object.keys(classes).filter(key => classes[key]))
})

onMounted(async () => {
	await settingsStore.fetchPreferences()

	if (settingsStore.preferences) {
		selectedPairs.value = settingsStore.preferences.currency_pairs
		localFrequency.value = settingsStore.preferences.email_frequency
		isActive.value = settingsStore.preferences.is_active
		if (settingsStore.preferences.alert_thresholds) {
			thresholds.value = {
				rate_change:
					settingsStore.preferences.alert_thresholds
						.rate_change || 0.5,
				spread:
					settingsStore.preferences.alert_thresholds.spread || 10,
			}
		}
	}

	await fetchSessions()
})

const fetchSessions = async () => {
	sessionsLoading.value = true
	try {
		const response = await authApi.getSessions()
		sessions.value = response.sessions
	} catch (e) {
		console.error('Failed to fetch sessions:', e)
	} finally {
		sessionsLoading.value = false
	}
}

const formatDate = (dateStr: string | null) => {
	if (!dateStr) return 'Never'
	const date = new Date(dateStr)
	return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

const formatDeviceInfo = (deviceInfo: Record<string, unknown> | null) => {
	if (!deviceInfo) return 'Unknown device'
	const platform = deviceInfo.platform || 'Unknown platform'
	const browser = deviceInfo.user_agent ? 
		deviceInfo.user_agent.toString().split(' ')[0] : 'Unknown browser'
	return `${browser} on ${platform}`
}

const revokeSession = async (sessionId: string) => {
	try {
		await authApi.revokeSession(sessionId)
		await fetchSessions()
	} catch (e) {
		console.error('Failed to revoke session:', e)
	}
}

const logoutAllSessions = async () => {
	if (!confirm('Are you sure you want to log out all other sessions?')) return
	try {
		await authStore.logoutAll()
		await fetchSessions()
	} catch (e) {
		console.error('Failed to logout all sessions:', e)
	}
}

const saveEmailPreferences = async () => {
		const result = await settingsStore.updatePreferences({
			email_frequency: localFrequency.value as 'hourly' | 'daily' | 'weekly',
			is_active: isActive.value,
		})

		showMessage(result.success)
	}

const saveCurrencyPairs = async () => {
	const result = await settingsStore.updatePreferences({
		currency_pairs: selectedPairs.value,
	})

	showMessage(result.success)
}

const saveThresholds = async () => {
	const result = await settingsStore.updatePreferences({
		alert_thresholds: thresholds.value,
	})

	showMessage(result.success)
}

const showMessage = (success: boolean) => {
	message.value = success
		? 'Settings saved successfully!'
		: 'Failed to save settings'
	isError.value = !success

	setTimeout(() => {
		message.value = ''
	}, 3000)
}
</script>

<template>
	<div class="max-w-2xl mx-auto">
		<h1 class="text-3xl font-bold text-gray-900 mb-6">Account Settings</h1>

		<div class="bg-white rounded-lg shadow-md p-6 mb-6">
			<h2 class="text-xl font-semibold mb-4">Email Preferences</h2>

			<div class="mb-4">
				<label class="block text-sm font-medium text-gray-700 mb-2"
					>Email Frequency</label
				>
				<select
					v-model="localFrequency"
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
					<option value="hourly">Hourly Updates</option>
					<option value="daily">Daily Summary</option>
					<option value="weekly">Weekly Digest</option>
				</select>
			</div>

			<div class="mb-4">
				<label class="flex items-center">
					<input
						type="checkbox"
						v-model="isActive"
						class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300" />
					<span class="ml-2 text-sm text-gray-700"
						>Receive email notifications</span
					>
				</label>
			</div>

			<button
				@click="saveEmailPreferences"
				:disabled="settingsStore.loading"
				class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50">
				{{ settingsStore.loading ? 'Saving...' : 'Save Changes' }}
			</button>
		</div>

		<div class="bg-white rounded-lg shadow-md p-6 mb-6">
			<h2 class="text-xl font-semibold mb-4">Currency Pairs</h2>
			<p class="text-gray-600 mb-4">
				Select the currency pairs you want to track:
			</p>

			<div class="grid grid-cols-2 gap-2">
				<label
					v-for="pair in availablePairs"
					:key="pair"
					class="flex items-center">
					<input
						type="checkbox"
						:value="pair"
						v-model="selectedPairs"
						class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300" />
					<span class="ml-2 text-sm text-gray-700">{{ pair }}</span>
				</label>
			</div>

			<button
				@click="saveCurrencyPairs"
				:disabled="settingsStore.loading"
				class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50">
				{{
					settingsStore.loading ? 'Saving...' : 'Save Currency Pairs'
				}}
			</button>
		</div>

		<div class="bg-white rounded-lg shadow-md p-6">
			<h2 class="text-xl font-semibold mb-4">Alert Thresholds</h2>
			<p class="text-gray-600 mb-4">
				Set thresholds for rate change alerts:
			</p>

			<div class="space-y-4">
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">
						Rate Change Threshold (%)
					</label>
					<input
						type="number"
						v-model="thresholds.rate_change"
						step="0.1"
						min="0"
						max="100"
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">
						Spread Threshold (pips)
					</label>
					<input
						type="number"
						v-model="thresholds.spread"
						step="1"
						min="0"
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
				</div>
			</div>

			<button
				@click="saveThresholds"
				:disabled="settingsStore.loading"
				class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50">
				{{ settingsStore.loading ? 'Saving...' : 'Save Thresholds' }}
			</button>
		</div>

		<div v-if="message" :class="cn('mt-4 p-4 rounded', messageClass)">
			{{ message }}
		</div>

		<div class="bg-white rounded-lg shadow-md p-6 mt-6">
			<h2 class="text-xl font-semibold mb-4">Active Sessions</h2>
			<p class="text-gray-600 mb-4">
				Manage your active sessions across different devices:
			</p>

			<div v-if="sessionsLoading" class="text-center py-4">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
			</div>

			<div v-else-if="sessions.length === 0" class="text-gray-500 text-center py-4">
				No active sessions
			</div>

			<div v-else class="space-y-3">
				<div
					v-for="session in sessions"
					:key="session.id"
					class="border rounded-lg p-4 flex items-center justify-between">
					<div>
						<div class="font-medium">
							{{ formatDeviceInfo(session.device_info) }}
						</div>
						<div class="text-sm text-gray-500">
							IP: {{ session.ip_address || 'Unknown' }}
						</div>
						<div class="text-sm text-gray-500">
							Last active: {{ formatDate(session.last_used_at) }}
						</div>
						<div class="text-sm text-gray-500">
							Expires: {{ formatDate(session.expires_at) }}
						</div>
					</div>
					<div>
						<span
							v-if="session.is_current"
							class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
							Current
						</span>
						<button
							v-else
							@click="revokeSession(session.id)"
							class="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm hover:bg-red-200">
							Revoke
						</button>
					</div>
				</div>
			</div>

			<button
				@click="logoutAllSessions"
				class="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition">
				Log out all other sessions
			</button>
		</div>
	</div>
</template>
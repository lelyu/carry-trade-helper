<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { cn } from '@/utils/utils.js'

const settingsStore = useSettingsStore()

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
})

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
	</div>
</template>
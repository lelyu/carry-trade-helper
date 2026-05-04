<script setup lang="ts">
</script>

<template>
  <footer class="bg-gray-800 text-gray-300 mt-auto">
    <div class="max-w-7xl mx-auto px-4 py-12">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <h3 class="text-white font-semibold text-lg mb-4">Carry Trade Helper</h3>
          <p class="text-sm text-gray-400 leading-relaxed">
            Real-time exchange rates and interest rates for 40+ currencies. Identify carry trade opportunities with AI-powered analysis.
          </p>
        </div>

        <div>
          <h4 class="text-white font-semibold text-sm mb-4 uppercase tracking-wider">Features</h4>
          <ul class="space-y-2 text-sm">
            <li>Currency Converter</li>
            <li>Interest Rates Lookup</li>
            <li>Carry Trade Analysis</li>
            <li>AI-Powered Trading Signals</li>
          </ul>
        </div>

        <div>
          <h4 class="text-white font-semibold text-sm mb-4 uppercase tracking-wider">Resources</h4>
          <ul class="space-y-2 text-sm">
            <li><router-link to="/" class="hover:text-white transition-colors">Home</router-link></li>
            <li><a href="https://api.frankfurter.dev" target="_blank" rel="noopener noreferrer" class="hover:text-white transition-colors">Exchange Rate Data</a></li>
            <li><a href="https://fred.stlouisfed.org" target="_blank" rel="noopener noreferrer" class="hover:text-white transition-colors">Interest Rate Data</a></li>
          </ul>
        </div>
      </div>

      <div class="border-t border-gray-700 mt-8 pt-8 text-center text-sm text-gray-500">
        <p>&copy; {{ new Date().getFullYear() }} Carry Trade Helper. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>
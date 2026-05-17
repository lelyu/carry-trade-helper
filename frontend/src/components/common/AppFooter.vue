<script setup lang="ts">
</script>

<template>
  <footer class="bg-gray-800 text-gray-300 hidden md:block">
    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <h3 class="text-white font-semibold text-lg mb-3">Carry Trade Helper</h3>
          <p class="text-sm text-gray-400 leading-relaxed">
            Real-time exchange rates and interest rates for carry trade analysis.
          </p>
        </div>
        <div>
          <h4 class="text-white font-semibold text-sm mb-3 uppercase tracking-wider">Data Sources</h4>
          <ul class="space-y-2 text-sm">
            <li><a href="https://api.frankfurter.dev" target="_blank" rel="noopener noreferrer" class="hover:text-white transition-colors">Frankfurter Exchange Rates</a></li>
            <li><a href="https://fred.stlouisfed.org" target="_blank" rel="noopener noreferrer" class="hover:text-white transition-colors">FRED Interest Rates</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-white font-semibold text-sm mb-3 uppercase tracking-wider">Navigation</h4>
          <ul class="space-y-2 text-sm">
            <li><router-link to="/exchange" class="hover:text-white transition-colors">Exchange Rates</router-link></li>
            <li><router-link to="/interest" class="hover:text-white transition-colors">Interest Rates</router-link></li>
          </ul>
        </div>
      </div>
      <div class="border-t border-gray-700 mt-6 pt-6 text-center text-sm text-gray-500">
        <p>&copy; {{ new Date().getFullYear() }} Carry Trade Helper. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>
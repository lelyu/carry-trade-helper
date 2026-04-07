<template>
  <div class="chart-container">
    <h3 class="text-lg font-semibold mb-4">{{ title }}</h3>
    <div ref="chartRef" class="w-full"></div>
  </div>
</template>

<script setup lang="ts">
import * as d3 from 'd3'
import { onMounted, ref, watch } from 'vue'

const props = defineProps<{
  data: Array<{ country: string; rate: number }>
  title: string
}>()

const chartRef = ref<HTMLDivElement>()

const drawChart = () => {
  if (!props.data || props.data.length === 0) return

  const margin = { top: 20, right: 30, bottom: 60, left: 60 }
  const width = 800 - margin.left - margin.right
  const height = 400 - margin.top - margin.bottom

  d3.select(chartRef.value!).selectAll('*').remove()

  const svg = d3.select(chartRef.value!)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scaleBand()
    .domain(props.data.map(d => d.country))
    .range([0, width])
    .padding(0.3)

  const y = d3.scaleLinear()
    .domain([0, d3.max(props.data, d => d.rate)!])
    .range([height, 0])

  svg.append('g')
    .attr('class', 'axis-bottom')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll('text')
    .attr('transform', 'rotate(-45)')
    .style('text-anchor', 'end')

  svg.append('g')
    .attr('class', 'axis-left')
    .call(d3.axisLeft(y).ticks(5))

  svg.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('y', 0 - margin.left + 15)
    .attr('x', 0 - (height / 2))
    .attr('dy', '1em')
    .style('text-anchor', 'middle')
    .style('font-size', '12px')
    .text('Interest Rate (%)')

  const bars = svg.selectAll('.bar')
    .data(props.data)
    .enter()
    .append('rect')
    .attr('class', 'bar')
    .attr('x', d => x(d.country)!)
    .attr('y', height)
    .attr('width', x.bandwidth())
    .attr('height', 0)
    .attr('fill', '#3b82f6')
    .attr('rx', 4)

  bars.transition()
    .duration(800)
    .attr('y', d => y(d.rate))
    .attr('height', d => height - y(d.rate))

  svg.selectAll('.label')
    .data(props.data)
    .enter()
    .append('text')
    .attr('class', 'label')
    .attr('x', d => x(d.country)! + x.bandwidth() / 2)
    .attr('y', d => y(d.rate) -5)
    .attr('text-anchor', 'middle')
    .style('font-size', '11px')
    .style('fill', '#374151')
    .text(d => `${d.rate.toFixed(2)}%`)

  bars.on('mouseover', function(event, d) {
    d3.select(this)
      .transition()
      .duration(200)
      .attr('fill', '#2563eb')
  })
  .on('mouseout', function() {
    d3.select(this)
      .transition()
      .duration(200)
      .attr('fill', '#3b82f6')
  })
}

onMounted(() => {
  drawChart()
})

watch(() => props.data, () => {
  drawChart()
}, { deep: true })
</script>

<style scoped>
.chart-container {
  @apply bg-white rounded-lg shadow-md p-6;
}

:deep(.axis-bottom path),
:deep(.axis-left path),
:deep(.axis-bottom line),
:deep(.axis-left line) {
  stroke: #e5e7eb;
}

:deep(.axis-bottom text),
:deep(.axis-left text) {
  fill: #6b7280;
  font-size: 12px;
}
</style>
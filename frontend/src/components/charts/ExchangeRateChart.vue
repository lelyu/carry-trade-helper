<script setup lang="ts">
import * as d3 from 'd3'
import { onMounted, ref, watch } from 'vue'

const props = defineProps<{
  data: Array<{ date: Date; rate: number }>
  title: string
}>()

const chartRef = ref<HTMLDivElement>()

const drawChart = () => {
  if (!props.data || props.data.length === 0) return

  const margin = { top: 20, right: 30, bottom: 30, left: 40 }
  const width = 800 - margin.left - margin.right
  const height = 400 - margin.top - margin.bottom

  d3.select(chartRef.value!).selectAll('*').remove()

  const svg = d3.select(chartRef.value!)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scaleTime()
    .domain(d3.extent(props.data, d => d.date) as [Date, Date])
    .range([0, width])

  const y = d3.scaleLinear()
    .domain([d3.min(props.data, d => d.rate)!, d3.max(props.data, d => d.rate)!])
    .range([height, 0])

  svg.append('g')
    .attr('class', 'axis-bottom')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(7))

  svg.append('g')
    .attr('class', 'axis-left')
    .call(d3.axisLeft(y))

  svg.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('y', 0 - margin.left)
    .attr('x', 0 - (height / 2))
    .attr('dy', '1em')
    .style('text-anchor', 'middle')
    .style('font-size', '12px')
    .text('Exchange Rate')

  const line = d3.line<{ date: Date; rate: number }>()
    .x(d => x(d.date))
    .y(d => y(d.rate))
    .curve(d3.curveMonotoneX)

  const path = svg.append('path')
    .datum(props.data)
    .attr('fill', 'none')
    .attr('stroke', '#3b82f6')
    .attr('stroke-width', 2)
    .attr('d', line)

  const totalLength = path.node()!.getTotalLength()
  path
    .attr('stroke-dasharray', `${totalLength} ${totalLength}`)
    .attr('stroke-dashoffset', totalLength)
    .transition()
    .duration(1000)
    .attr('stroke-dashoffset', 0)

  const dot = svg.selectAll('.dot')
    .data(props.data)
    .enter()
    .append('circle')
    .attr('cx', d => x(d.date))
    .attr('cy', d => y(d.rate))
    .attr('r', 3)
    .attr('fill', '#3b82f6')
    .attr('opacity', 0)
    .attr('class', 'dot')

  dot.transition()
    .duration(1000)
    .attr('opacity', 1)

  svg.selectAll('.dot')
    .on('mouseover', function(_event: MouseEvent, datum: unknown) {
      const d = datum as { date: Date; rate: number }
      d3.select(this)
        .transition()
        .duration(200)
        .attr('r', 6)
      
      svg.append('text')
        .attr('class', 'tooltip')
        .attr('x', x(d.date))
        .attr('y', y(d.rate) - 10)
        .attr('text-anchor', 'middle')
        .text(`${d.rate.toFixed(4)}`)
        .style('font-size', '12px')
    })
    .on('mouseout', function() {
      d3.select(this)
        .transition()
        .duration(200)
        .attr('r', 3)
      
      svg.selectAll('.tooltip').remove()
    })
}

onMounted(() => {
  drawChart()
})

watch(() => props.data, () => {
  drawChart()
}, { deep: true })
</script>

<template>
  <div class="chart-container">
    <h3 class="text-lg font-semibold mb-4">{{ title }}</h3>
    <div ref="chartRef" class="w-full"></div>
  </div>
</template>

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
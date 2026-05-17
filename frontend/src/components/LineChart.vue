<script setup lang="ts">
import * as d3 from 'd3'
import { onMounted, ref, watch } from 'vue'
import { useTheme } from '@/composables/useTheme'

const props = defineProps<{
  data: Array<{ date: string; rate: number }>
  color?: string
  height?: number
  step?: boolean
}>()

const chartRef = ref<HTMLDivElement>()
const { resolvedTheme } = useTheme()

const isDark = () => resolvedTheme.value === 'dark'

const drawChart = () => {
  if (!props.data || props.data.length === 0 || !chartRef.value) return

  const containerWidth = chartRef.value.clientWidth
  if (containerWidth === 0) return

  const margin = { top: 10, right: 15, bottom: 25, left: 50 }
  const width = containerWidth - margin.left - margin.right
  const height = (props.height || 250) - margin.top - margin.bottom
  const color = props.color || '#3b82f6'
  const dark = isDark()
  const textColor = dark ? '#9ca3af' : '#6b7280'
  const gridColor = dark ? '#374151' : '#f3f4f6'
  const domainColor = dark ? '#4b5563' : '#e5e7eb'
  const labelColor = dark ? '#e5e7eb' : '#111827'

  d3.select(chartRef.value).selectAll('*').remove()

  const svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const parseDate = d3.timeParse('%Y-%m-%d')
  const parsedData = props.data
    .map(d => ({ ...d, parsedDate: parseDate(d.date)! }))
    .filter(d => d.parsedDate !== null)
    .sort((a, b) => a.parsedDate.getTime() - b.parsedDate.getTime())

  if (parsedData.length === 0) return

  const x = d3.scaleTime()
    .domain(d3.extent(parsedData, d => d.parsedDate) as [Date, Date])
    .range([0, width])

  const y = d3.scaleLinear()
    .domain([
      d3.min(parsedData, d => d.rate)! * 0.999,
      d3.max(parsedData, d => d.rate)! * 1.001,
    ])
    .range([height, 0])

  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(5).tickSize(0).tickPadding(8))
    .selectAll('text')
    .style('font-size', '11px')
    .style('fill', textColor)

  svg.append('g')
    .call(d3.axisLeft(y).ticks(5).tickSize(-width).tickFormat(d => props.step ? d3.format('.2f')(d) : d3.format('.4f')(d)))
    .selectAll('text')
    .style('font-size', '11px')
    .style('fill', textColor)

  svg.selectAll('.domain').attr('stroke', domainColor)
  svg.selectAll('.tick line').attr('stroke', gridColor)

  const line = d3.line<typeof parsedData[0]>()
    .x(d => x(d.parsedDate))
    .y(d => y(d.rate))
    .curve(props.step ? d3.curveStepAfter : d3.curveMonotoneX)

  const area = d3.area<typeof parsedData[0]>()
    .x(d => x(d.parsedDate))
    .y0(height)
    .y1(d => y(d.rate))
    .curve(props.step ? d3.curveStepAfter : d3.curveMonotoneX)

  const gradient = svg.append('defs')
    .append('linearGradient')
    .attr('id', 'area-gradient')
    .attr('x1', '0%').attr('y1', '0%')
    .attr('x2', '0%').attr('y2', '100%')

  gradient.append('stop').attr('offset', '0%').attr('stop-color', color).attr('stop-opacity', 0.2)
  gradient.append('stop').attr('offset', '100%').attr('stop-color', color).attr('stop-opacity', 0)

  svg.append('path')
    .datum(parsedData)
    .attr('fill', 'url(#area-gradient)')
    .attr('d', area)

  const path = svg.append('path')
    .datum(parsedData)
    .attr('fill', 'none')
    .attr('stroke', color)
    .attr('stroke-width', 2)
    .attr('d', line)

  const totalLength = path.node()?.getTotalLength() || 0
  path
    .attr('stroke-dasharray', `${totalLength} ${totalLength}`)
    .attr('stroke-dashoffset', totalLength)
    .transition()
    .duration(800)
    .attr('stroke-dashoffset', 0)

  const focus = svg.append('g').style('display', 'none')
  focus.append('circle').attr('r', 4).attr('fill', color)
  focus.append('line').attr('class', 'focus-line').attr('stroke', dark ? '#6b7280' : '#9ca3af').attr('stroke-dasharray', '3,3').attr('y1', 0).attr('y2', height)
  focus.append('text').attr('class', 'focus-label').attr('dy', '-10').attr('text-anchor', 'middle').style('font-size', '12px').style('font-weight', '600').style('fill', labelColor)

  const overlay = svg.append('rect')
    .attr('width', width)
    .attr('height', height)
    .style('fill', 'none')
    .style('pointer-events', 'all')

  const bisect = d3.bisector<typeof parsedData[0], Date>((d) => d.parsedDate).left

  overlay
    .on('mouseover', () => focus.style('display', null))
    .on('mouseout', () => focus.style('display', 'none'))
    .on('mousemove', (event: MouseEvent) => {
      const [mx] = d3.pointer(event)
      const x0 = x.invert(mx)
      const i = bisect(parsedData, x0, 1)
      const d0 = parsedData[i - 1]
      const d1 = parsedData[i]
      if (!d0 || !d1) return
      const d = x0.getTime() - d0.parsedDate.getTime() > d1.parsedDate.getTime() - x0.getTime() ? d1 : d0
      focus.select('circle').attr('cx', x(d.parsedDate)).attr('cy', y(d.rate))
      focus.select('.focus-line').attr('x1', x(d.parsedDate)).attr('x2', x(d.parsedDate))
      focus.select('.focus-label').attr('x', x(d.parsedDate)).attr('y', y(d.rate)).text(d.rate.toFixed(4))
    })
}

onMounted(() => {
  drawChart()
  const observer = new ResizeObserver(() => drawChart())
  if (chartRef.value) observer.observe(chartRef.value)
})

watch(() => props.data, () => drawChart(), { deep: true })
watch(() => props.color, () => drawChart())
watch(resolvedTheme, () => drawChart())
</script>

<template>
  <div ref="chartRef" class="w-full" />
</template>
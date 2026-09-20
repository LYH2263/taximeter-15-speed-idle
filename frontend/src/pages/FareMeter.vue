<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const distance_km = ref(8)
const slow_min = ref(3)
const duration_min = ref(40)
const night = ref(false)
// slow = 直接低速分钟（改造前口径）；duration = 行驶时长按阈值时速折算
const mode = ref('slow')
const threshold = ref(null)
const out = ref(null)
const err = ref('')
onMounted(async () => {
  const s = await getJSON('/api/settings')
  threshold.value = s.slow_speed_threshold
})
const run = async () => {
  err.value = ''
  // 两种口径只提交其一，避免被后端拒绝。
  const body = { distance_km: distance_km.value, night: night.value, persist: true }
  if (mode.value === 'duration') body.duration_min = duration_min.value
  else body.slow_min = slow_min.value
  try {
    out.value = await postJSON('/api/fare', body)
    threshold.value = out.value.slow_speed_threshold
  } catch (e) {
    out.value = null
    err.value = String(e.message || e)
  }
}
</script>
<template>
  <div class="page"><h1>打表试算</h1>
    <div class="panel">
      <label>公里 <input type="number" min="0" v-model.number="distance_km" /></label>
      <label><input type="radio" value="slow" v-model="mode" /> 直接低速分钟</label>
      <label v-if="mode === 'slow'">低速分钟 <input type="number" min="0" v-model.number="slow_min" /></label>
      <label><input type="radio" value="duration" v-model="mode" /> 按时长折算</label>
      <label v-if="mode === 'duration'">行驶时长(分钟) <input type="number" min="0" v-model.number="duration_min" /></label>
      <label v-if="mode === 'duration'" class="hint">阈值时速 {{ threshold }} km/h，计入分钟 = max(0, 时长 − 公里 ÷ 阈值 × 60)</label>
      <label><input type="checkbox" v-model="night" /> 夜间</label>
      <button @click="run">计算</button>
    </div>
    <p v-if="err" class="err">{{ err }}</p>
    <div v-if="out" class="panel">
      <p class="hero-num">应付 ¥{{ out.total }}</p>
      <p>阈值时速 {{ out.slow_speed_threshold }} km/h · 计入低速分钟 {{ out.slow_min }} 分钟</p>
      <p>起步 {{ out.start }} · 里程 {{ out.mileage }} · 低速费 {{ out.slow_fee }}</p>
    </div>
  </div>
</template>

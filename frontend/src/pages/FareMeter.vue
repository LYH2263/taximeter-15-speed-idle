<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const distance_km = ref(8)
const slow_min = ref(3)
const duration_min = ref(20)
const night = ref(false)
// mode=direct 直填低速分钟（改造前行为）；mode=duration 按行驶时长折算
const mode = ref('direct')
const threshold = ref(null)
const out = ref(null)
const err = ref('')

const loadSettings = async () => {
  const s = await getJSON('/api/settings')
  threshold.value = Number(s.slow_threshold_kmh)
}
onMounted(loadSettings)

const buildBody = (persist) => {
  const b = { distance_km: distance_km.value, night: night.value, persist }
  if (mode.value === 'duration') b.duration_min = duration_min.value
  else b.slow_min = slow_min.value
  return b
}
// 只读试算：不写记录；改阈值后重新试算计入分钟随之变化
const preview = async () => {
  err.value = ''
  try { out.value = await postJSON('/api/fare', buildBody(false)) }
  catch (e) { err.value = String(e.message || e) }
}
// 正式提交：写入一条计费记录
const submit = async () => {
  err.value = ''
  try { out.value = await postJSON('/api/fare', buildBody(true)) }
  catch (e) { err.value = String(e.message || e) }
}
</script>
<template>
  <div class="page"><h1>打表试算</h1>
    <div class="panel">
      <label>公里 <input type="number" min="0" v-model.number="distance_km" /></label>
      <label>模式
        <select v-model="mode">
          <option value="direct">直填低速分钟</option>
          <option value="duration">按时长折算</option>
        </select>
      </label>
      <label v-if="mode === 'direct'">低速分钟 <input type="number" min="0" v-model.number="slow_min" /></label>
      <template v-else>
        <label>行驶时长（分钟） <input type="number" min="0" v-model.number="duration_min" /></label>
        <p class="hint">阈值时速 {{ threshold }} km/h：计入低速分钟 = max(0, 时长 − 公里 ÷ 阈值 × 60)</p>
      </template>
      <label><input type="checkbox" v-model="night" /> 夜间</label>
      <span class="btn-row">
        <button @click="preview">只读试算</button>
        <button class="primary" @click="submit">提交计费</button>
      </span>
    </div>
    <p v-if="err" class="err">{{ err }}</p>
    <div v-if="out" class="panel result">
      <p class="hero-num">应付 ¥{{ out.total }}</p>
      <p>阈值时速：{{ out.threshold_kmh ?? '—' }} km/h</p>
      <p>计入低速分钟：{{ out.slow_min }} 分钟</p>
      <p>低速费：¥{{ out.slow_fee }}</p>
      <p>起步 {{ out.start }} · 里程 {{ out.mileage }}<template v-if="out.run_id"> · 记录 #{{ out.run_id }}</template></p>
    </div>
  </div>
</template>
<style scoped>
.hint { color: var(--muted); font-size: 0.85rem; margin: 0.3rem 0; }
.err { color: #ff7a5c; }
.btn-row { display: inline-flex; gap: 0.5rem; margin-left: 0.5rem; }
button.primary { font-weight: 700; }
.result p { margin: 0.25rem 0; }
</style>

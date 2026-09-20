<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const s = ref({})
const thresholdDraft = ref(null)
const savedAt = ref('')
const err = ref('')
onMounted(load)
async function load() {
  s.value = await getJSON('/api/settings')
  // 草稿以服务端原值为准
  thresholdDraft.value = Number(s.value.slow_threshold_kmh)
  err.value = ''
}
async function save() {
  err.value = ''
  savedAt.value = ''
  // 必须为正数；先在前端拦一道
  if (!(Number(thresholdDraft.value) > 0)) {
    err.value = '阈值时速必须为正数，已保留原值'
    thresholdDraft.value = Number(s.value.slow_threshold_kmh)
    return
  }
  try {
    s.value = await postJSON('/api/settings', { slow_threshold_kmh: Number(thresholdDraft.value) })
    thresholdDraft.value = Number(s.value.slow_threshold_kmh)
    savedAt.value = '已保存'
  } catch (e) {
    // 保存失败不得改原值：草稿回退到服务端值
    err.value = '保存失败（阈值时速必须为正），已保留原值'
    thresholdDraft.value = Number(s.value.slow_threshold_kmh)
  }
}
</script>
<template>
  <div class="page"><h1>设置</h1>
    <div class="panel">
      <label>低速阈值时速（km/h，必须为正数）
        <input type="number" min="0" step="0.1" v-model.number="thresholdDraft" />
      </label>
      <button @click="save">保存</button>
      <span v-if="err" class="err">{{ err }}</span>
      <span v-else-if="savedAt" class="ok">{{ savedAt }}</span>
    </div>
    <pre>{{ s }}</pre>
  </div>
</template>
<style scoped>
.err { color: #ff7a5c; margin-left: 0.5rem; }
.ok { color: #8fd14f; margin-left: 0.5rem; }
</style>

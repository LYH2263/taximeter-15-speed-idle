<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const s = ref({})
const threshold = ref('')   // 输入框草稿
const saved = ref(null)     // 服务端已保存的值，保存失败时拿它回退
const msg = ref('')
const err = ref('')
onMounted(async () => {
  s.value = await getJSON('/api/settings')
  threshold.value = String(s.value.slow_speed_threshold)
  saved.value = s.value.slow_speed_threshold
})
const save = async () => {
  msg.value = ''
  err.value = ''
  try {
    const next = await postJSON('/api/settings', { slow_speed_threshold: Number(threshold.value) })
    s.value = next
    saved.value = next.slow_speed_threshold
    threshold.value = String(next.slow_speed_threshold)
    msg.value = '已保存'
  } catch (e) {
    // 保存失败不得改原值：草稿回退到服务端旧值并提示。
    threshold.value = String(saved.value)
    err.value = '保存失败：阈值时速必须为正数，原值未改动'
  }
}
</script>
<template>
  <div class="page"><h1>设置</h1>
    <div class="panel">
      <label>阈值时速(km/h)，必须为正
        <input type="number" min="0" step="0.1" v-model="threshold" />
      </label>
      <button @click="save">保存</button>
      <span v-if="msg" class="ok">{{ msg }}</span>
      <span v-if="err" class="err">{{ err }}</span>
    </div>
    <pre>{{ s }}</pre>
  </div>
</template>

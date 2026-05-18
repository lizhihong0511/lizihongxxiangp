<template>
  <div class="page">
    <h2 class="page-title">题库管理</h2>

    <!-- 上传区 -->
    <div class="upload-area" @drop.prevent="onDrop" @dragover.prevent
         :class="{ 'upload--dragover': dragging }"
         @dragenter="dragging = true" @dragleave="dragging = false">
      <div class="upload-icon">📁</div>
      <p class="upload-text">拖拽 Word 或 PDF 文件到此处</p>
      <p class="upload-hint">支持 .docx 和 .pdf 格式</p>
      <input ref="fileInput" type="file" accept=".docx,.pdf"
             @change="onFileSelect" style="display:none" />
      <button class="upload-btn" @click="$refs.fileInput.click()">选择文件</button>
    </div>

    <!-- 解析中 -->
    <div v-if="parsing" class="loading-bar">
      <div class="spinner"></div>
      <span>AI 正在解析文档，请稍候...</span>
    </div>

    <!-- 预览列表 -->
    <div v-if="questions.length" class="preview">
      <div class="preview-header">
        <h3>AI 识别结果（{{ questions.length }} 道题）</h3>
        <div class="preview-actions">
          <select v-model="importSubjectId" class="form-select">
            <option value="">选择科目（可选）</option>
            <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
          <button class="import-btn" @click="doImport" :disabled="importing">
            {{ importing ? '导入中...' : '✅ 确认导入' }}
          </button>
        </div>
      </div>

      <div v-for="(q, i) in questions" :key="i" class="question-card">
        <div class="q-head">
          <span class="q-num">{{ i + 1 }}</span>
          <span class="q-tag" :class="q.difficulty">{{ diffLabel(q.difficulty) }}</span>
          <span class="q-tag type">{{ typeLabel(q.type) }}</span>
          <button class="q-del" @click="questions.splice(i, 1)">✕</button>
        </div>
        <div class="q-text">{{ q.question_text }}</div>
        <div v-if="q.options?.length" class="q-options">
          <div v-for="opt in q.options" :key="opt.label" class="q-opt">
            <span class="opt-lbl">{{ opt.label }}.</span>
            <span>{{ opt.text }}</span>
          </div>
        </div>
        <div class="q-answer">答案：<strong>{{ q.correct_answer }}</strong></div>
        <div v-if="q.explanation" class="q-explain">{{ q.explanation }}</div>
      </div>
    </div>

    <!-- 结果提示 -->
    <div v-if="resultMsg" class="result-msg" :class="resultOk ? 'msg-ok' : 'msg-err'">
      {{ resultMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { uploadAndParse, importQuestions } from '../api/admin.js'
import { getUserId } from '../api/exam.js'
import { fetchExamTypes, fetchSubjects } from '../api/exam.js'

const fileInput = ref(null)
const dragging = ref(false)
const parsing = ref(false)
const importing = ref(false)
const questions = ref([])
const resultMsg = ref('')
const resultOk = ref(false)
const subjects = ref([])
const importSubjectId = ref('')
const userId = getUserId()

onMounted(async () => {
  try {
    const types = await fetchExamTypes()
    if (types.length) subjects.value = await fetchSubjects(types[0].id)
  } catch {}
})

async function onFileSelect(e) {
  const file = e.target.files[0]
  if (file) await processFile(file)
}

async function onDrop(e) {
  dragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) await processFile(file)
}

async function processFile(file) {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!['docx', 'pdf'].includes(ext)) {
    resultMsg.value = '仅支持 .docx 和 .pdf 文件'
    resultOk.value = false
    return
  }

  parsing.value = true
  questions.value = []
  resultMsg.value = ''
  try {
    const data = await uploadAndParse(file, userId)
    questions.value = data.questions || []
    resultMsg.value = `成功识别 ${questions.value.length} 道题`
    resultOk.value = true
  } catch (e) {
    resultMsg.value = '解析失败: ' + (e.response?.data?.detail || e.message)
    resultOk.value = false
  } finally {
    parsing.value = false
  }
}

async function doImport() {
  if (!questions.value.length) return
  importing.value = true
  try {
    await importQuestions(questions.value, userId, importSubjectId.value || undefined, undefined)
    resultMsg.value = `✅ 成功导入 ${questions.value.length} 道题！`
    resultOk.value = true
    questions.value = []
  } catch (e) {
    resultMsg.value = '导入失败: ' + (e.response?.data?.detail || e.message)
    resultOk.value = false
  } finally {
    importing.value = false
  }
}

function diffLabel(d) { return { easy: '简单', medium: '中等', hard: '困难' }[d] || d }
function typeLabel(t) {
  return {
    single_choice: '单选', multi_choice: '多选',
    true_false: '判断', fill_blank: '填空',
  }[t] || t
}
</script>

<style scoped>
.page { padding: 20px 16px; }
.page-title { font-size: 20px; margin-bottom: 16px; }

.upload-area {
  border: 2px dashed var(--border); border-radius: 14px;
  padding: 40px 20px; text-align: center; cursor: pointer;
  transition: all 0.2s; background: var(--card);
}
.upload--dragover { border-color: var(--primary); background: var(--primary-light); }
.upload-icon { font-size: 48px; margin-bottom: 12px; }
.upload-text { font-size: 16px; color: var(--text); margin-bottom: 4px; }
.upload-hint { font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; }
.upload-btn {
  padding: 10px 24px; background: var(--primary); color: #fff;
  border: none; border-radius: 8px; font-size: 15px; cursor: pointer;
}

.loading-bar { display: flex; align-items: center; gap: 10px; margin: 20px 0; justify-content: center; color: var(--text-secondary); }
.spinner {
  width: 18px; height: 18px; border: 2px solid var(--primary);
  border-top-color: transparent; border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.preview { margin-top: 20px; }
.preview-header {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 10px; margin-bottom: 16px;
}
.preview-header h3 { font-size: 16px; }
.preview-actions { display: flex; gap: 8px; align-items: center; }
.form-select {
  font-size: 13px; padding: 8px 10px; border: 1px solid var(--border);
  border-radius: 8px; background: var(--card);
}
.import-btn {
  padding: 10px 18px; background: var(--correct); color: #fff;
  border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer;
}
.import-btn:disabled { opacity: 0.5; }

.question-card {
  background: var(--card); border-radius: 10px; padding: 14px;
  margin-bottom: 10px; border: 1px solid var(--border);
}
.q-head { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.q-num { font-weight: 700; color: var(--primary); font-size: 14px; margin-right: 4px; }
.q-tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; }
.q-tag.easy { background: #dcfce7; color: #16a34a; }
.q-tag.medium { background: #fef3c7; color: #d97706; }
.q-tag.hard { background: #fee2e2; color: #dc2626; }
.q-tag.type { background: #eef2ff; color: var(--primary); }
.q-del { margin-left: auto; background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 16px; }
.q-text { font-size: 14px; line-height: 1.5; margin-bottom: 8px; }
.q-options { margin-bottom: 8px; }
.q-opt { font-size: 13px; padding: 4px 0; }
.opt-lbl { font-weight: 600; }
.q-answer { font-size: 13px; color: var(--correct); margin-bottom: 4px; }
.q-explain { font-size: 13px; color: var(--text-secondary); background: var(--bg); padding: 8px; border-radius: 6px; }

.result-msg { margin-top: 16px; padding: 12px; border-radius: 8px; font-size: 14px; text-align: center; }
.msg-ok { background: #dcfce7; color: var(--correct); }
.msg-err { background: #fee2e2; color: var(--wrong); }
</style>

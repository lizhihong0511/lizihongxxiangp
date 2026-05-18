<template>
  <div class="page">
    <div class="header">
      <h2 class="page-title">AI 问答</h2>
      <select v-model="selectedSubjectId" class="subject-select">
        <option value="">不限科目</option>
        <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
      </select>
    </div>

    <div class="chat-area" ref="chatArea">
      <div v-if="messages.length === 0" class="empty-hint">
        <div class="empty-icon">🎓</div>
        <div>问我任何考证相关问题</div>
        <div class="empty-examples">
          <button v-for="q in quickQuestions" :key="q" class="quick-btn" @click="send(q)">{{ q }}</button>
        </div>
      </div>

      <div v-for="(m, i) in messages" :key="i" :class="['message', m.role]">
        <div class="message-content" v-html="renderMarkdown(m.content)"></div>
        <div v-if="m.role === 'assistant' && i === messages.length - 1" class="qa-actions">
          <button class="btn-sm" @click="startPracticeFromQA">📝 相关练习</button>
        </div>
      </div>

      <div v-if="loading" class="message assistant">
        <div class="typing">AI 思考中<span class="dots">...</span></div>
      </div>
    </div>

    <div class="input-bar">
      <input
        v-model="input"
        class="chat-input"
        placeholder="输入你的问题..."
        @keyup.enter="send(input)"
        :disabled="loading"
      />
      <button class="send-btn" @click="send(input)" :disabled="loading || !input.trim()">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { askQuestion, fetchExamTypes, fetchSubjects } from '../api/exam.js'

const router = useRouter()
const input = ref('')
const messages = ref([])
const loading = ref(false)
const subjects = ref([])
const selectedSubjectId = ref('')
const chatArea = ref(null)

const quickQuestions = [
  '什么是矛盾的普遍性和特殊性？',
  '如何理解剩余价值理论？',
  '新发展理念包含哪些内容？',
]

onMounted(async () => {
  try {
    const types = await fetchExamTypes()
    if (types.length) {
      subjects.value = await fetchSubjects(types[0].id)
    }
  } catch {}
})

async function send(text) {
  const q = text.trim()
  if (!q || loading.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: q })
  loading.value = true

  try {
    const subjectName = subjects.value.find(s => s.id === selectedSubjectId.value)?.name
    const result = await askQuestion(q, subjectName, selectedSubjectId.value || undefined)
    messages.value.push({ role: 'assistant', content: result.answer })
  } catch {
    messages.value.push({ role: 'assistant', content: '抱歉，请求失败，请稍后重试。' })
  } finally {
    loading.value = false
    nextTick(() => scrollBottom())
  }
}

function startPracticeFromQA() {
  if (selectedSubjectId.value) {
    router.push({ path: '/practice', query: { subject_id: selectedSubjectId.value } })
  } else {
    router.push('/bank')
  }
}

function renderMarkdown(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n- (.+)/g, '\n<li>$1</li>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>')
}

function scrollBottom() {
  if (chatArea.value) chatArea.value.scrollTop = chatArea.value.scrollHeight
}
</script>

<style scoped>
.page { display: flex; flex-direction: column; height: 100%; }
.header { padding: 16px 16px 0; display: flex; justify-content: space-between; align-items: center; }
.page-title { font-size: 20px; }
.subject-select {
  font-size: 13px; padding: 6px 10px; border-radius: 8px;
  border: 1px solid var(--border); background: var(--card);
}

.chat-area { flex: 1; overflow-y: auto; padding: 16px; }

.empty-hint { text-align: center; padding: 40px 0; color: var(--text-secondary); }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-examples { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 16px; }
.quick-btn {
  font-size: 13px; padding: 8px 14px; background: var(--primary-light);
  color: var(--primary); border: none; border-radius: 20px; cursor: pointer;
}

.message { margin-bottom: 16px; }
.message.user { text-align: right; }
.message.user .message-content {
  display: inline-block; background: var(--primary); color: #fff;
  padding: 10px 16px; border-radius: 16px 16px 4px 16px; max-width: 85%;
  text-align: left; font-size: 15px;
}
.message.assistant .message-content {
  display: inline-block; background: var(--card); padding: 12px 16px;
  border-radius: 4px 16px 16px 16px; max-width: 90%;
  font-size: 15px; line-height: 1.6;
}

.qa-actions { margin-top: 8px; }
.btn-sm {
  font-size: 12px; padding: 6px 12px; background: var(--primary-light);
  color: var(--primary); border: none; border-radius: 8px; cursor: pointer;
}

.typing { color: var(--text-secondary); font-size: 14px; padding: 8px; }
.dots { animation: blink 1.5s infinite; }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

.input-bar {
  display: flex; gap: 8px; padding: 12px 16px;
  background: var(--card); border-top: 1px solid var(--border);
}
.chat-input {
  flex: 1; padding: 12px 16px; border: 1px solid var(--border);
  border-radius: 24px; font-size: 15px; outline: none;
}
.chat-input:focus { border-color: var(--primary); }
.send-btn {
  padding: 12px 20px; background: var(--primary); color: #fff;
  border: none; border-radius: 24px; font-size: 15px; font-weight: 600;
  cursor: pointer; white-space: nowrap;
}
.send-btn:disabled { opacity: 0.5; }
</style>

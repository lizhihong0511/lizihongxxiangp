<template>
  <div class="page">
    <!-- 未开始：配置 -->
    <div v-if="!session" class="setup">
      <h2 class="page-title">练习</h2>
      <div class="form-group">
        <label>选择科目</label>
        <select v-model="config.subjectId" @change="onSubjectChange" class="form-select">
          <option value="">请选择</option>
          <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>
      <div class="form-group" v-if="chapters.length">
        <label>章节（可选）</label>
        <select v-model="config.chapterId" class="form-select">
          <option value="">全部章节</option>
          <option v-for="c in chapters" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label>难度</label>
        <div class="chip-row">
          <button :class="['chip-sm', config.difficulty === '' && 'active']" @click="config.difficulty = ''">全部</button>
          <button :class="['chip-sm', config.difficulty === 'easy' && 'active']" @click="config.difficulty = 'easy'">简单</button>
          <button :class="['chip-sm', config.difficulty === 'medium' && 'active']" @click="config.difficulty = 'medium'">中等</button>
          <button :class="['chip-sm', config.difficulty === 'hard' && 'active']" @click="config.difficulty = 'hard'">困难</button>
        </div>
      </div>
      <div class="form-group">
        <label>题目数量</label>
        <input type="range" v-model.number="config.count" min="5" max="30" step="5" class="range" />
        <span class="range-val">{{ config.count }} 题</span>
      </div>
      <button class="start-btn" @click="begin" :disabled="!config.subjectId">开始练习</button>
      <button class="ai-btn" @click="beginAi" :disabled="!config.subjectId || generating">
        <span v-if="generating" class="spinner"></span>
        <span>{{ generating ? 'AI 出题中...' : '🤖 AI 智能出题' }}</span>
      </button>
      <p v-if="generating" class="ai-hint">正在根据章节知识点生成题目，请稍候...</p>
    </div>

    <!-- 练习中 -->
    <div v-else-if="session && !finished" class="practice">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <div class="progress-info">
        <span>第 {{ session.current + 1 }} / {{ session.total }} 题</span>
        <span>✅ {{ session.correct }} 正确</span>
      </div>

      <div class="question-area" v-if="currentQ">
        <div class="q-type-tag">{{ typeLabel(currentQ.type) }}</div>
        <div class="q-stem">{{ currentQ.question_text }}</div>

        <!-- 选择题 -->
        <div v-if="currentQ.type !== 'fill_blank'" class="options">
          <button
            v-for="opt in currentQ.options" :key="opt.label"
            :class="['option', {
              'option--selected': selectedAnswer === opt.label,
              'option--correct': feedback && opt.label === feedback.correct_answer,
              'option--wrong': feedback && selectedAnswer === opt.label && !feedback.is_correct,
            }]"
            @click="selectOption(opt.label)"
            :disabled="!!feedback"
          >
            <span class="opt-badge">{{ opt.label }}</span>
            <span>{{ opt.text }}</span>
          </button>
        </div>

        <!-- 填空题 -->
        <div v-else class="fill-input-wrap">
          <input
            v-model="fillAnswer"
            class="fill-input"
            placeholder="请输入答案..."
            :disabled="!!feedback"
            @keyup.enter="submitAnswer(fillAnswer)"
          />
          <button v-if="!feedback" class="submit-btn" @click="submitAnswer(fillAnswer)" :disabled="!fillAnswer.trim()">
            确认
          </button>
        </div>

        <!-- 判断题/单选题 直接提交 -->
        <div v-if="currentQ.type !== 'fill_blank' && selectedAnswer && !feedback" class="confirm-row">
          <button class="submit-btn" @click="submitAnswer(selectedAnswer)">确认提交</button>
        </div>

        <!-- 反馈 -->
        <div v-if="feedback" class="feedback" :class="feedback.is_correct ? 'fb-correct' : 'fb-wrong'">
          <div class="fb-header">
            {{ feedback.is_correct ? '✅ 回答正确！' : '❌ 回答错误' }}
          </div>
          <div v-if="!feedback.is_correct" class="fb-answer">
            正确答案：<strong>{{ feedback.correct_answer }}</strong>
          </div>
          <div class="fb-explain">{{ feedback.explanation }}</div>
          <button class="next-btn" @click="next">下一题 →</button>
        </div>
      </div>
    </div>

    <!-- 结束总结 -->
    <div v-else-if="finished" class="summary">
      <div class="summary-icon">🎉</div>
      <div class="summary-score">{{ session.correct }} / {{ session.total }}</div>
      <div class="summary-pct">正确率 {{ Math.round(session.correct / session.total * 100) }}%</div>
      <div class="summary-actions">
        <button class="btn-primary" @click="begin">再来一轮</button>
        <button class="btn-secondary" @click="router.push('/wrong')">复习错题</button>
        <button class="btn-text" @click="reset">返回</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  fetchExamTypes, fetchSubjects, fetchChapters,
  startPractice as apiStartPractice, submitAnswer as apiSubmitAnswer,
  generateQuestions as apiGenerateQuestions,
} from '../api/exam.js'

const router = useRouter()
const route = useRoute()

const examTypes = ref([])
const subjects = ref([])
const chapters = ref([])
const config = ref({ subjectId: '', chapterId: '', difficulty: '', count: 10 })
const session = ref(null)
const currentQ = ref(null)
const selectedAnswer = ref(null)
const fillAnswer = ref('')
const feedback = ref(null)
const finished = ref(false)
const generating = ref(false)

const progressPercent = computed(() => {
  if (!session.value) return 0
  return Math.round((session.value.current / session.value.total) * 100)
})

// 初始化：加载所有考试类型的科目
;(async () => {
  try {
    examTypes.value = await fetchExamTypes()
    // 加载所有科目的扁平列表
    for (const e of examTypes.value) {
      const subs = await fetchSubjects(e.id)
      subjects.value.push(...subs)
    }
    const sid = route.query.subject_id
    if (sid) {
      config.value.subjectId = sid
      chapters.value = await fetchChapters(sid)
      if (route.query.chapter_id) config.value.chapterId = route.query.chapter_id
      // 自动开始
      if (route.query.auto_start === '1') {
        await begin()
      }
    }
  } catch {}
})()

async function onSubjectChange() {
  chapters.value = []
  if (config.value.subjectId) {
    try { chapters.value = await fetchChapters(config.value.subjectId) } catch {}
  }
}

function ensureOptions(q) {
  if (q.type === 'true_false' && (!q.options || !q.options.length)) {
    return { ...q, options: [{label: 'True', text: '正确'}, {label: 'False', text: '错误'}] }
  }
  if (q.type !== 'fill_blank' && (!q.options || !q.options.length)) {
    return { ...q, options: [{label: 'A'}, {label: 'B'}, {label: 'C'}, {label: 'D'}] }
  }
  return q
}

async function begin() {
  const result = await apiStartPractice({
    subjectId: config.value.subjectId,
    chapterId: config.value.chapterId || undefined,
    difficulty: config.value.difficulty || undefined,
    count: config.value.count,
  })
  if (!result.questions?.length) return
  const questions = result.questions.map(q => ensureOptions(q))
  session.value = {
    questions,
    current: 0,
    correct: 0,
    total: result.questions.length,
    subjectId: config.value.subjectId,
    chapterId: config.value.chapterId,
  }
  currentQ.value = questions[0]
  selectedAnswer.value = null
  fillAnswer.value = ''
  feedback.value = null
  finished.value = false
}

async function beginAi() {
  generating.value = true
  try {
    const chapterName = chapters.value.find(c => c.id === config.value.chapterId)?.name || ''
    const subjectName = subjects.value.find(s => s.id === config.value.subjectId)?.name || ''

    const result = await apiGenerateQuestions({
      subjectId: config.value.subjectId,
      chapterId: config.value.chapterId || undefined,
      subjectName,
      chapterName,
      count: config.value.count,
    })

    const questions = result.questions || []
    if (!questions.length) return

    // 把 AI 生成的题目直接作为练习会话
    const mapped = questions.map(q => ensureOptions({
      id: q.id || `ai_${Date.now()}_${Math.random()}`,
      type: q.type || 'single_choice',
      difficulty: q.difficulty || 'medium',
      question_text: q.question_text,
      options: q.options || [],
    }))
    session.value = {
      questions: mapped,
      current: 0,
      correct: 0,
      total: questions.length,
      subjectId: config.value.subjectId,
      chapterId: config.value.chapterId,
    }
    currentQ.value = session.value.questions[0]
    selectedAnswer.value = null
    fillAnswer.value = ''
    feedback.value = null
    finished.value = false
  } catch (e) {
    alert('AI 出题失败，请重试: ' + (e.response?.data?.detail || e.message))
  } finally {
    generating.value = false
  }
}

function selectOption(label) {
  if (feedback.value) return
  if (currentQ.value.type === 'multi_choice') {
    // 多选 toggle
    const arr = selectedAnswer.value ? selectedAnswer.value.split(',') : []
    const idx = arr.indexOf(label)
    if (idx >= 0) arr.splice(idx, 1)
    else arr.push(label)
    selectedAnswer.value = arr.sort().join(',')
  } else {
    selectedAnswer.value = label
  }
}

async function submitAnswer(answer) {
  if (!answer || !currentQ.value) return
  try {
    const result = await apiSubmitAnswer({
      questionId: currentQ.value.id,
      userAnswer: answer,
      subjectId: session.value.subjectId,
      chapterId: session.value.chapterId || undefined,
    })
    feedback.value = result
    if (result.is_correct) session.value.correct++
  } catch (e) {
    alert('提交失败，请重试: ' + (e.response?.data?.detail || e.message))
  }
}

function next() {
  session.value.current++
  if (session.value.current >= session.value.questions.length) {
    finishSession()
    return
  }
  currentQ.value = session.value.questions[session.value.current]
  selectedAnswer.value = null
  fillAnswer.value = ''
  feedback.value = null
}

function finishSession() { finished.value = true }

function reset() {
  session.value = null
  currentQ.value = null
  feedback.value = null
  finished.value = false
  selectedAnswer.value = null
  fillAnswer.value = ''
}

function typeLabel(t) {
  return {
    single_choice: '单选题', multi_choice: '多选题',
    true_false: '判断题', fill_blank: '填空题',
  }[t] || t
}
</script>

<style scoped>
.page { padding: 20px 16px; min-height: 100%; }
.page-title { font-size: 20px; margin-bottom: 20px; }

.setup { max-width: 400px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 8px; color: var(--text-secondary); }
.form-select {
  width: 100%; padding: 12px; font-size: 15px; border: 1px solid var(--border);
  border-radius: 10px; background: var(--card);
}
.chip-row { display: flex; gap: 8px; }
.chip-sm {
  padding: 8px 16px; font-size: 14px; border: 1px solid var(--border);
  border-radius: 8px; background: var(--card); cursor: pointer;
}
.chip-sm.active { background: var(--primary); color: #fff; border-color: var(--primary); }
.range { width: 100%; margin-bottom: 4px; }
.range-val { font-size: 14px; color: var(--primary); font-weight: 600; }
.start-btn {
  width: 100%; padding: 16px; font-size: 18px; font-weight: 700;
  background: var(--primary); color: #fff; border: none;
  border-radius: 12px; cursor: pointer; margin-top: 8px;
}
.start-btn:disabled { opacity: 0.5; }

/* Practice */
.practice { }
.progress-bar { height: 6px; background: var(--border); border-radius: 3px; margin-bottom: 8px; }
.progress-fill { height: 100%; background: var(--primary); border-radius: 3px; transition: width 0.3s; }
.progress-info { display: flex; justify-content: space-between; font-size: 13px; color: var(--text-secondary); margin-bottom: 20px; }

.question-area { background: var(--card); border-radius: 14px; padding: 20px; }
.q-type-tag {
  display: inline-block; font-size: 12px; padding: 3px 10px;
  background: var(--primary-light); color: var(--primary); border-radius: 4px;
  margin-bottom: 12px;
}
.q-stem { font-size: 16px; line-height: 1.6; margin-bottom: 20px; }

.options { display: flex; flex-direction: column; gap: 10px; }
.option {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 14px; border: 2px solid var(--border); border-radius: 12px;
  background: var(--card); cursor: pointer; font-size: 15px;
  text-align: left; transition: all 0.15s;
}
.option:active { background: var(--primary-light); }
.option--selected { border-color: var(--primary); background: var(--primary-light); }
.option--correct { border-color: var(--correct); background: #dcfce7; }
.option--wrong { border-color: var(--wrong); background: #fee2e2; }
.opt-badge {
  width: 26px; height: 26px; border-radius: 50%;
  background: var(--bg); display: flex; align-items: center;
  justify-content: center; font-weight: 700; font-size: 13px;
  flex-shrink: 0;
}

.fill-input-wrap { display: flex; gap: 10px; }
.fill-input {
  flex: 1; padding: 14px; font-size: 16px; border: 2px solid var(--border);
  border-radius: 12px; outline: none;
}
.fill-input:focus { border-color: var(--primary); }

.confirm-row { margin-top: 16px; }
.submit-btn {
  padding: 12px 24px; font-size: 16px; font-weight: 600;
  background: var(--primary); color: #fff; border: none;
  border-radius: 10px; cursor: pointer;
}
.submit-btn:disabled { opacity: 0.5; }

.feedback { margin-top: 16px; padding: 16px; border-radius: 12px; }
.fb-correct { background: #dcfce7; border: 1px solid var(--correct); }
.fb-wrong { background: #fee2e2; border: 1px solid var(--wrong); }
.fb-header { font-size: 16px; font-weight: 700; margin-bottom: 8px; }
.fb-answer { margin-bottom: 8px; font-size: 14px; }
.fb-explain { font-size: 14px; line-height: 1.6; color: var(--text); margin-bottom: 12px; }
.next-btn {
  padding: 10px 20px; font-size: 15px; font-weight: 600;
  background: var(--card); border: 1px solid var(--border);
  border-radius: 8px; cursor: pointer; width: 100%;
}

/* Summary */
.summary { text-align: center; padding: 40px 0; }
.summary-icon { font-size: 64px; margin-bottom: 16px; }
.summary-score { font-size: 48px; font-weight: 800; color: var(--primary); }
.summary-pct { font-size: 18px; color: var(--text-secondary); margin: 8px 0 24px; }
.summary-actions { display: flex; flex-direction: column; gap: 10px; max-width: 320px; margin: 0 auto; }
.btn-primary {
  padding: 16px; font-size: 16px; font-weight: 700;
  background: var(--primary); color: #fff; border: none; border-radius: 12px; cursor: pointer;
}
.btn-secondary {
  padding: 14px; font-size: 15px; font-weight: 600;
  background: var(--card); border: 1px solid var(--border); border-radius: 12px; cursor: pointer;
}
.btn-text {
  padding: 10px; font-size: 14px; background: none; border: none;
  color: var(--text-secondary); cursor: pointer;
}

.ai-btn {
  width: 100%; padding: 14px; font-size: 15px; font-weight: 600;
  background: #fff; color: var(--primary); border: 2px dashed var(--primary);
  border-radius: 12px; cursor: pointer; margin-top: 10px;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.ai-btn:disabled { opacity: 0.5; }
.ai-hint { font-size: 12px; color: var(--text-secondary); text-align: center; margin-top: 8px; }

.spinner {
  width: 16px; height: 16px; border: 2px solid var(--primary);
  border-top-color: transparent; border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>

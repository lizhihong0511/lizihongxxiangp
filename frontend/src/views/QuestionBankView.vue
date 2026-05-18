<template>
  <div class="page">
    <h2 class="page-title">题库</h2>

    <!-- 考试类型 -->
    <div class="section" v-if="!selectedExam">
      <div class="chip-row">
        <button v-for="e in examTypes" :key="e.id" class="chip" @click="selectExam(e)">
          <span>{{ e.icon }}</span>
          <span>{{ e.name }}</span>
        </button>
      </div>
    </div>

    <!-- 科目 -->
    <div class="section" v-if="selectedExam && !selectedSubject">
      <button class="back-btn" @click="selectedExam = null">← 返回</button>
      <div class="chip-row" style="margin-top:12px">
        <button v-for="s in subjects" :key="s.id" class="chip" @click="selectSubject(s)">
          {{ s.name }}
        </button>
      </div>
    </div>

    <!-- 章节 -->
    <div class="section" v-if="selectedSubject">
      <button class="back-btn" @click="goBack">← 返回</button>
      <div class="list" style="margin-top:12px">
        <button
          v-for="c in chapters" :key="c.id"
          class="list-item"
          @click="selectChapter(c)"
        >
          <span>{{ c.name }}</span>
          <span class="list-actions">
            <span class="practice-chapter-btn" @click.stop="startChapterPractice(c)">✏️ 练习</span>
            <span class="list-arrow">→</span>
          </span>
        </button>
      </div>
    </div>

    <!-- 题目列表 -->
    <div v-if="questions.length" class="section">
      <div class="filter-row">
        <select v-model="filterDifficulty" @change="loadQuestions" class="filter-select">
          <option value="">全部难度</option>
          <option value="easy">简单</option>
          <option value="medium">中等</option>
          <option value="hard">困难</option>
        </select>
        <select v-model="filterType" @change="loadQuestions" class="filter-select">
          <option value="">全部题型</option>
          <option value="single_choice">单选题</option>
          <option value="multi_choice">多选题</option>
          <option value="true_false">判断题</option>
          <option value="fill_blank">填空题</option>
        </select>
      </div>

      <div v-for="q in questions" :key="q.id" class="question-card" @click="showDetail(q)">
        <div class="q-meta">
          <span class="q-tag" :class="q.difficulty">{{ diffLabel(q.difficulty) }}</span>
          <span class="q-tag type">{{ typeLabel(q.type) }}</span>
        </div>
        <div class="q-text">{{ q.question_text }}</div>
      </div>

      <div v-if="totalPages > 1" class="pager">
        <button :disabled="page <= 1" @click="page--; loadQuestions()">上一页</button>
        <span>{{ page }} / {{ totalPages }}</span>
        <button :disabled="page >= totalPages" @click="page++; loadQuestions()">下一页</button>
      </div>
    </div>

    <!-- 题目详情弹窗 -->
    <div v-if="detailQ" class="modal" @click.self="detailQ = null">
      <div class="modal-card">
        <div class="q-meta" style="margin-bottom:12px">
          <span class="q-tag" :class="detailQ.difficulty">{{ diffLabel(detailQ.difficulty) }}</span>
          <span class="q-tag type">{{ typeLabel(detailQ.type) }}</span>
        </div>
        <div class="q-text" style="margin-bottom:16px">{{ detailQ.question_text }}</div>
        <div v-if="detailQ.options && detailQ.options.length" class="options-list">
          <div v-for="opt in detailQ.options" :key="opt.label" class="opt-item">
            <span class="opt-label">{{ opt.label }}</span>
            <span>{{ opt.text }}</span>
          </div>
        </div>
        <button class="practice-btn" @click="startPractice(detailQ)">📝 开始练习</button>
        <button class="close-btn" @click="detailQ = null">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  fetchExamTypes, fetchSubjects, fetchChapters,
  fetchQuestions, startPractice as apiStartPractice,
} from '../api/exam.js'

const router = useRouter()
const route = useRoute()

const examTypes = ref([])
const subjects = ref([])
const chapters = ref([])
const questions = ref([])
const selectedExam = ref(null)
const selectedSubject = ref(null)
const selectedChapter = ref(null)
const detailQ = ref(null)
const filterDifficulty = ref('')
const filterType = ref('')
const page = ref(1)
const totalPages = ref(1)

onMounted(async () => {
  try { examTypes.value = await fetchExamTypes() } catch {}
  const examId = route.query.exam_id
  if (examId) {
    const e = examTypes.value.find(t => t.id === examId)
    if (e) await selectExam(e)
  }
})

async function selectExam(e) {
  selectedExam.value = e
  subjects.value = []
  try { subjects.value = await fetchSubjects(e.id) } catch {}
}

async function selectSubject(s) {
  selectedSubject.value = s
  chapters.value = []
  try { chapters.value = await fetchChapters(s.id) } catch {}
}

async function selectChapter(c) {
  selectedChapter.value = c
  await loadQuestions()
}

function goBack() {
  if (selectedChapter.value) {
    selectedChapter.value = null
    questions.value = []
  } else {
    selectedSubject.value = null
    selectedExam.value = null
    chapters.value = []
  }
}

async function loadQuestions() {
  const result = await fetchQuestions({
    subjectId: selectedSubject.value?.id,
    chapterId: selectedChapter.value?.id,
    difficulty: filterDifficulty.value || undefined,
    type: filterType.value || undefined,
    page: page.value,
  })
  questions.value = result.items || []
  totalPages.value = Math.ceil((result.total || 0) / 20)
}

function showDetail(q) { detailQ.value = q }

function startChapterPractice(c) {
  router.push({
    path: '/practice',
    query: {
      subject_id: selectedSubject.value?.id,
      chapter_id: c.id,
      auto_start: '1',
    },
  })
}

function startPractice(q) {
  router.push({
    path: '/practice',
    query: {
      subject_id: selectedSubject.value?.id,
      chapter_id: q.chapter_id || '',
      auto_start: '1',
    },
  })
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

.section { margin-bottom: 20px; }
.chip-row { display: flex; gap: 10px; flex-wrap: wrap; }
.chip {
  display: flex; align-items: center; gap: 6px;
  background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; padding: 12px 18px; font-size: 15px; cursor: pointer;
}
.chip:active { background: var(--primary-light); }

.back-btn {
  background: none; border: none; color: var(--primary);
  font-size: 15px; cursor: pointer; padding: 4px 0;
}

.list { display: flex; flex-direction: column; gap: 8px; }
.list-item {
  display: flex; justify-content: space-between; align-items: center;
  background: var(--card); border: none; border-radius: 10px;
  padding: 14px 16px; font-size: 15px; cursor: pointer; width: 100%;
  text-align: left;
}
.list-item:active { background: var(--primary-light); }
.list-actions { display: flex; align-items: center; gap: 8px; }
.list-arrow { color: var(--text-secondary); }
.practice-chapter-btn {
  font-size: 12px; padding: 4px 10px; background: var(--primary-light);
  color: var(--primary); border-radius: 6px; white-space: nowrap;
}

.filter-row { display: flex; gap: 8px; margin-bottom: 12px; }
.filter-select {
  flex: 1; font-size: 13px; padding: 8px 10px;
  border: 1px solid var(--border); border-radius: 8px; background: var(--card);
}

.question-card {
  background: var(--card); border-radius: 10px; padding: 14px 16px;
  margin-bottom: 8px; cursor: pointer;
}
.q-meta { display: flex; gap: 6px; margin-bottom: 8px; }
.q-tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; }
.q-tag.easy { background: #dcfce7; color: #16a34a; }
.q-tag.medium { background: #fef3c7; color: #d97706; }
.q-tag.hard { background: #fee2e2; color: #dc2626; }
.q-tag.type { background: #eef2ff; color: var(--primary); }
.q-text { font-size: 14px; line-height: 1.5; }

.pager { display: flex; justify-content: center; gap: 16px; align-items: center; margin-top: 16px; }
.pager button {
  padding: 8px 16px; background: var(--card); border: 1px solid var(--border);
  border-radius: 8px; cursor: pointer;
}
.pager button:disabled { opacity: 0.4; }

.modal {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: flex-end; justify-content: center; z-index: 100;
}
.modal-card {
  background: var(--card); border-radius: 16px 16px 0 0;
  padding: 24px 20px; width: 100%; max-width: 480px; max-height: 80vh;
  overflow-y: auto;
}
.options-list { margin-bottom: 20px; }
.opt-item {
  display: flex; gap: 10px; padding: 10px 12px; background: var(--bg);
  border-radius: 8px; margin-bottom: 6px; font-size: 14px;
}
.opt-label { font-weight: 700; color: var(--primary); min-width: 20px; }
.practice-btn {
  width: 100%; padding: 14px; background: var(--primary); color: #fff;
  border: none; border-radius: 10px; font-size: 16px; font-weight: 600;
  cursor: pointer; margin-bottom: 8px;
}
.close-btn {
  width: 100%; padding: 12px; background: var(--bg); border: none;
  border-radius: 10px; font-size: 15px; cursor: pointer;
}
</style>

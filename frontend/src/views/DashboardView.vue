<template>
  <div class="page">
    <h2 class="page-title">考证刷题助手</h2>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ stats.totalAnswered }}</div>
        <div class="stat-label">总答题</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.accuracy }}%</div>
        <div class="stat-label">正确率</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.wrongCount }}</div>
        <div class="stat-label">待复习</div>
      </div>
    </div>

    <div class="quick-actions">
      <router-link to="/qa" class="action-card">
        <span class="action-icon">💬</span>
        <div>
          <div class="action-title">AI 问答</div>
          <div class="action-sub">问知识点，AI 帮你解答</div>
        </div>
        <span class="action-arrow">→</span>
      </router-link>

      <router-link to="/bank" class="action-card">
        <span class="action-icon">📋</span>
        <div>
          <div class="action-title">题库浏览</div>
          <div class="action-sub">考研 / 公考 / 教资</div>
        </div>
        <span class="action-arrow">→</span>
      </router-link>

      <router-link to="/wrong" class="action-card">
        <span class="action-icon">📝</span>
        <div>
          <div class="action-title">错题复习</div>
          <div class="action-sub">{{ stats.wrongCount }} 道待复习</div>
        </div>
        <span class="action-arrow">→</span>
      </router-link>
    </div>

    <div class="section" v-if="examTypes.length">
      <h3 class="section-title">考试类型</h3>
      <div class="exam-grid">
        <button
          v-for="e in examTypes" :key="e.id"
          class="exam-chip"
          @click="goToBank(e.id)"
        >
          <span>{{ e.icon }}</span>
          <span>{{ e.name }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchExamTypes, fetchProgress, fetchWrongAnswers } from '../api/exam.js'

const router = useRouter()

const examTypes = ref([])
const stats = ref({ totalAnswered: 0, accuracy: 0, wrongCount: 0 })

onMounted(async () => {
  try {
    examTypes.value = await fetchExamTypes()
  } catch {}
  try {
    const progress = await fetchProgress()
    let answered = 0, correct = 0
    for (const p of progress) {
      answered += p.total_answered || 0
      correct += p.total_correct || 0
    }
    stats.value.totalAnswered = answered
    stats.value.accuracy = answered > 0 ? Math.round((correct / answered) * 100) : 0
  } catch {}
  try {
    const wrong = await fetchWrongAnswers({ isReviewed: false })
    stats.value.wrongCount = wrong.total || 0
  } catch {}
})

function goToBank(examId) {
  router.push({ path: '/bank', query: { exam_id: examId } })
}
</script>

<style scoped>
.page { padding: 20px 16px; }
.page-title { font-size: 22px; margin-bottom: 20px; }

.stats-row { display: flex; gap: 10px; margin-bottom: 24px; }
.stat-card {
  flex: 1; background: var(--card); border-radius: 12px;
  padding: 16px; text-align: center;
}
.stat-value { font-size: 28px; font-weight: 700; color: var(--primary); }
.stat-label { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }

.quick-actions { display: flex; flex-direction: column; gap: 10px; margin-bottom: 24px; }
.action-card {
  display: flex; align-items: center; gap: 12px;
  background: var(--card); border-radius: 12px; padding: 16px;
  text-decoration: none; color: var(--text);
}
.action-icon { font-size: 28px; }
.action-title { font-weight: 600; margin-bottom: 2px; }
.action-sub { font-size: 13px; color: var(--text-secondary); }
.action-arrow { margin-left: auto; color: var(--text-secondary); font-size: 18px; }

.section-title { font-size: 16px; font-weight: 600; margin-bottom: 12px; }
.exam-grid { display: flex; gap: 10px; flex-wrap: wrap; }
.exam-chip {
  display: flex; align-items: center; gap: 6px;
  background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; padding: 12px 18px;
  font-size: 15px; cursor: pointer;
}
.exam-chip:hover { border-color: var(--primary); background: var(--primary-light); }
</style>

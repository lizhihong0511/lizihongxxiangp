<template>
  <div class="page">
    <h2 class="page-title">我的</h2>

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

    <div class="menu-list">
      <div class="menu-item" @click="goAdmin">
        <span>📥 题库管理</span>
        <span class="menu-arrow">→</span>
      </div>
      <div class="menu-item" @click="clearCache">
        <span>🗑️ 清除本地缓存</span>
        <span class="menu-arrow">→</span>
      </div>
      <div class="menu-item" @click="showAbout = true">
        <span>ℹ️ 关于</span>
        <span class="menu-arrow">→</span>
      </div>
    </div>

    <div class="about-text">
      <p>考证刷题助手 v0.1</p>
      <p>AI 驱动的考证练习平台</p>
      <p>支持考研 / 公考 / 教资</p>
      <p class="user-id">你的 ID：<code>{{ userId }}</code></p>
      <p class="user-id-hint">在 .env 文件中设置 ADMIN_IDS 获取管理权限</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchProgress, fetchWrongAnswers, getUserId } from '../api/exam.js'

const router = useRouter()
const stats = ref({ totalAnswered: 0, accuracy: 0, wrongCount: 0 })
const showAbout = ref(false)
const userId = getUserId()

onMounted(async () => {
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

function goAdmin() {
  router.push('/admin')
}

function clearCache() {
  localStorage.removeItem('exam_user_id')
  location.reload()
}
</script>

<style scoped>
.page { padding: 20px 16px; }
.page-title { font-size: 20px; margin-bottom: 20px; }

.stats-row { display: flex; gap: 10px; margin-bottom: 32px; }
.stat-card {
  flex: 1; background: var(--card); border-radius: 12px;
  padding: 16px; text-align: center;
}
.stat-value { font-size: 28px; font-weight: 700; color: var(--primary); }
.stat-label { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }

.menu-list { display: flex; flex-direction: column; border-radius: 12px; overflow: hidden; margin-bottom: 24px; }
.menu-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px; background: var(--card); cursor: pointer;
  font-size: 15px;
}
.menu-item:not(:last-child) { border-bottom: 1px solid var(--border); }
.menu-arrow { color: var(--text-secondary); }

.about-text { text-align: center; font-size: 13px; color: var(--text-secondary); line-height: 1.8; }
.user-id { margin-top: 16px; font-size: 12px; }
.user-id code { background: var(--bg); padding: 2px 6px; border-radius: 4px; font-size: 11px; }
.user-id-hint { font-size: 11px; color: #aaa; margin-top: 2px; }
</style>

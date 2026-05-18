<template>
  <div class="page">
    <h2 class="page-title">错题本</h2>

    <div class="filter-row">
      <button :class="['filter-chip', filterReviewed === null && 'active']" @click="filterReviewed = null; load()">全部</button>
      <button :class="['filter-chip', filterReviewed === false && 'active']" @click="filterReviewed = false; load()">待复习</button>
      <button :class="['filter-chip', filterReviewed === true && 'active']" @click="filterReviewed = true; load()">已复习</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="items.length === 0" class="empty">
      <div class="empty-icon">🎉</div>
      <div>暂无错题记录</div>
    </div>

    <div v-else class="list">
      <div v-for="item in items" :key="item.id" class="wrong-card">
        <div class="wc-header">
          <span class="wc-tag" :class="item.is_reviewed ? 'reviewed' : 'pending'">
            {{ item.is_reviewed ? '已复习' : '待复习' }}
          </span>
          <span class="wc-count" v-if="item.wrong_count > 1">错 {{ item.wrong_count }} 次</span>
        </div>
        <div class="wc-question">{{ item.question?.question_text }}</div>
        <div class="wc-answers">
          <div class="wc-mine">❌ 你的答案：<strong>{{ item.user_answer }}</strong></div>
          <div class="wc-correct">✅ 正确答案：<strong>{{ item.question?.correct_answer }}</strong></div>
        </div>
        <div class="wc-actions">
          <button v-if="!item.is_reviewed" class="wc-btn primary" @click="markReviewed(item)">标记已复习</button>
          <button class="wc-btn" @click="removeItem(item)">删除</button>
        </div>
      </div>
    </div>

    <div v-if="totalPages > 1" class="pager">
      <button :disabled="page <= 1" @click="page--; load()">上一页</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="page++; load()">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchWrongAnswers, retryWrongAnswer, deleteWrongAnswer } from '../api/exam.js'

const loading = ref(false)
const items = ref([])
const filterReviewed = ref(null)
const page = ref(1)
const totalPages = ref(1)

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    const result = await fetchWrongAnswers({
      isReviewed: filterReviewed.value,
      page: page.value,
    })
    items.value = result.items || []
    totalPages.value = Math.ceil((result.total || 0) / 20)
  } catch {} finally { loading.value = false }
}

async function markReviewed(item) {
  await retryWrongAnswer(item.id)
  item.is_reviewed = true
}

async function removeItem(item) {
  await deleteWrongAnswer(item.id)
  items.value = items.value.filter(i => i.id !== item.id)
}
</script>

<style scoped>
.page { padding: 20px 16px; }
.page-title { font-size: 20px; margin-bottom: 16px; }

.filter-row { display: flex; gap: 8px; margin-bottom: 16px; }
.filter-chip {
  padding: 8px 16px; font-size: 14px; border: 1px solid var(--border);
  border-radius: 8px; background: var(--card); cursor: pointer;
}
.filter-chip.active { background: var(--primary); color: #fff; border-color: var(--primary); }

.loading { text-align: center; padding: 40px; color: var(--text-secondary); }
.empty { text-align: center; padding: 60px 0; color: var(--text-secondary); }
.empty-icon { font-size: 48px; margin-bottom: 12px; }

.list { display: flex; flex-direction: column; gap: 12px; }
.wrong-card { background: var(--card); border-radius: 12px; padding: 16px; }
.wc-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.wc-tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; }
.wc-tag.pending { background: #fee2e2; color: var(--wrong); }
.wc-tag.reviewed { background: #dcfce7; color: var(--correct); }
.wc-count { font-size: 12px; color: var(--text-secondary); }
.wc-question { font-size: 14px; line-height: 1.5; margin-bottom: 10px; }
.wc-answers { margin-bottom: 12px; }
.wc-mine, .wc-correct { font-size: 13px; margin-bottom: 4px; }
.wc-mine strong { color: var(--wrong); }
.wc-correct strong { color: var(--correct); }
.wc-actions { display: flex; gap: 8px; }
.wc-btn {
  padding: 8px 16px; font-size: 13px; border: 1px solid var(--border);
  border-radius: 8px; background: var(--card); cursor: pointer;
}
.wc-btn.primary { background: var(--primary); color: #fff; border-color: var(--primary); }

.pager { display: flex; justify-content: center; gap: 16px; align-items: center; margin-top: 16px; }
.pager button {
  padding: 8px 16px; background: var(--card); border: 1px solid var(--border);
  border-radius: 8px; cursor: pointer;
}
.pager button:disabled { opacity: 0.4; }
</style>

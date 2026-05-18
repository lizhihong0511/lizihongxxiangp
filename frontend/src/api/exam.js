import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
})

function getUserId() {
  let id = localStorage.getItem('exam_user_id')
  if (!id) {
    id = 'u_' + crypto.randomUUID()
    localStorage.setItem('exam_user_id', id)
  }
  return id
}

// 考试类型
export async function fetchExamTypes() {
  const resp = await api.get('/api/exam/types')
  return resp.data.data
}

// 科目
export async function fetchSubjects(examId) {
  const resp = await api.get(`/api/exam/types/${examId}/subjects`)
  return resp.data.data
}

// 章节
export async function fetchChapters(subjectId) {
  const resp = await api.get(`/api/exam/subjects/${subjectId}/chapters`)
  return resp.data.data
}

// 题目列表
export async function fetchQuestions({ subjectId, chapterId, difficulty, type, page = 1, size = 20 }) {
  const params = { page, size }
  if (subjectId) params.subject_id = subjectId
  if (chapterId) params.chapter_id = chapterId
  if (difficulty) params.difficulty = difficulty
  if (type) params.type = type
  const resp = await api.get('/api/exam/questions', { params })
  return resp.data.data
}

// 开始练习
export async function startPractice({ subjectId, chapterId, difficulty, count = 10 }) {
  const resp = await api.post('/api/exam/practice/start', {
    subject_id: subjectId, chapter_id: chapterId,
    difficulty, count,
  })
  return resp.data.data
}

// 提交答案
export async function submitAnswer({ questionId, userAnswer, subjectId, chapterId }) {
  const resp = await api.post('/api/exam/practice/submit', {
    question_id: questionId, user_answer: userAnswer,
    user_id: getUserId(), subject_id: subjectId, chapter_id: chapterId,
  })
  return resp.data.data
}

// AI 生成题目
export async function generateQuestions({ subjectId, chapterId, subjectName, chapterName, weakTopics, count = 5 }) {
  const resp = await api.post('/api/exam/practice/generate', {
    subject_id: subjectId, chapter_id: chapterId,
    subject_name: subjectName, chapter_name: chapterName,
    weak_topics: weakTopics, count,
  })
  return resp.data.data
}

// AI 问答
export async function askQuestion(question, subjectName, subjectId) {
  const resp = await api.post('/api/exam/qa/ask', {
    question, subject_name: subjectName, subject_id: subjectId,
    user_id: getUserId(),
  })
  return resp.data.data
}

// 进度
export async function fetchProgress(subjectId) {
  const params = { user_id: getUserId() }
  if (subjectId) params.subject_id = subjectId
  const resp = await api.get('/api/exam/progress', { params })
  return resp.data.data
}

// 错题本
export async function fetchWrongAnswers({ isReviewed, page = 1, size = 20 }) {
  const params = { user_id: getUserId(), page, size }
  if (isReviewed !== undefined && isReviewed !== null) params.is_reviewed = isReviewed
  const resp = await api.get('/api/exam/wrong-answers', { params })
  return resp.data.data
}

// 标记错题已复习
export async function retryWrongAnswer(wrongId) {
  await api.post(`/api/exam/wrong-answers/${wrongId}/retry`, {})
}

// 删除错题
export async function deleteWrongAnswer(wrongId) {
  await api.delete(`/api/exam/wrong-answers/${wrongId}`)
}

export { getUserId }

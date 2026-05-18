import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
})

export async function uploadAndParse(file, userId) {
  const form = new FormData()
  form.append('file', file)
  form.append('user_id', userId)
  const resp = await api.post('/api/admin/parse-doc', form)
  return resp.data.data
}

export async function importQuestions(questions, userId, subjectId, chapterId) {
  const resp = await api.post('/api/admin/import-questions', {
    questions,
    user_id: userId,
    subject_id: subjectId,
    chapter_id: chapterId,
  })
  return resp.data.data
}

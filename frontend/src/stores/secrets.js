import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useSecretsStore = defineStore('secrets', () => {
  const secrets = ref([])
  const categories = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchSecrets(categoryId = null, keyword = '') {
    loading.value = true
    error.value = ''
    const params = {}
    if (categoryId) params.category_id = categoryId
    if (keyword) params.keyword = keyword
    const res = await api.get('/secrets', { params })
    secrets.value = res.data
    loading.value = false
  }

  async function fetchSecret(id) {
    const res = await api.get(`/secrets/item/${id}`)
    return res.data
  }

  async function createSecret(data) {
    const res = await api.post('/secrets', data)
    return res.data
  }

  async function updateSecret(id, data) {
    const res = await api.put(`/secrets/${id}`, data)
    return res.data
  }

  async function deleteSecret(id) {
    await api.delete(`/secrets/${id}`)
  }

  async function searchSecrets(keyword) {
    const res = await api.get(`/secrets/q/${encodeURIComponent(keyword)}`)
    secrets.value = res.data
  }

  async function fetchCategories() {
    const res = await api.get('/categories')
    categories.value = res.data
  }

  async function createCategory(name, icon = 'tag') {
    const res = await api.post('/categories', { name, icon })
    await fetchCategories()
    return res.data
  }

  async function deleteCategory(id) {
    await api.delete(`/categories/${id}`)
    await fetchCategories()
  }

  async function exportCsv() {
    const res = await api.get('/export/csv', { responseType: 'blob' })
    downloadBlob(res.data, 'secretbox_export.csv')
  }

  async function exportJson() {
    const res = await api.get('/export/json', { responseType: 'blob' })
    downloadBlob(res.data, 'secretbox_export.json')
  }

  async function importCsv(file, masterPassword, categoryName = '通用密码') {
    const form = new FormData()
    form.append('file', file)
    form.append('category_name', categoryName)
    if (masterPassword) {
      form.append('master_password', masterPassword)
    }
    const res = await api.post(
      '/import/csv-password',
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    return res.data
  }

  return {
    secrets, categories, loading, error,
    fetchSecrets, fetchSecret, createSecret, updateSecret, deleteSecret,
    searchSecrets, fetchCategories, createCategory, deleteCategory,
    exportCsv, exportJson, importCsv,
  }
})

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

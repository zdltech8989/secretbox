import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('sb_token') || '')
  const currentUser = ref(JSON.parse(localStorage.getItem('sb_user') || 'null'))
  const vaultUnlocked = ref(false)
  const masterInitialized = ref(false)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => currentUser.value?.is_admin === true)

  async function checkStatus() {
    try {
      const res = await api.get('/auth/status')
      masterInitialized.value = res.data.initialized
      return res.data.initialized
    } catch {
      masterInitialized.value = false
      return false
    }
  }

  async function fetchMe() {
    try {
      const res = await api.get('/auth/me')
      currentUser.value = res.data
      localStorage.setItem('sb_user', JSON.stringify(res.data))
    } catch {
      currentUser.value = null
      localStorage.removeItem('sb_user')
    }
  }

  async function checkVaultStatus() {
    try {
      const res = await api.get('/auth/vault-status')
      vaultUnlocked.value = res.data.unlocked
    } catch {
      vaultUnlocked.value = false
    }
  }

  async function login(username, password) {
    const res = await api.post('/auth/login', { username, password })
    token.value = res.data.token
    localStorage.setItem('sb_token', res.data.token)
    vaultUnlocked.value = false
    await fetchMe()
    await checkStatus()
    return res.data
  }

  async function setupVault(password) {
    const res = await api.post('/auth/setup', { password }, { timeout: 60000 })
    masterInitialized.value = true
    vaultUnlocked.value = true
    return res.data
  }

  async function unlockVault(masterPassword) {
    console.log('开始解锁保险箱...')
    try {
      const res = await api.post('/auth/unlock-vault', { master_password: masterPassword }, { timeout: 60000 })
      console.log('解锁成功', res.data)
      vaultUnlocked.value = true
      return res.data
    } catch (e) {
      console.error('解锁失败', e)
      throw e
    }
  }

  async function changePassword(oldPassword, newPassword) {
    const res = await api.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    token.value = res.data.token
    localStorage.setItem('sb_token', res.data.token)
    await fetchMe()
    return res.data
  }

  async function resetMasterPassword(oldMasterPassword, newMasterPassword) {
    const res = await api.post('/auth/reset-master-password', {
      old_master_password: oldMasterPassword,
      new_master_password: newMasterPassword,
    })
    return res.data
  }

  function lockVault() {
    vaultUnlocked.value = false
  }

  function logout() {
    token.value = ''
    currentUser.value = null
    vaultUnlocked.value = false
    masterInitialized.value = false
    localStorage.removeItem('sb_token')
    localStorage.removeItem('sb_user')
  }

  // 恢复 vaultUnlocked 状态为 false（页面刷新时始终需要重新解锁）
  function initFromStorage() {
    vaultUnlocked.value = false
    if (token.value) {
      checkStatus()
    }
  }

  return {
    token, currentUser, vaultUnlocked, masterInitialized, isLoggedIn, isAdmin,
    checkStatus, fetchMe, checkVaultStatus, login, setupVault, unlockVault, lockVault, changePassword, resetMasterPassword, logout, initFromStorage,
  }
})

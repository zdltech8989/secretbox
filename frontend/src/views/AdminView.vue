<template>
  <div class="min-h-screen pt-20 pb-20 md:pb-8 px-4 lg:px-6">
    <div class="max-w-4xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-txt">系统管理</h1>
          <p class="text-txt-dim text-sm mt-1">管理用户账号和密码</p>
        </div>
        <button @click="openCreateModal"
          class="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors">
          <Plus class="w-4 h-4" />
          新增用户
        </button>
      </div>

      <!-- 用户列表 -->
      <div class="glass rounded-xl overflow-hidden">
        <table class="w-full">
          <thead>
            <tr class="border-b border-surface-lighter">
              <th class="text-left px-4 py-3 text-sm font-medium text-txt-muted">用户名</th>
              <th class="text-left px-4 py-3 text-sm font-medium text-txt-muted">角色</th>
              <th class="text-left px-4 py-3 text-sm font-medium text-txt-muted">创建时间</th>
              <th class="text-right px-4 py-3 text-sm font-medium text-txt-muted">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id"
              class="border-b border-surface-lighter/50 hover:bg-surface-lighter/30 transition-colors">
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <UserIcon class="w-4 h-4 text-primary" />
                  </div>
                  <span class="text-sm font-medium text-txt">{{ user.username }}</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <span v-if="user.is_admin"
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400">
                  <Shield class="w-3 h-3" />
                  管理员
                </span>
                <span v-else
                  class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-surface-lighter text-txt-dim">
                  普通用户
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-txt-dim">{{ formatDate(user.created_at) }}</td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="openResetModal(user)"
                    class="p-1.5 rounded-lg text-txt-dim hover:text-primary hover:bg-primary/10 transition-colors"
                    title="重置密码">
                    <KeyRound class="w-4 h-4" />
                  </button>
                  <button @click="confirmDelete(user)"
                    class="p-1.5 rounded-lg text-txt-dim hover:text-danger hover:bg-danger/10 transition-colors"
                    title="删除用户">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="4" class="px-4 py-8 text-center text-txt-dim text-sm">暂无用户</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 新增用户弹窗 -->
      <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="showCreateModal = false">
        <div class="glass-strong rounded-2xl p-6 w-full max-w-sm animate-slide-up">
          <h2 class="text-lg font-bold text-txt mb-4">新增用户</h2>
          <form @submit.prevent="createUser" class="space-y-3">
            <div>
              <label class="block text-sm text-txt-muted mb-1">用户名</label>
              <input v-model="newUser.username" type="text" required minlength="2"
                class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2 text-sm text-txt focus:outline-none focus:border-primary" placeholder="输入用户名" />
            </div>
            <div>
              <label class="block text-sm text-txt-muted mb-1">密码</label>
              <input v-model="newUser.password" type="password" required minlength="6"
                class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2 text-sm text-txt focus:outline-none focus:border-primary" placeholder="至少 6 位" />
            </div>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="newUser.is_admin" type="checkbox"
                class="w-4 h-4 rounded border-surface-lighter bg-surface text-primary focus:ring-primary" />
              <span class="text-sm text-txt">设为管理员</span>
            </label>
            <p v-if="createError" class="text-danger text-sm">{{ createError }}</p>
            <div class="flex gap-2 pt-2">
              <button type="button" @click="showCreateModal = false"
                class="flex-1 py-2 rounded-lg border border-surface-lighter text-sm text-txt-muted hover:text-txt transition-colors">
                取消
              </button>
              <button type="submit" :disabled="createLoading"
                class="flex-1 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-50">
                {{ createLoading ? '创建中...' : '创建' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- 重置密码弹窗 -->
      <div v-if="showResetModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="showResetModal = false">
        <div class="glass-strong rounded-2xl p-6 w-full max-w-sm animate-slide-up">
          <h2 class="text-lg font-bold text-txt mb-1">重置密码</h2>
          <p class="text-sm text-txt-dim mb-4">为用户 <strong class="text-txt">{{ resetTarget?.username }}</strong> 设置新密码</p>
          <form @submit.prevent="resetPassword" class="space-y-3">
            <div>
              <label class="block text-sm text-txt-muted mb-1">新密码</label>
              <input v-model="resetPwd" type="password" required minlength="6"
                class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2 text-sm text-txt focus:outline-none focus:border-primary" placeholder="至少 6 位" />
            </div>
            <p v-if="resetError" class="text-danger text-sm">{{ resetError }}</p>
            <div class="flex gap-2 pt-2">
              <button type="button" @click="showResetModal = false"
                class="flex-1 py-2 rounded-lg border border-surface-lighter text-sm text-txt-muted hover:text-txt transition-colors">
                取消
              </button>
              <button type="submit" :disabled="resetLoading"
                class="flex-1 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-50">
                {{ resetLoading ? '重置中...' : '确认重置' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- 删除确认弹窗 -->
      <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="showDeleteModal = false">
        <div class="glass-strong rounded-2xl p-6 w-full max-w-sm animate-slide-up">
          <h2 class="text-lg font-bold text-txt mb-2">确认删除</h2>
          <p class="text-sm text-txt-dim mb-4">
            确定要删除用户 <strong class="text-txt">{{ deleteTarget?.username }}</strong> 吗？此操作不可撤销。
          </p>
          <div class="flex gap-2">
            <button @click="showDeleteModal = false"
              class="flex-1 py-2 rounded-lg border border-surface-lighter text-sm text-txt-muted hover:text-txt transition-colors">
              取消
            </button>
            <button @click="deleteUser" :disabled="deleteLoading"
              class="flex-1 py-2 rounded-lg bg-danger text-white text-sm font-medium hover:bg-red-600 transition-colors disabled:opacity-50">
              {{ deleteLoading ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, User as UserIcon, Shield, KeyRound, Trash2 } from 'lucide-vue-next'
import api from '../api'

const users = ref([])
const loading = ref(false)

// 新增用户
const showCreateModal = ref(false)
const newUser = ref({ username: '', password: '', is_admin: false })
const createLoading = ref(false)
const createError = ref('')

// 重置密码
const showResetModal = ref(false)
const resetTarget = ref(null)
const resetPwd = ref('')
const resetLoading = ref(false)
const resetError = ref('')

// 删除用户
const showDeleteModal = ref(false)
const deleteTarget = ref(null)
const deleteLoading = ref(false)

onMounted(() => {
  fetchUsers()
})

async function fetchUsers() {
  loading.value = true
  try {
    const res = await api.get('/users')
    users.value = res.data
  } catch (e) {
    console.error('获取用户列表失败:', e)
  }
  loading.value = false
}

function formatDate(isoStr) {
  if (!isoStr) return '-'
  const d = new Date(isoStr)
  return d.toLocaleDateString('zh-CN') + ' ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function openCreateModal() {
  newUser.value = { username: '', password: '', is_admin: false }
  createError.value = ''
  showCreateModal.value = true
}

async function createUser() {
  createError.value = ''
  createLoading.value = true
  try {
    await api.post('/users', newUser.value)
    showCreateModal.value = false
    await fetchUsers()
  } catch (e) {
    createError.value = e.response?.data?.detail || '创建失败'
  }
  createLoading.value = false
}

function openResetModal(user) {
  resetTarget.value = user
  resetPwd.value = ''
  resetError.value = ''
  showResetModal.value = true
}

async function resetPassword() {
  resetError.value = ''
  resetLoading.value = true
  try {
    await api.put(`/users/${resetTarget.value.id}/reset-password`, { new_password: resetPwd.value })
    showResetModal.value = false
  } catch (e) {
    resetError.value = e.response?.data?.detail || '重置失败'
  }
  resetLoading.value = false
}

function confirmDelete(user) {
  deleteTarget.value = user
  showDeleteModal.value = true
}

async function deleteUser() {
  deleteLoading.value = true
  try {
    await api.delete(`/users/${deleteTarget.value.id}`)
    showDeleteModal.value = false
    await fetchUsers()
  } catch (e) {
    console.error('删除失败:', e)
  }
  deleteLoading.value = false
}
</script>

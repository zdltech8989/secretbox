<template>
  <nav class="fixed top-0 left-0 right-0 z-50 glass-strong h-16 flex items-center px-4 lg:px-6">
    <router-link to="/" class="flex items-center gap-2 mr-6">
      <Shield class="w-7 h-7 text-primary" />
      <span class="text-lg font-bold hidden sm:inline bg-gradient-to-r from-primary to-cyan-300 bg-clip-text text-transparent">SecretBox</span>
    </router-link>

    <div class="flex-1 max-w-md mx-2 lg:mx-4">
      <SearchBar @search="handleSearch" />
    </div>

    <div class="flex items-center gap-3">
      <router-link v-if="auth.isAdmin" to="/admin" class="hidden md:flex items-center gap-1 text-txt-muted hover:text-primary transition-colors text-sm">
        <Users class="w-4 h-4" />
        <span>用户管理</span>
      </router-link>
      <router-link to="/import-export" class="hidden md:flex items-center gap-1 text-txt-muted hover:text-primary transition-colors text-sm">
        <Download class="w-4 h-4" />
        <span>导入导出</span>
      </router-link>
      <router-link to="/categories" class="hidden md:flex items-center gap-1 text-txt-muted hover:text-primary transition-colors text-sm">
        <Folder class="w-4 h-4" />
        <span>分类</span>
      </router-link>
      <!-- 锁定保险箱 -->
      <button v-if="auth.vaultUnlocked" @click="auth.lockVault()"
        class="hidden md:flex items-center gap-1 text-txt-muted hover:text-amber-400 transition-colors text-sm"
        title="锁定保险箱">
        <Lock class="w-4 h-4" />
        <span>锁定</span>
      </button>
      <button @click="showChangePwd = true" class="hidden md:flex items-center gap-1 text-txt-muted hover:text-primary transition-colors text-sm"
        title="修改登录密码">
        <Settings class="w-4 h-4" />
      </button>
      <button v-if="auth.vaultUnlocked" @click="showResetMasterPwd = true" class="hidden md:flex items-center gap-1 text-txt-muted hover:text-amber-400 transition-colors text-sm"
        title="重置主密码">
        <KeyRound class="w-4 h-4" />
      </button>
      <!-- 退出登录 -->
      <button @click="handleLogout" class="hidden md:flex items-center gap-1 text-txt-dim hover:text-danger transition-colors text-sm"
        :title="`当前用户: ${auth.currentUser?.username || ''}`">
        <LogOut class="w-4 h-4" />
        <span>退出</span>
      </button>
    </div>

    <ChangePasswordModal v-if="showChangePwd" @close="showChangePwd = false" />
    <ResetMasterPasswordModal v-if="showResetMasterPwd" @close="showResetMasterPwd = false" />
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Shield, Download, Folder, Settings, Users, LogOut, Lock, KeyRound } from 'lucide-vue-next'
import SearchBar from '../components/SearchBar.vue'
import ChangePasswordModal from '../components/ChangePasswordModal.vue'
import ResetMasterPasswordModal from '../components/ResetMasterPasswordModal.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const showChangePwd = ref(false)
const showResetMasterPwd = ref(false)

function handleSearch(keyword) {
  router.push({ name: 'Dashboard', query: { q: keyword } })
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

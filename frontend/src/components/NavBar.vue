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
      <!-- 语言切换 -->
      <button @click="toggleLanguage" class="hidden md:flex items-center gap-1 text-txt-muted hover:text-primary transition-colors text-sm" title="切换语言">
        <Languages class="w-4 h-4" />
        <span>{{ localeText }}</span>
      </button>
      
      <router-link v-if="auth.isAdmin" to="/admin" class="hidden md:flex items-center gap-1 text-txt-muted hover:text-primary transition-colors text-sm">
        <Users class="w-4 h-4" />
        <span>{{ t('nav.manage') }}</span>
      </router-link>
      <router-link to="/import-export" class="hidden md:flex items-center gap-1 text-txt-muted hover:text-primary transition-colors text-sm">
        <Download class="w-4 h-4" />
        <span>{{ t('nav.importExport') }}</span>
      </router-link>
      <router-link to="/categories" class="hidden md:flex items-center gap-1 text-txt-muted hover:text-primary transition-colors text-sm">
        <Folder class="w-4 h-4" />
        <span>{{ t('nav.categories') }}</span>
      </router-link>
      <!-- 锁定保险箱 -->
      <button v-if="auth.vaultUnlocked" @click="auth.lockVault()"
        class="hidden md:flex items-center gap-1 text-txt-muted hover:text-amber-400 transition-colors text-sm"
        :title="t('nav.lockVault')">
        <Lock class="w-4 h-4" />
        <span>{{ t('nav.lock') }}</span>
      </button>
      <button @click="showChangePwd = true" class="hidden md:flex items-center gap-1 text-txt-muted hover:text-primary transition-colors text-sm"
        :title="t('nav.changePwd')">
        <Settings class="w-4 h-4" />
      </button>
      <button v-if="auth.vaultUnlocked" @click="showResetMasterPwd = true" class="hidden md:flex items-center gap-1 text-txt-muted hover:text-amber-400 transition-colors text-sm"
        :title="t('nav.resetMasterPwd')">
        <KeyRound class="w-4 h-4" />
      </button>
      <!-- 退出登录 -->
      <button @click="handleLogout" class="hidden md:flex items-center gap-1 text-txt-dim hover:text-danger transition-colors text-sm"
        :title="t('nav.logoutConfirm', { username: auth.currentUser?.username || '' })">
        <LogOut class="w-4 h-4" />
        <span>{{ t('nav.logout') }}</span>
      </button>
    </div>

    <ChangePasswordModal v-if="showChangePwd" @close="showChangePwd = false" />
    <ResetMasterPasswordModal v-if="showResetMasterPwd" @close="showResetMasterPwd = false" />
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Shield, Download, Folder, Settings, Users, LogOut, Lock, KeyRound, Languages } from 'lucide-vue-next'
import SearchBar from '../components/SearchBar.vue'
import ChangePasswordModal from '../components/ChangePasswordModal.vue'
import ResetMasterPasswordModal from '../components/ResetMasterPasswordModal.vue'
import { useAuthStore } from '../stores/auth'
import { useI18n } from '../i18n'

const router = useRouter()
const auth = useAuthStore()
const { t, setLocale, locale } = useI18n()
const showChangePwd = ref(false)
const showResetMasterPwd = ref(false)

const localeText = computed(() => locale() === 'zh-CN' ? '中文' : 'English')

function toggleLanguage() {
  setLocale(locale() === 'zh-CN' ? 'en' : 'zh-CN')
}

function handleSearch(keyword) {
  router.push({ name: 'Dashboard', query: { q: keyword } })
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

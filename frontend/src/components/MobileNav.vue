<template>
  <nav class="fixed bottom-0 left-0 right-0 z-50 glass-strong md:hidden flex items-center justify-around h-16 border-t border-surface-lighter">
    <router-link to="/" class="flex flex-col items-center gap-0.5 text-txt-dim hover:text-primary transition-colors p-2">
      <Home class="w-5 h-5" />
      <span class="text-[10px]">{{ t('mobile.secrets') }}</span>
    </router-link>
    <router-link to="/categories" class="flex flex-col items-center gap-0.5 text-txt-dim hover:text-primary transition-colors p-2">
      <Folder class="w-5 h-5" />
      <span class="text-[10px]">{{ t('mobile.categories') }}</span>
    </router-link>
    <button @click="$router.push('/secret/new')" class="flex flex-col items-center justify-center w-12 h-12 -mt-4 rounded-full bg-primary text-white shadow-lg shadow-primary/30 animate-pulse-glow">
      <Plus class="w-6 h-6" />
    </button>
    <router-link v-if="auth.isAdmin" to="/admin" class="flex flex-col items-center gap-0.5 text-txt-dim hover:text-primary transition-colors p-2">
      <Users class="w-5 h-5" />
      <span class="text-[10px]">{{ t('mobile.manage') }}</span>
    </router-link>
    <router-link v-else to="/import-export" class="flex flex-col items-center gap-0.5 text-txt-dim hover:text-primary transition-colors p-2">
      <Download class="w-5 h-5" />
      <span class="text-[10px]">{{ t('mobile.importExport') }}</span>
    </router-link>
    <button @click="showMobileMenu = true" class="flex flex-col items-center gap-0.5 text-txt-dim hover:text-primary transition-colors p-2">
      <MoreHorizontal class="w-5 h-5" />
      <span class="text-[10px]">{{ t('mobile.more') }}</span>
    </button>
  </nav>

  <!-- 移动端更多菜单 -->
  <div v-if="showMobileMenu" class="fixed inset-0 z-[60] md:hidden" @click.self="showMobileMenu = false">
    <div class="absolute inset-0 bg-black/40" />
    <div class="absolute bottom-16 left-2 right-2 glass-strong rounded-2xl p-2 animate-slide-up">
      <button v-if="auth.vaultUnlocked" @click="showMobileMenu = false; auth.lockVault()"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-amber-400 hover:bg-surface-lighter transition-colors">
        <Lock class="w-5 h-5" />
        <span>{{ t('nav.lockVault') }}</span>
      </button>
      <button @click="showMobileMenu = false; toggleLanguage"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-txt-muted hover:bg-surface-lighter transition-colors">
        <Languages class="w-5 h-5" />
        <span>{{ locale() === 'zh-CN' ? 'English' : '中文' }}</span>
      </button>
      <button @click="showMobileMenu = false; showChangePwd = true"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-txt-muted hover:bg-surface-lighter transition-colors">
        <Settings class="w-5 h-5" />
        <span>{{ t('nav.changePwd') }}</span>
      </button>
      <button v-if="auth.vaultUnlocked" @click="showMobileMenu = false; showResetMasterPwd = true"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-amber-400 hover:bg-surface-lighter transition-colors">
        <KeyRound class="w-5 h-5" />
        <span>{{ t('nav.resetMasterPwd') }}</span>
      </button>
      <button @click="showMobileMenu = false; handleLogout()"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-danger hover:bg-surface-lighter transition-colors">
        <LogOut class="w-5 h-5" />
        <span>{{ t('nav.logout') }}</span>
      </button>
    </div>
  </div>

  <ChangePasswordModal v-if="showChangePwd" @close="showChangePwd = false" />
  <ResetMasterPasswordModal v-if="showResetMasterPwd" @close="showResetMasterPwd = false" />
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Home, Folder, Plus, Download, Settings, Users, LogOut, Lock, MoreHorizontal, KeyRound, Languages } from 'lucide-vue-next'
import ChangePasswordModal from './ChangePasswordModal.vue'
import ResetMasterPasswordModal from './ResetMasterPasswordModal.vue'
import { useAuthStore } from '../stores/auth'
import { useI18n } from '../i18n'

const router = useRouter()
const auth = useAuthStore()
const { t, setLocale, locale } = useI18n()
const showChangePwd = ref(false)
const showResetMasterPwd = ref(false)
const showMobileMenu = ref(false)

function toggleLanguage() {
  setLocale(locale() === 'zh-CN' ? 'en' : 'zh-CN')
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

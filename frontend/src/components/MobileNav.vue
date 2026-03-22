<template>
  <nav class="fixed bottom-0 left-0 right-0 z-50 glass-strong md:hidden flex items-center justify-around h-16 border-t border-surface-lighter">
    <router-link to="/" class="flex flex-col items-center gap-0.5 text-txt-dim hover:text-primary transition-colors p-2">
      <Home class="w-5 h-5" />
      <span class="text-[10px]">密钥</span>
    </router-link>
    <router-link to="/categories" class="flex flex-col items-center gap-0.5 text-txt-dim hover:text-primary transition-colors p-2">
      <Folder class="w-5 h-5" />
      <span class="text-[10px]">分类</span>
    </router-link>
    <button @click="$router.push('/secret/new')" class="flex flex-col items-center justify-center w-12 h-12 -mt-4 rounded-full bg-primary text-white shadow-lg shadow-primary/30 animate-pulse-glow">
      <Plus class="w-6 h-6" />
    </button>
    <router-link v-if="auth.isAdmin" to="/admin" class="flex flex-col items-center gap-0.5 text-txt-dim hover:text-primary transition-colors p-2">
      <Users class="w-5 h-5" />
      <span class="text-[10px]">管理</span>
    </router-link>
    <router-link v-else to="/import-export" class="flex flex-col items-center gap-0.5 text-txt-dim hover:text-primary transition-colors p-2">
      <Download class="w-5 h-5" />
      <span class="text-[10px]">导入导出</span>
    </router-link>
    <button @click="showMobileMenu = true" class="flex flex-col items-center gap-0.5 text-txt-dim hover:text-primary transition-colors p-2">
      <MoreHorizontal class="w-5 h-5" />
      <span class="text-[10px]">更多</span>
    </button>
  </nav>

  <!-- 移动端更多菜单 -->
  <div v-if="showMobileMenu" class="fixed inset-0 z-[60] md:hidden" @click.self="showMobileMenu = false">
    <div class="absolute inset-0 bg-black/40" />
    <div class="absolute bottom-16 left-2 right-2 glass-strong rounded-2xl p-2 animate-slide-up">
      <button v-if="auth.vaultUnlocked" @click="showMobileMenu = false; auth.lockVault()"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-amber-400 hover:bg-surface-lighter transition-colors">
        <Lock class="w-5 h-5" />
        <span>锁定保险箱</span>
      </button>
      <button @click="showMobileMenu = false; showChangePwd = true"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-txt-muted hover:bg-surface-lighter transition-colors">
        <Settings class="w-5 h-5" />
        <span>修改登录密码</span>
      </button>
      <button v-if="auth.vaultUnlocked" @click="showMobileMenu = false; showResetMasterPwd = true"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-amber-400 hover:bg-surface-lighter transition-colors">
        <KeyRound class="w-5 h-5" />
        <span>重置主密码</span>
      </button>
      <button @click="showMobileMenu = false; handleLogout()"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-danger hover:bg-surface-lighter transition-colors">
        <LogOut class="w-5 h-5" />
        <span>退出登录</span>
      </button>
    </div>
  </div>

  <ChangePasswordModal v-if="showChangePwd" @close="showChangePwd = false" />
  <ResetMasterPasswordModal v-if="showResetMasterPwd" @close="showResetMasterPwd = false" />
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Home, Folder, Plus, Download, Settings, Users, LogOut, Lock, MoreHorizontal, KeyRound } from 'lucide-vue-next'
import ChangePasswordModal from './ChangePasswordModal.vue'
import ResetMasterPasswordModal from './ResetMasterPasswordModal.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const showChangePwd = ref(false)
const showResetMasterPwd = ref(false)
const showMobileMenu = ref(false)

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="fixed inset-0 z-[70] bg-gradient-to-br from-surface via-surface to-slate-900 flex items-center justify-center p-4">
    <div class="glass-strong rounded-2xl p-8 w-full max-w-md animate-slide-up">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 mb-4">
          <Lock v-if="!isSetup" class="w-8 h-8 text-primary" />
          <ShieldCheck v-else class="w-8 h-8 text-primary" />
        </div>
        <h2 v-if="isSetup" class="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-300 bg-clip-text text-transparent">设置主密码</h2>
        <h2 v-else class="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-300 bg-clip-text text-transparent">保险箱已锁定</h2>
        <p class="text-txt-dim text-sm mt-2">{{ isSetup ? '首次使用，请设置主密码用于加密密钥' : '输入主密码以解锁加密密钥' }}</p>
        <p v-if="auth.currentUser" class="text-txt-dim text-xs mt-1">
          当前用户: {{ auth.currentUser.username }}
        </p>
      </div>

      <!-- 设置主密码 -->
      <form v-if="isSetup" @submit.prevent="submitSetup" class="space-y-4">
        <div>
          <label class="block text-sm text-txt-muted mb-1">设置主密码</label>
          <div class="relative">
            <KeyRound class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-txt-dim" />
            <input v-model="setupPwd" type="password" required minlength="8"
              class="w-full bg-surface border border-surface-lighter rounded-lg pl-10 pr-4 py-2.5 text-sm text-txt focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50"
              placeholder="至少 8 位字符" />
          </div>
        </div>
        <div>
          <label class="block text-sm text-txt-muted mb-1">确认密码</label>
          <div class="relative">
            <KeyRound class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-txt-dim" />
            <input v-model="confirmPwd" type="password" required minlength="8"
              class="w-full bg-surface border border-surface-lighter rounded-lg pl-10 pr-4 py-2.5 text-sm text-txt focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50"
              placeholder="再次输入密码" />
          </div>
        </div>

        <p v-if="errMsg" class="text-danger text-sm">{{ errMsg }}</p>

        <button type="submit" :disabled="loading"
          class="w-full py-2.5 rounded-lg bg-gradient-to-r from-primary to-cyan-500 text-white font-medium hover:from-primary-dark hover:to-cyan-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
          {{ loading ? '创建中...' : '创建保险箱' }}
        </button>
      </form>

      <!-- 解锁主密码 -->
      <form v-else @submit.prevent="submitUnlock" class="space-y-4">
        <div>
          <label class="block text-sm text-txt-muted mb-1">主密码</label>
          <div class="relative">
            <KeyRound class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-txt-dim" />
            <input v-model="masterPwd" type="password" required
              class="w-full bg-surface border border-surface-lighter rounded-lg pl-10 pr-4 py-2.5 text-sm text-txt focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50"
              placeholder="输入主密码" autofocus />
          </div>
        </div>

        <p v-if="errMsg" class="text-danger text-sm">{{ errMsg }}</p>

        <button type="submit" :disabled="loading"
          class="w-full py-2.5 rounded-lg bg-gradient-to-r from-primary to-cyan-500 text-white font-medium hover:from-primary-dark hover:to-cyan-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
          {{ loading ? '解锁中...' : '解锁保险箱' }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <button @click="handleLogout" class="text-txt-dim text-xs hover:text-danger transition-colors">
          退出登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Lock, ShieldCheck, KeyRound } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  isSetup: { type: Boolean, default: false },
})

const router = useRouter()
const auth = useAuthStore()

const masterPwd = ref('')
const setupPwd = ref('')
const confirmPwd = ref('')
const errMsg = ref('')
const loading = ref(false)

async function submitSetup() {
  errMsg.value = ''
  if (setupPwd.value !== confirmPwd.value) {
    errMsg.value = '两次输入的密码不一致'
    return
  }
  loading.value = true
  try {
    await auth.setupVault(setupPwd.value)
  } catch (e) {
    errMsg.value = e.response?.data?.detail || '设置失败'
  }
  loading.value = false
}

async function submitUnlock() {
  errMsg.value = ''
  loading.value = true
  try {
    await auth.unlockVault(masterPwd.value)
  } catch (e) {
    errMsg.value = e.response?.data?.detail || '解锁失败'
  }
  loading.value = false
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

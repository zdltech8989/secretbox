<template>
  <div class="min-h-screen bg-gradient-to-br from-surface via-surface to-slate-900 flex items-center justify-center p-4">
    <div class="glass-strong rounded-2xl p-8 w-full max-w-md animate-slide-up">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 mb-4 animate-pulse-glow">
          <Shield class="w-8 h-8 text-primary" />
        </div>
        <h1 class="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-300 bg-clip-text text-transparent">SecretBox</h1>
        <p class="text-txt-dim text-sm mt-1">输入用户名和密码登录</p>
      </div>

      <form @submit.prevent="submitLogin" class="space-y-4">
        <div>
          <label class="block text-sm text-txt-muted mb-1">用户名</label>
          <div class="relative">
            <UserIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-txt-dim" />
            <input v-model="username" type="text" required autocomplete="username"
              class="w-full bg-surface border border-surface-lighter rounded-lg pl-10 pr-4 py-2.5 text-sm text-txt focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50" placeholder="输入用户名" />
          </div>
        </div>
        <div>
          <label class="block text-sm text-txt-muted mb-1">密码</label>
          <div class="relative">
            <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-txt-dim" />
            <input v-model="password" type="password" required autocomplete="current-password"
              class="w-full bg-surface border border-surface-lighter rounded-lg pl-10 pr-4 py-2.5 text-sm text-txt focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50" placeholder="输入密码" />
          </div>
        </div>

        <p v-if="error" class="text-danger text-sm">{{ error }}</p>

        <button type="submit" :disabled="loading"
          class="w-full py-2.5 rounded-lg bg-gradient-to-r from-primary to-cyan-500 text-white font-medium hover:from-primary-dark hover:to-cyan-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <p class="text-center text-txt-dim text-xs mt-6">SecretBox v1.0 - Developer Secret Vault</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Shield, Lock, User as UserIcon } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submitLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  }
  loading.value = false
}
</script>

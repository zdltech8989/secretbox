<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[80] flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="$emit('close')">
      <div class="glass-strong rounded-2xl p-6 w-full max-w-sm mx-4 animate-slide-up">
      <div class="flex items-center gap-2 mb-4">
        <KeyRound class="w-5 h-5 text-amber-400" />
        <h3 class="text-lg font-bold text-txt">重置主密码</h3>
      </div>
      <p class="text-xs text-txt-dim mb-4">重置主密码将使用新密码重新加密所有已存储的密钥，请确保牢记新密码。</p>
      <form @submit.prevent="submit">
        <label class="block text-sm text-txt-muted mb-1">当前主密码</label>
        <input v-model="oldPwd" type="password" required
          class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2 text-sm text-txt focus:outline-none focus:border-primary mb-3" />
        <label class="block text-sm text-txt-muted mb-1">新主密码</label>
        <input v-model="newPwd" type="password" required minlength="8"
          class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2 text-sm text-txt focus:outline-none focus:border-primary mb-3"
          placeholder="至少 8 位字符" />
        <label class="block text-sm text-txt-muted mb-1">确认新主密码</label>
        <input v-model="confirmPwd" type="password" required minlength="8"
          class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2 text-sm text-txt focus:outline-none focus:border-primary mb-4"
          placeholder="再次输入新密码" />
        <p v-if="errMsg" class="text-danger text-xs mb-3">{{ errMsg }}</p>
        <div class="flex gap-3">
          <button type="button" @click="$emit('close')"
            class="flex-1 py-2 rounded-lg border border-surface-lighter text-txt-muted hover:text-txt transition-colors text-sm">取消</button>
          <button type="submit" :disabled="saving"
            class="flex-1 py-2 rounded-lg bg-amber-500 text-white hover:bg-amber-600 transition-colors text-sm disabled:opacity-50">
            {{ saving ? '重置中...' : '确认重置' }}
          </button>
        </div>
      </form>
    </div>
  </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { KeyRound } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const emit = defineEmits(['close'])
const auth = useAuthStore()

const oldPwd = ref('')
const newPwd = ref('')
const confirmPwd = ref('')
const errMsg = ref('')
const saving = ref(false)

async function submit() {
  errMsg.value = ''
  if (newPwd.value !== confirmPwd.value) { errMsg.value = '两次输入的新密码不一致'; return }
  saving.value = true
  try {
    await auth.resetMasterPassword(oldPwd.value, newPwd.value)
    emit('close')
  } catch (e) {
    errMsg.value = e.response?.data?.detail || '重置失败'
  }
  saving.value = false
}
</script>

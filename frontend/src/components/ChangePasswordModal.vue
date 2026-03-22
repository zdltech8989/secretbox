<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[80] flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="$emit('close')">
      <div class="glass-strong rounded-2xl p-6 w-full max-w-sm mx-4 animate-slide-up">
        <h3 class="text-lg font-bold text-txt mb-4">修改登录密码</h3>
      <form @submit.prevent="submit">
        <label class="block text-sm text-txt-muted mb-1">当前密码</label>
        <input v-model="oldPwd" type="password" required
          class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2 text-sm text-txt focus:outline-none focus:border-primary mb-3" />
        <label class="block text-sm text-txt-muted mb-1">新密码</label>
        <input v-model="newPwd" type="password" required minlength="8"
          class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2 text-sm text-txt focus:outline-none focus:border-primary mb-3" />
        <label class="block text-sm text-txt-muted mb-1">确认新密码</label>
        <input v-model="confirmPwd" type="password" required minlength="8"
          class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2 text-sm text-txt focus:outline-none focus:border-primary mb-4" />
        <p v-if="errMsg" class="text-danger text-xs mb-3">{{ errMsg }}</p>
        <div class="flex gap-3">
          <button type="button" @click="$emit('close')"
            class="flex-1 py-2 rounded-lg border border-surface-lighter text-txt-muted hover:text-txt transition-colors text-sm">取消</button>
          <button type="submit" :disabled="saving"
            class="flex-1 py-2 rounded-lg bg-primary text-white hover:bg-primary-dark transition-colors text-sm disabled:opacity-50">
            {{ saving ? '保存中...' : '确认修改' }}
          </button>
        </div>
      </form>
    </div>
  </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
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
    await auth.changePassword(oldPwd.value, newPwd.value)
    emit('close')
  } catch (e) {
    errMsg.value = e.response?.data?.detail || '修改失败'
  }
  saving.value = false
}
</script>

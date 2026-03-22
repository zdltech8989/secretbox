<template>
  <div class="bg-surface-light rounded-xl border border-surface-lighter p-4 hover:border-primary/30 transition-all group animate-fade-in">
    <div class="flex items-start justify-between">
      <div class="flex-1 min-w-0 cursor-pointer" @click="expanded = !expanded">
        <div class="flex items-center gap-2 mb-1">
          <span class="text-txt font-medium truncate">{{ secret.name }}</span>
          <span v-if="categoryName" class="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">{{ categoryName }}</span>
        </div>
        <div v-if="secret.remark" class="text-txt-dim text-xs truncate">{{ secret.remark }}</div>
      </div>

      <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          @click="copyValue"
          class="p-1.5 rounded-lg hover:bg-primary/10 text-txt-dim hover:text-primary transition-colors"
          :title="t('secret.copy')"
        >
          <Copy v-if="!copied" class="w-4 h-4" />
          <Check v-else class="w-4 h-4 text-success" />
        </button>
        <router-link
          :to="{ name: 'SecretEdit', params: { id: secret.id } }"
          class="p-1.5 rounded-lg hover:bg-primary/10 text-txt-dim hover:text-primary transition-colors"
          :title="t('common.edit')"
        >
          <Edit class="w-4 h-4" />
        </router-link>
        <button
          @click="$emit('delete', secret.id)"
          class="p-1.5 rounded-lg hover:bg-danger/10 text-txt-dim hover:text-danger transition-colors"
          :title="t('common.delete')"
        >
          <Trash class="w-4 h-4" />
        </button>
      </div>
    </div>

    <div v-if="expanded && secret.url" class="mt-2 text-xs text-primary/70 truncate">
      <Globe class="w-3 h-3 inline mr-1" />{{ secret.url }}
    </div>

    <div v-if="expanded && decryptedValue" class="mt-3 animate-fade-in">
      <div class="flex items-center justify-between bg-surface rounded-lg p-3">
        <code class="text-sm text-primary break-all select-all flex-1">{{ showValue ? decryptedValue : '••••••••••••' }}</code>
        <button @click="showValue = !showValue" class="ml-2 text-txt-dim hover:text-txt transition-colors">
          <Eye v-if="!showValue" class="w-4 h-4" />
          <EyeOff v-else class="w-4 h-4" />
        </button>
      </div>
      <div v-if="secret.notes" class="mt-2 text-xs text-txt-muted bg-surface rounded-lg p-2">
        <span class="text-txt-dim font-medium">备注: </span>{{ secret.notes }}
      </div>
    </div>

    <div v-if="expanded && !decryptedValue && !loading && !loadError && !needUnlock" class="mt-2">
      <button @click="loadValue" class="text-xs text-primary hover:text-primary-dark transition-colors">
        {{ t('secret.showValue') }}
      </button>
    </div>
    <div v-if="expanded && loadError" class="mt-2 text-xs text-danger">
      {{ loadError }}
    </div>
    <div v-if="expanded && needUnlock" class="mt-2 animate-fade-in">
      <div class="flex items-center gap-2">
        <input v-model="unlockPwd" type="password" placeholder="输入主密码"
          @keyup.enter="doInlineUnlock"
          class="flex-1 bg-surface border border-surface-lighter rounded-lg px-3 py-1.5 text-xs text-txt focus:outline-none focus:border-primary" />
        <button @click="doInlineUnlock" :disabled="unlocking"
          class="px-3 py-1.5 rounded-lg bg-primary/10 text-primary text-xs hover:bg-primary/20 transition-colors disabled:opacity-50">
          {{ unlocking ? t('common.loading') + '...' : t('unlock.unlockBtn') }}
        </button>
        <button @click="needUnlock = false" class="text-xs text-txt-dim hover:text-txt">{{ t('common.cancel') }}</button>
      </div>
      <p v-if="unlockError" class="mt-1 text-xs text-danger">{{ unlockError }}</p>
    </div>
    <div v-if="loading" class="mt-2 text-xs text-txt-dim animate-pulse">{{ t('common.loading') }}...</div>

    <div class="mt-2 text-xs text-txt-dim">
      {{ formatDate(secret.updated_at || secret.created_at) }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Copy, Check, Edit, Trash, Eye, EyeOff, Globe } from 'lucide-vue-next'
import { useSecretsStore } from '../stores/secrets'
import { useAuthStore } from '../stores/auth'
import { useI18n } from '../i18n'

const props = defineProps({
  secret: { type: Object, required: true },
  categoryName: { type: String, default: '' },
})
defineEmits(['delete'])

const store = useSecretsStore()
const auth = useAuthStore()
const { t, locale } = useI18n()
const expanded = ref(false)
const decryptedValue = ref('')
const showValue = ref(false)
const copied = ref(false)
const loading = ref(false)
const loadError = ref('')
const needUnlock = ref(false)
const unlockPwd = ref('')
const unlocking = ref(false)
const unlockError = ref('')

async function loadValue() {
  loading.value = true
  loadError.value = ''
  needUnlock.value = false
  try {
    const data = await store.fetchSecret(props.secret.id)
    decryptedValue.value = data.value
    if (data.notes) props.secret.notes = data.notes
  } catch (e) {
    const detail = e.response?.data?.detail || t('common.error')
    if (detail.toLowerCase().includes('unlock') || detail.toLowerCase().includes('encrypt') || detail.includes('解锁')) {
      needUnlock.value = true
    } else {
      loadError.value = detail
    }
  }
  loading.value = false
}

async function doInlineUnlock() {
  if (!unlockPwd.value) return
  unlocking.value = true
  unlockError.value = ''
  try {
    await auth.unlockVault(unlockPwd.value)
    unlockPwd.value = ''
    needUnlock.value = false
    await loadValue()
  } catch (e) {
    unlockError.value = e.response?.data?.detail || t('unlock.unlockFailed')
  } finally {
    unlocking.value = false
  }
}

async function copyValue() {
  if (!decryptedValue.value) {
    await loadValue()
  }
  const text = decryptedValue.value
  try {
    await navigator.clipboard.writeText(text)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  } catch {
    console.error('Copy failed')
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const lang = locale()
  return d.toLocaleDateString(lang === 'zh-CN' ? 'zh-CN' : 'en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

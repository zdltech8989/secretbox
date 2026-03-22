<template>
  <div class="pt-16 pb-20 md:pb-0 min-h-screen bg-surface">
    <div class="max-w-2xl mx-auto p-4 lg:p-6">
      <h2 class="text-xl font-bold text-txt mb-6">{{ t('importExport.title') }}</h2>

      <!-- Export Section -->
      <div class="glass-strong rounded-2xl p-6 mb-4">
        <h3 class="text-lg font-semibold text-txt mb-4 flex items-center gap-2">
          <Upload class="w-5 h-5 text-primary" />{{ t('importExport.export') }}
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button @click="handleExportCsv"
            class="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-surface-light border border-surface-lighter hover:border-primary/30 transition-all text-sm text-txt-muted hover:text-txt">
            <FileText class="w-4 h-4" />{{ t('importExport.exportCsv') }}
          </button>
          <button @click="handleExportJson"
            class="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-surface-light border border-surface-lighter hover:border-primary/30 transition-all text-sm text-txt-muted hover:text-txt">
            <FileJson class="w-4 h-4" />{{ t('importExport.exportJson') }}
          </button>
        </div>
      </div>

      <!-- Import Section -->
      <div class="glass-strong rounded-2xl p-6">
        <h3 class="text-lg font-semibold text-txt mb-4 flex items-center gap-2">
          <Download class="w-5 h-5 text-primary" />{{ t('importExport.import') }}
        </h3>
        <p class="text-sm text-txt-dim mb-4">{{ t('importExport.importHint') }}</p>

        <div @dragover.prevent="dragOver = true" @dragleave="dragOver = false" @drop.prevent="handleDrop"
          :class="['border-2 border-dashed rounded-xl p-8 text-center transition-all', dragOver ? 'border-primary bg-primary/5' : 'border-surface-lighter hover:border-txt-dim']">
          <UploadCloud class="w-10 h-10 text-txt-dim mx-auto mb-3" />
          <p class="text-sm text-txt-muted mb-2">{{ t('importExport.dragHint') }}</p>
          <label class="inline-flex items-center gap-1 text-sm text-primary hover:text-primary-dark cursor-pointer">
            <FileUp class="w-4 h-4" />{{ t('importExport.clickHint') }}
            <input type="file" accept=".csv" class="hidden" @change="handleFileSelect" />
          </label>
        </div>

        <div v-if="file" class="mt-4 p-3 rounded-lg bg-surface-light flex items-center justify-between">
          <span class="text-sm text-txt-muted truncate">{{ file.name }}</span>
          <button @click="file = null" class="text-txt-dim hover:text-danger ml-2">
            <X class="w-4 h-4" />
          </button>
        </div>

        <div v-if="file" class="mt-3">
          <label class="block text-sm text-txt-muted mb-1">{{ t('importExport.importCategory') }}</label>
          <select v-model="importCategory"
            class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2 text-sm text-txt focus:outline-none focus:border-primary">
            <option v-for="cat in categories" :key="cat.id" :value="cat.name">{{ cat.name }}</option>
          </select>
        </div>

        <div v-if="file" class="mt-4">
          <button @click="handleImport" :disabled="importing"
            class="w-full py-2.5 rounded-lg bg-primary text-white font-medium hover:bg-primary-dark transition-colors text-sm disabled:opacity-50">
            {{ importing ? t('importExport.importing') : t('importExport.startImport') }}
          </button>
        </div>
      </div>

      <!-- 导入结果 Toast -->
      <div v-if="importResult" class="fixed top-20 left-1/2 -translate-x-1/2 z-[80] px-6 py-3 rounded-xl shadow-lg animate-slide-up text-sm"
        :class="importResult.error ? 'bg-danger/90 text-white' : 'bg-success/90 text-white'">
        {{ importResult.message || importResult.error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Upload, Download, FileText, FileJson, UploadCloud, FileUp, X } from 'lucide-vue-next'
import { useSecretsStore } from '../stores/secrets'
import { useAuthStore } from '../stores/auth'
import { useI18n } from '../i18n'

const store = useSecretsStore()
const auth = useAuthStore()
const { t } = useI18n()
const categories = computed(() => store.categories)
const dragOver = ref(false)
const file = ref(null)
const importCategory = ref(t('nav.categories'))
const importing = ref(false)
const importResult = ref(null)

onMounted(() => {
  if (auth.vaultUnlocked) {
    store.fetchCategories()
  }
})

watch(() => auth.vaultUnlocked, (unlocked) => {
  if (unlocked) {
    store.fetchCategories()
  }
})

async function handleExportCsv() {
  try { await store.exportCsv() } catch (e) { console.error(e) }
}

async function handleExportJson() {
  try { await store.exportJson() } catch (e) { console.error(e) }
}

function handleDrop(e) {
  dragOver.value = false
  const f = e.dataTransfer.files[0]
  if (f && f.name.endsWith('.csv')) file.value = f
}

function handleFileSelect(e) {
  const f = e.target.files[0]
  if (f) file.value = f
}

async function handleImport() {
  if (!file.value) return

  // 检查后端解锁状态
  await auth.checkVaultStatus()
  if (!auth.vaultUnlocked) {
    importResult.value = { error: t('unlock.unlockFailed') }
    setTimeout(() => { importResult.value = null }, 3000)
    return
  }

  importResult.value = null
  importing.value = true
  try {
    // 保险箱已解锁，后端会使用缓存的密钥，不需要传递主密码
    const res = await store.importCsv(file.value, null, importCategory.value)
    importResult.value = res
    file.value = null
    store.fetchSecrets()
    store.fetchCategories()
    setTimeout(() => { importResult.value = null }, 3000)
  } catch (e) {
    importResult.value = { error: e.response?.data?.detail || t('importExport.importFailed', { error: '未知错误' }) }
    setTimeout(() => { importResult.value = null }, 5000)
  }
  importing.value = false
}
</script>

<template>
  <div class="pt-16 pb-20 md:pb-0 min-h-screen bg-surface">
    <div class="max-w-2xl mx-auto p-4 lg:p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-bold text-txt">{{ t('categories.title') }}</h2>
        <button @click="showAdd = true"
          class="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors">
          <Plus class="w-4 h-4" />{{ t('categories.add') }}
        </button>
      </div>

      <div class="glass-strong rounded-2xl overflow-hidden">
        <div v-for="cat in categories" :key="cat.id"
          class="flex items-center justify-between px-5 py-4 border-b border-surface-lighter last:border-b-0 hover:bg-surface-light/50 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
              <Tag class="w-4 h-4 text-primary" />
            </div>
            <div>
              <p class="text-sm font-medium text-txt">{{ cat.name }}</p>
              <p class="text-xs text-txt-dim">{{ cat.secret_count }} {{ t('dashboard.allSecrets').replace('全部密钥', '') }}</p>
            </div>
          </div>
          <button @click="handleDelete(cat.id, cat.name)"
            class="p-2 rounded-lg hover:bg-danger/10 text-txt-dim hover:text-danger transition-colors">
            <Trash class="w-4 h-4" />
          </button>
        </div>
      </div>

      <div v-if="categories.length === 0" class="text-center py-12">
        <Tag class="w-12 h-12 text-txt-dim mx-auto mb-3 opacity-30" />
        <p class="text-txt-muted text-sm">{{ t('categories.noCategories') }}</p>
      </div>
    </div>

    <!-- Add Category Modal -->
    <div v-if="showAdd" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="showAdd = false">
      <div class="glass-strong rounded-2xl p-6 w-full max-w-sm mx-4 animate-slide-up">
        <h3 class="text-lg font-bold text-txt mb-4">{{ t('categories.add') }}</h3>
        <input v-model="newName" type="text" :placeholder="t('categories.namePlaceholder')"
          class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2.5 text-sm text-txt focus:outline-none focus:border-primary mb-4" />
        <div class="flex gap-3">
          <button @click="showAdd = false" class="flex-1 py-2 rounded-lg border border-surface-lighter text-txt-muted hover:text-txt text-sm">{{ t('common.cancel') }}</button>
          <button @click="handleAdd" class="flex-1 py-2 rounded-lg bg-primary text-white text-sm hover:bg-primary-dark">{{ t('common.add') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, Tag, Trash } from 'lucide-vue-next'
import { useSecretsStore } from '../stores/secrets'
import { useAuthStore } from '../stores/auth'
import { useI18n } from '../i18n'

const store = useSecretsStore()
const auth = useAuthStore()
const { t } = useI18n()
const categories = computed(() => store.categories)
const showAdd = ref(false)
const newName = ref('')

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

async function handleAdd() {
  if (!newName.value.trim()) return
  await store.createCategory(newName.value.trim())
  newName.value = ''
  showAdd.value = false
}

async function handleDelete(id, name) {
  if (confirm(t('categories.deleteConfirm', { name }))) {
    await store.deleteCategory(id)
  }
}
</script>

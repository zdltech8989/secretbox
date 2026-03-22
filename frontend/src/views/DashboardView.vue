<template>
  <div class="pt-16 pb-20 md:pb-0 min-h-screen bg-surface">
    <div class="flex">
      <!-- Sidebar (Desktop) -->
      <aside class="hidden md:block w-60 fixed top-16 left-0 bottom-0 bg-surface-light border-r border-surface-lighter overflow-y-auto p-4">
        <h3 class="text-xs font-semibold text-txt-dim uppercase tracking-wider mb-3">{{ t('nav.categories') }}</h3>
        <div class="space-y-1">
          <button @click="selectCategory(null)"
            :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-colors', !activeCategory ? 'bg-primary/10 text-primary' : 'text-txt-muted hover:text-txt hover:bg-surface']">
            <Key class="w-4 h-4 inline mr-2" />{{ t('dashboard.allSecrets') }}
          </button>
          <button v-for="cat in categories" :key="cat.id" @click="selectCategory(cat.id)"
            :class="['w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between', activeCategory === cat.id ? 'bg-primary/10 text-primary' : 'text-txt-muted hover:text-txt hover:bg-surface']">
            <span><Tag class="w-4 h-4 inline mr-2" />{{ cat.name }}</span>
            <span class="text-xs opacity-50">{{ cat.secret_count }}</span>
          </button>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 md:ml-60 p-4 lg:p-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-xl font-bold text-txt">
              {{ activeCategoryName }}
            </h2>
            <p class="text-txt-dim text-sm mt-1">{{ t('dashboard.totalRecords', { count: secrets.length }) }}</p>
          </div>
          <router-link to="/secret/new"
            class="hidden md:flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors">
            <Plus class="w-4 h-4" />{{ t('dashboard.addSecret') }}
          </router-link>
        </div>

        <div v-if="loading" class="flex items-center justify-center py-20">
          <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
        </div>

        <div v-else-if="secrets.length === 0" class="text-center py-20">
          <Key class="w-12 h-12 text-txt-dim mx-auto mb-4 opacity-30" />
          <p class="text-txt-muted">{{ t('dashboard.noSecrets') }}</p>
          <router-link to="/secret/new" class="text-primary text-sm mt-2 inline-block hover:underline">{{ t('dashboard.addFirstSecret') }}</router-link>
        </div>

        <div v-else class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-3">
          <SecretCard
            v-for="s in secrets" :key="s.id"
            :secret="s"
            :category-name="getCategoryName(s.category_id)"
            @delete="handleDelete"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Key, Tag, Plus } from 'lucide-vue-next'
import SecretCard from '../components/SecretCard.vue'
import { useSecretsStore } from '../stores/secrets'
import { useAuthStore } from '../stores/auth'
import { useI18n } from '../i18n'

const route = useRoute()
const router = useRouter()
const store = useSecretsStore()
const auth = useAuthStore()
const { t } = useI18n()

const activeCategory = ref(null)
const loading = computed(() => store.loading)
const secrets = computed(() => store.secrets)
const categories = computed(() => store.categories)

const activeCategoryName = computed(() => {
  if (!activeCategory.value) return t('dashboard.allSecrets')
  const cat = categories.value.find(c => c.id === activeCategory.value)
  return cat ? cat.name : ''
})

function getCategoryName(id) {
  if (!id) return ''
  const cat = categories.value.find(c => c.id === id)
  return cat ? cat.name : ''
}

function selectCategory(id) {
  activeCategory.value = id
  const keyword = route.query.q || ''
  if (keyword) {
    store.searchSecrets(keyword)
  } else {
    store.fetchSecrets(id)
  }
}

async function handleDelete(id) {
  if (confirm(t('secret.deleteConfirm'))) {
    await store.deleteSecret(id)
    const keyword = route.query.q || ''
    if (keyword) {
      store.searchSecrets(keyword)
    } else {
      store.fetchSecrets(activeCategory.value)
    }
  }
}

onMounted(() => {
  // 只有在保险箱已解锁时才加载数据
  if (auth.vaultUnlocked) {
    store.fetchCategories()
    const keyword = route.query.q || ''
    if (keyword) {
      store.searchSecrets(keyword)
    } else {
      store.fetchSecrets()
    }
  }
})

// 监听解锁状态变化，解锁后加载数据
watch(() => auth.vaultUnlocked, (unlocked) => {
  if (unlocked) {
    store.fetchCategories()
    const keyword = route.query.q || ''
    if (keyword) {
      store.searchSecrets(keyword)
    } else {
      store.fetchSecrets()
    }
  }
})

// 监听搜索关键词变化
watch(() => route.query.q, (keyword) => {
  if (auth.vaultUnlocked) {
    if (keyword) {
      store.searchSecrets(keyword)
    } else {
      // 清空搜索时，按当前分类重新加载
      store.fetchSecrets(activeCategory.value)
    }
  }
})
</script>

<template>
  <div class="pt-16 pb-20 md:pb-0 min-h-screen bg-surface">
    <div class="max-w-2xl mx-auto p-4 lg:p-6">
      <div class="flex items-center gap-3 mb-6">
        <button @click="$router.back()" class="p-2 rounded-lg hover:bg-surface-light transition-colors text-txt-muted">
          <ArrowLeft class="w-5 h-5" />
        </button>
        <h2 class="text-xl font-bold text-txt">{{ isEdit ? '编辑密钥' : '添加密钥' }}</h2>
      </div>

      <form @submit.prevent="submit" class="glass-strong rounded-2xl p-6 space-y-5">
        <div>
          <label class="block text-sm text-txt-muted mb-1.5">名称 *</label>
          <input v-model="form.name" type="text" required
            class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2.5 text-sm text-txt focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50"
            placeholder="如 OpenAI API Key" />
        </div>

        <div>
          <label class="block text-sm text-txt-muted mb-1.5">密钥值 *</label>
          <div class="relative">
            <input v-model="form.value" :type="showValue ? 'text' : 'password'" required
              class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2.5 pr-10 text-sm text-txt focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 font-mono"
              placeholder="sk-xxxxxxxxxxxxxxxx" />
            <button type="button" @click="showValue = !showValue" class="absolute right-3 top-1/2 -translate-y-1/2 text-txt-dim hover:text-txt">
              <Eye v-if="!showValue" class="w-4 h-4" />
              <EyeOff v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm text-txt-muted mb-1.5">分类</label>
          <select v-model="form.category_id"
            class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2.5 text-sm text-txt focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50">
            <option :value="null">未分类</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm text-txt-muted mb-1.5">URL</label>
          <input v-model="form.url" type="url"
            class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2.5 text-sm text-txt focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50"
            placeholder="https://api.example.com" />
        </div>

        <div>
          <label class="block text-sm text-txt-muted mb-1.5">备注（明文，简短标记）</label>
          <input v-model="form.remark" type="text"
            class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2.5 text-sm text-txt focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50"
            placeholder="生产环境 / 测试用途" />
        </div>

        <div>
          <label class="block text-sm text-txt-muted mb-1.5">加密备注（敏感信息）</label>
          <textarea v-model="form.notes" rows="3"
            class="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2.5 text-sm text-txt focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 resize-none"
            placeholder="详细备注，将加密存储" />
        </div>

        <p v-if="error" class="text-danger text-sm">{{ error }}</p>

        <div class="flex gap-3 pt-2">
          <button type="button" @click="$router.back()"
            class="flex-1 py-2.5 rounded-lg border border-surface-lighter text-txt-muted hover:text-txt transition-colors text-sm">取消</button>
          <button type="submit" :disabled="saving"
            class="flex-1 py-2.5 rounded-lg bg-gradient-to-r from-primary to-cyan-500 text-white font-medium hover:from-primary-dark hover:to-cyan-600 transition-all disabled:opacity-50 text-sm">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>

        <button v-if="isEdit" type="button" @click="handleDelete"
          class="w-full py-2 rounded-lg border border-danger/30 text-danger hover:bg-danger/10 transition-colors text-sm">删除此密钥</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Eye, EyeOff } from 'lucide-vue-next'
import { useSecretsStore } from '../stores/secrets'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const store = useSecretsStore()
const auth = useAuthStore()

const isEdit = computed(() => !!route.params.id)
const showValue = ref(false)
const saving = ref(false)
const error = ref('')

const form = reactive({
  name: '',
  value: '',
  category_id: null,
  url: '',
  remark: '',
  notes: '',
})

const categories = computed(() => store.categories)

onMounted(async () => {
  await store.fetchCategories()
  if (isEdit.value) {
    try {
      const data = await store.fetchSecret(route.params.id)
      form.name = data.name
      form.value = data.value
      form.category_id = data.category_id
      form.url = data.url || ''
      form.remark = data.remark || ''
      form.notes = data.notes || ''
    } catch (e) {
      error.value = e.response?.data?.detail || '加载失败，请确保保险箱已解锁'
    }
  }
})

// 监听解锁状态变化，解锁后重新加载数据
watch(() => auth.vaultUnlocked, async (unlocked) => {
  if (unlocked) {
    await store.fetchCategories()
    if (isEdit.value) {
      try {
        const data = await store.fetchSecret(route.params.id)
        form.name = data.name
        form.value = data.value
        form.category_id = data.category_id
        form.url = data.url || ''
        form.remark = data.remark || ''
        form.notes = data.notes || ''
        error.value = ''
      } catch (e) {
        error.value = e.response?.data?.detail || '加载失败'
      }
    }
  }
})

async function submit() {
  error.value = ''
  saving.value = true
  try {
    if (isEdit.value) {
      await store.updateSecret(route.params.id, { ...form })
    } else {
      await store.createSecret({ ...form })
    }
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (confirm('确认删除此密钥？此操作不可撤销。')) {
    await store.deleteSecret(route.params.id)
    router.push('/')
  }
}
</script>

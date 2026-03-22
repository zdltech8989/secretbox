<template>
  <div class="relative">
    <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-txt-dim" />
    <input
      type="text"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      @keyup.enter="$emit('search', modelValue)"
      :placeholder="t('nav.searchPlaceholder')"
      class="w-full bg-surface-light border border-surface-lighter rounded-lg pl-10 pr-4 py-2 text-sm text-txt placeholder-txt-dim focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all"
    />
  </div>
</template>

<script setup>
import { Search } from 'lucide-vue-next'
import { useI18n } from '../i18n'

const { t } = useI18n()

defineProps({ modelValue: { type: String, default: '' } })
defineEmits(['update:modelValue', 'search'])
</script>

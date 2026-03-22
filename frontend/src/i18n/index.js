import { reactive } from 'vue'
import zhCN from './zh-CN'
import en from './en'

const messages = {
  'zh-CN': zhCN,
  'en': en
}

const i18n = reactive({
  locale: localStorage.getItem('secretbox_locale') || 'zh-CN',
  messages,
  
  t(key, params = {}) {
    const keys = key.split('.')
    let value = this.messages[this.locale]
    
    for (const k of keys) {
      value = value?.[k]
      if (!value) return key
    }
    
    if (typeof value === 'string') {
      return Object.keys(params).reduce((str, param) => {
        return str.replace(`{${param}}`, params[param])
      }, value)
    }
    
    return value
  },
  
  setLocale(locale) {
    if (this.messages[locale]) {
      this.locale = locale
      localStorage.setItem('secretbox_locale', locale)
    }
  }
})

export function useI18n() {
  return {
    locale: () => i18n.locale,
    t: (key, params) => i18n.t(key, params),
    setLocale: (locale) => i18n.setLocale(locale)
  }
}

export default i18n

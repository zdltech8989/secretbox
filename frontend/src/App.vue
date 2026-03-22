<template>
  <NavBar v-if="auth.isLoggedIn" />
  <router-view />
  <MobileNav v-if="auth.isLoggedIn" />

  <!-- 登录后：未设置主密码 → 设置界面；已设置但未解锁 → 解锁界面 -->
  <VaultUnlockModal
    v-if="auth.isLoggedIn && !auth.vaultUnlocked"
    :is-setup="!auth.masterInitialized" />
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import NavBar from './components/NavBar.vue'
import MobileNav from './components/MobileNav.vue'
import VaultUnlockModal from './components/VaultUnlockModal.vue'

const auth = useAuthStore()
auth.initFromStorage()
</script>

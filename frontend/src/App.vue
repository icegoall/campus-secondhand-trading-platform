<template>
  <el-config-provider :locale="enLocale">
    <div class="app-layout">
      <el-header class="app-header">
        <div class="header-inner">
          <div class="logo" @click="router.push('/')">
            <span class="logo-badge">🛒</span>
            <span class="logo-text">Campus Market</span>
          </div>
          <el-menu :default-active="activeMenu" mode="horizontal" :ellipsis="false" router class="nav-menu">
            <el-menu-item index="/">Browse Market</el-menu-item>
            <el-menu-item index="/publish" v-if="userStore.isLoggedIn">Publish Item</el-menu-item>
            <el-menu-item index="/profile" v-if="userStore.isLoggedIn">User Profile</el-menu-item>
          </el-menu>
          <div class="header-right">
            <template v-if="userStore.isLoggedIn">
              <el-dropdown @command="handleCommand">
                <span class="user-chip">
                  <el-avatar :size="28" :src="userStore.user?.avatar" class="user-avatar">
                    {{ userStore.user?.nickname?.[0] }}
                  </el-avatar>
                  <span class="user-name">{{ userStore.user?.nickname }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">User Profile</el-dropdown-item>
                    <el-dropdown-item command="publish">Publish Item</el-dropdown-item>
                    <el-dropdown-item command="logout" divided>Logout</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <el-button round @click="router.push('/login')">Login</el-button>
              <el-button type="primary" round @click="router.push('/register')">Register</el-button>
            </template>
          </div>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>

      <el-footer class="app-footer">
        <span>Campus Market · Lab 6 · Vue 3 + Flask + SQLite · For educational use only</span>
      </el-footer>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import enLocale from 'element-plus/es/locale/lang/en'
import { ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from './stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

async function handleCommand(cmd) {
  if (cmd === 'profile') router.push('/profile')
  else if (cmd === 'publish') router.push('/publish')
  else if (cmd === 'logout') {
    await ElMessageBox.confirm('Are you sure you want to log out?', 'Confirm', { type: 'warning', confirmButtonText: 'Logout', cancelButtonText: 'Cancel' })
    await userStore.logout()
    ElMessage.success('Logged out')
    router.push('/')
  }
}
</script>

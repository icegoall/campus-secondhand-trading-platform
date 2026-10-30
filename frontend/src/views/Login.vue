<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="never">
      <template #header>
        <div class="auth-title">Welcome back</div>
        <div class="auth-sub">Sign in to Campus Market</div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="onSubmit">
        <el-form-item label="Student ID" prop="account">
          <el-input v-model="form.account" placeholder="e.g. 202100101" :prefix-icon="User" clearable />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="Your password" :prefix-icon="Lock" @keyup.enter="onSubmit" />
        </el-form-item>
        <el-button type="primary" round :loading="loading" class="submit-btn" @click="onSubmit">Sign In</el-button>
        <div class="auth-foot">
          No account yet? <el-link type="primary" @click="router.push('/register')">Create one</el-link>
        </div>
      </el-form>
      <el-alert class="demo-tip" type="info" :closable="false" title="Demo account: ID 202100101 · password alice" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ account: '', password: '' })
const rules = {
  account: [{ required: true, message: 'Please enter your student ID', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter your password', trigger: 'blur' }]
}

async function onSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await userStore.login(form.account, form.password)
    ElMessage.success(`Welcome back, ${userStore.user.nickname}!`)
    router.push(route.query.redirect || '/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { display: flex; justify-content: center; padding-top: 48px; }
.auth-card { width: 440px; border-radius: 20px; border: 1px solid var(--line); box-shadow: var(--shadow-sm); }
.auth-title { font-size: 24px; font-weight: 800; text-align: center; letter-spacing: -.3px; }
.auth-sub { text-align: center; color: var(--ink-3); font-size: 14px; margin-top: 6px; }
.submit-btn { width: 100%; margin-top: 8px; }
.auth-foot { text-align: center; margin-top: 16px; font-size: 14px; color: var(--ink-2); }
.demo-tip { margin-top: 18px; border-radius: 12px; }
</style>

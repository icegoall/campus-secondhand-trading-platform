<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="never">
      <template #header>
        <div class="auth-title">Create your account</div>
        <div class="auth-sub">Join Campus Market in seconds</div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="Student ID" prop="student_id">
          <el-input v-model="form.student_id" placeholder="e.g. 202400101" :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="Nickname" prop="nickname">
          <el-input v-model="form.nickname" placeholder="e.g. Alex" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="At least 6 characters" :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item label="Phone (optional)" prop="phone">
          <el-input v-model="form.phone" placeholder="11-digit mobile number" />
        </el-form-item>
        <el-form-item label="Dorm / Building" prop="dorm">
          <el-input v-model="form.dorm" placeholder="e.g. Dorm 1" />
        </el-form-item>
        <el-form-item label="Campus" prop="campus">
          <el-select v-model="form.campus" placeholder="Select campus" class="full-width">
            <el-option v-for="c in CAMPUSES" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-button type="primary" round :loading="loading" class="submit-btn" @click="onSubmit">Sign Up</el-button>
        <div class="auth-foot">
          Already have an account? <el-link type="primary" @click="router.push('/login')">Sign in</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { authApi } from '../api'
import { CAMPUSES } from '../constants'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({ student_id: '', nickname: '', password: '', phone: '', dorm: '', campus: 'Main Campus' })

const rules = {
  student_id: [
    { required: true, message: 'Student ID is required', trigger: 'blur' },
    { pattern: /^\d{6,12}$/, message: 'Student ID must be 6–12 digits', trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: 'Nickname is required', trigger: 'blur' },
    { min: 2, max: 20, message: '2–20 characters', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Password is required', trigger: 'blur' },
    { min: 6, message: 'At least 6 characters', trigger: 'blur' }
  ],
  phone: [{ pattern: /^1\d{10}$/, message: 'Enter a valid 11-digit mobile number', trigger: 'blur' }],
  dorm: [{ max: 30, message: 'At most 30 characters', trigger: 'blur' }]
}

async function onSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await authApi.register(form)
    ElMessage.success('Account created — please sign in')
    router.push('/login')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { display: flex; justify-content: center; padding-top: 32px; }
.auth-card { width: 440px; border-radius: 20px; border: 1px solid var(--line); box-shadow: var(--shadow-sm); }
.auth-title { font-size: 24px; font-weight: 800; text-align: center; letter-spacing: -.3px; }
.auth-sub { text-align: center; color: var(--ink-3); font-size: 14px; margin-top: 6px; }
.full-width { width: 100%; }
.submit-btn { width: 100%; margin-top: 8px; }
.auth-foot { text-align: center; margin-top: 16px; font-size: 14px; color: var(--ink-2); }
</style>

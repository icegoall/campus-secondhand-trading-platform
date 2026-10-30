<template>
  <div class="publish-page">
    <h2 class="page-title">Publish an Item</h2>
    <el-card class="section-card" shadow="never">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="130px" class="publish-form">
        <el-form-item label="Title" prop="title">
          <el-input v-model="form.title" placeholder="Describe your item in one line" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="Category" prop="category">
          <el-select v-model="form.category" placeholder="Select a category">
            <el-option v-for="c in CATEGORIES" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="Condition" prop="condition">
          <el-select v-model="form.condition" placeholder="Select condition">
            <el-option v-for="c in CONDITIONS" :key="c.value" :label="`${c.value} (${c.hint})`" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Selling Price" prop="price">
          <el-input-number v-model="form.price" :min="0" :precision="2" :step="1" controls-position="right" />
          <span class="unit">{{ CURRENCY }}</span>
        </el-form-item>
        <el-form-item label="Original Price">
          <el-input-number v-model="form.original_price" :min="0" :precision="2" :step="1" controls-position="right" />
          <span class="unit">{{ CURRENCY }} (optional)</span>
        </el-form-item>
        <el-form-item label="Cover Image">
          <div class="image-area">
            <el-input v-model="form.image_url" placeholder="Paste an image URL, or upload a photo below" clearable @input="previewFailed = false" />
            <el-upload :show-file-list="false" accept="image/*" :http-request="onUpload" :before-upload="beforeUpload" class="uploader">
              <el-button :loading="uploading">Upload Image</el-button>
            </el-upload>
            <div class="img-preview" v-if="form.image_url">
              <img v-if="!previewFailed" :src="form.image_url" @error="previewFailed = true" />
              <div v-else class="preview-fallback">
                <span>⚠️ Preview unavailable — please check the URL</span>
              </div>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4" maxlength="300" show-word-limit
            placeholder="Usage, accessories included, flaws to note, meet-up preferences…" />
        </el-form-item>
        <el-form-item label="Contact" prop="contact">
          <el-input v-model="form.contact" placeholder="e.g. WeChat: name / QQ: 12345 / phone" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" round :loading="loading" @click="onSubmit">Publish Now</el-button>
          <el-button round @click="router.push('/')">Cancel</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { productApi, uploadApi } from '../api'
import { CATEGORIES, CONDITIONS, CURRENCY } from '../constants'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const uploading = ref(false)
const previewFailed = ref(false)

const form = reactive({
  title: '', category: '', condition: '', price: undefined, original_price: undefined,
  image_url: '', description: '', contact: ''
})

const rules = {
  title: [
    { required: true, message: 'Title is required', trigger: 'blur' },
    { min: 3, max: 50, message: '3–50 characters', trigger: 'blur' }
  ],
  category: [{ required: true, message: 'Please pick a category', trigger: 'change' }],
  condition: [{ required: true, message: 'Please pick the condition', trigger: 'change' }],
  price: [
    { required: true, message: 'Selling price is required', trigger: 'blur' },
    { validator: (r, v, cb) => (v > 0 ? cb() : cb(new Error('Price must be greater than 0'))), trigger: 'blur' }
  ],
  contact: [
    { required: true, message: 'Please add a contact method', trigger: 'blur' },
    { min: 3, max: 60, message: '3–60 characters', trigger: 'blur' }
  ]
}

function beforeUpload(file) {
  if (!file.type.startsWith('image/')) { ElMessage.error('Only image files are allowed'); return false }
  if (file.size > 5 * 1024 * 1024) { ElMessage.error('Image must be smaller than 5 MB'); return false }
  return true
}

async function onUpload({ file }) {
  uploading.value = true
  try {
    const res = await uploadApi.upload(file)
    form.image_url = res.data.url
    previewFailed.value = false
    ElMessage.success('Image uploaded')
  } finally {
    uploading.value = false
  }
}

async function onSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await productApi.create(form)
    ElMessage.success('Listing published 🎉')
    router.push(`/product/${res.data.id}`)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.publish-page { max-width: 780px; margin: 0 auto; }
.publish-form { margin-top: 10px; }
.unit { margin-left: 10px; color: var(--ink-3); font-size: 13px; }
.image-area { width: 100%; display: flex; flex-direction: column; gap: 10px; }
.uploader { align-self: flex-start; }
.img-preview img { max-width: 240px; max-height: 170px; border-radius: 12px; border: 1px solid var(--line); box-shadow: var(--shadow-sm); }
.preview-fallback {
  max-width: 240px; height: 120px; border-radius: 12px; border: 1px dashed var(--line);
  display: flex; align-items: center; justify-content: center; padding: 0 16px;
  color: var(--ink-3); font-size: 13px; background: #fafbfe;
}
</style>

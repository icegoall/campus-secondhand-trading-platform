<template>
  <div class="detail-page" v-loading="loading">
    <el-page-header @back="router.push('/')" class="back-header">
      <template #content><span class="back-title">Back to Market</span></template>
    </el-page-header>

    <div class="detail-layout" v-if="product">
      <div class="detail-left">
        <div class="big-img">
          <img v-if="showImg" :src="product.image_url" :alt="product.title" @error="onImgError" />
          <div v-else class="img-fallback" :style="{ background: meta.gradient }">
            <span class="fallback-emoji">{{ meta.emoji }}</span>
            <span class="fallback-label">{{ product.category }}</span>
          </div>
        </div>
      </div>
      <div class="detail-right">
        <div class="d-title">{{ product.title }}</div>
        <div class="d-tags">
          <span class="chip">{{ product.category }}</span>
          <span class="chip">{{ product.condition }}</span>
          <el-tag :type="statusInfo.type" effect="dark" round>{{ statusInfo.label }}</el-tag>
        </div>
        <div class="d-price">
          <span class="price">{{ formatPrice(product.price) }}</span>
          <span class="price-origin" v-if="product.original_price">{{ formatPrice(product.original_price) }}</span>
          <span class="off" v-if="offLabel">{{ offLabel }}</span>
        </div>
        <el-divider />
        <div class="d-desc">
          <div class="desc-label">Description</div>
          <p>{{ product.description || 'No description provided.' }}</p>
        </div>
        <div class="d-contact" v-if="product.contact">
          <div class="desc-label">Contact</div>
          <p>{{ product.contact }}</p>
        </div>
        <el-divider />
        <div class="d-seller">
          <el-avatar :size="44" class="seller-avatar">{{ product.seller?.nickname?.[0] }}</el-avatar>
          <div class="seller-info">
            <div class="seller-name">{{ product.seller?.nickname }}</div>
            <div class="seller-meta">ID {{ product.seller?.student_id }} · {{ product.seller?.dorm }}<span v-if="product.seller?.phone"> · {{ product.seller.phone }}</span></div>
          </div>
        </div>
        <div class="d-actions">
          <el-button type="primary" size="large" round :disabled="!canBook" @click="onBook">
            {{ bookBtnText }}
          </el-button>
          <el-button size="large" round @click="scrollToComments">View Comments</el-button>
        </div>
      </div>
    </div>

    <div class="comment-section" ref="commentRef" v-if="product">
      <h3 class="comment-title">Community Q&A ({{ comments.length }})</h3>
      <div class="comment-input" v-if="userStore.isLoggedIn">
        <el-input v-model="newComment" placeholder="Ask about condition, meet-up location…" maxlength="200" show-word-limit>
          <template #append>
            <el-button type="primary" :loading="commenting" @click="onComment">Post</el-button>
          </template>
        </el-input>
      </div>
      <el-alert v-else type="info" :closable="false" title="Sign in to join the discussion" class="login-tip" />
      <div class="comment-list">
        <div class="comment-item" v-for="c in comments" :key="c.id">
          <el-avatar :size="36" class="c-avatar">{{ c.user_name?.[0] }}</el-avatar>
          <div class="c-body">
            <div class="c-head">
              <span class="c-name">{{ c.user_name }}</span>
              <span class="c-time">{{ c.created_at }}</span>
            </div>
            <div class="c-content">{{ c.content }}</div>
          </div>
        </div>
        <el-empty v-if="comments.length === 0" description="No comments yet — be the first to ask!" :image-size="120" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { productApi, orderApi, commentApi } from '../api'
import { useUserStore } from '../stores/user'
import { PRODUCT_STATUS, CATEGORY_META, formatPrice, discountLabel } from '../constants'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const product = ref(null)
const comments = ref([])
const loading = ref(false)
const commenting = ref(false)
const newComment = ref('')
const commentRef = ref(null)
const imgFailed = ref(false)

const showImg = computed(() => !!product.value?.image_url && !imgFailed.value)
const onImgError = () => { imgFailed.value = true }
const meta = computed(() => CATEGORY_META[product.value?.category] || CATEGORY_META['Fashion & Others'])
const statusInfo = computed(() => PRODUCT_STATUS[product.value?.status] || PRODUCT_STATUS.Available)
const offLabel = computed(() => discountLabel(product.value?.price, product.value?.original_price))
const isOwner = computed(() => userStore.isLoggedIn && product.value?.seller_id === userStore.user?.id)
const canBook = computed(() => userStore.isLoggedIn && !isOwner.value && product.value?.status === 'Available')
const bookBtnText = computed(() => {
  if (!userStore.isLoggedIn) return 'Sign in to Book'
  if (isOwner.value) return 'This is your listing'
  if (product.value?.status === 'Reserved') return 'Already Reserved'
  if (product.value?.status === 'Sold') return 'Sold Out'
  return 'Book Now'
})

async function load() {
  loading.value = true
  try {
    const res = await productApi.detail(route.params.id)
    product.value = res.data
    const c = await commentApi.list(route.params.id)
    comments.value = c.data
  } finally {
    loading.value = false
  }
}

async function onBook() {
  await ElMessageBox.confirm(
    `Book "${product.value.title}" for ${formatPrice(product.value.price)}? The item will be locked for you until the seller confirms.`,
    'Confirm Booking',
    { type: 'warning', confirmButtonText: 'Book Now', cancelButtonText: 'Cancel' }
  )
  await orderApi.create(product.value.id)
  ElMessage.success('Booked! Waiting for the seller to confirm.')
  await load()
}

async function onComment() {
  if (!newComment.value.trim()) return
  commenting.value = true
  try {
    await commentApi.add(product.value.id, newComment.value)
    newComment.value = ''
    ElMessage.success('Comment posted')
    const c = await commentApi.list(product.value.id)
    comments.value = c.data
  } finally {
    commenting.value = false
  }
}

function scrollToComments() { commentRef.value?.scrollIntoView({ behavior: 'smooth' }) }

onMounted(load)
</script>

<style scoped>
.back-header { margin-bottom: 20px; }
.back-title { font-weight: 700; }
.detail-layout { display: flex; gap: 36px; background: var(--surface); border-radius: 20px; padding: 28px; box-shadow: var(--shadow-sm); border: 1px solid var(--line); }
.detail-left { flex: 0 0 440px; }
.big-img { width: 100%; height: 380px; border-radius: var(--radius-lg); overflow: hidden; background: #f1f3f9; }
.big-img img { width: 100%; height: 100%; object-fit: cover; }
.img-fallback { width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; }
.fallback-emoji { font-size: 72px; filter: drop-shadow(0 6px 10px rgba(15,23,42,.18)); }
.fallback-label { font-size: 14px; font-weight: 700; color: var(--ink-2); letter-spacing: .5px; text-transform: uppercase; }
.detail-right { flex: 1; min-width: 0; }
.d-title { font-size: 26px; font-weight: 800; line-height: 1.35; letter-spacing: -.3px; }
.d-tags { display: flex; gap: 8px; margin: 14px 0; align-items: center; }
.chip { font-size: 12px; font-weight: 600; color: var(--ink-2); background: #f1f3f9; padding: 4px 10px; border-radius: 999px; }
.d-price { margin: 18px 0; display: flex; align-items: baseline; gap: 12px; }
.d-price .price { font-size: 34px; }
.d-price .price-origin { font-size: 15px; }
.off { font-size: 12px; font-weight: 700; color: #e11d48; background: #ffe4e6; padding: 3px 9px; border-radius: 999px; }
.desc-label { font-size: 13px; font-weight: 700; color: var(--ink-3); text-transform: uppercase; letter-spacing: .6px; margin-bottom: 8px; }
.d-desc p, .d-contact p { margin: 0; line-height: 1.75; color: var(--ink-2); }
.d-contact { margin-top: 18px; }
.d-seller { display: flex; align-items: center; gap: 14px; }
.seller-avatar { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; font-weight: 700; }
.seller-name { font-weight: 700; font-size: 16px; }
.seller-meta { font-size: 13px; color: var(--ink-3); margin-top: 3px; }
.d-actions { margin-top: 26px; display: flex; gap: 12px; }
.comment-section { background: var(--surface); border-radius: 20px; padding: 26px; margin-top: 24px; box-shadow: var(--shadow-sm); border: 1px solid var(--line); }
.comment-title { margin: 0 0 18px; font-size: 19px; font-weight: 800; }
.comment-input { margin-bottom: 22px; }
.login-tip { margin-bottom: 22px; }
.comment-item { display: flex; gap: 12px; padding: 14px 0; border-bottom: 1px solid #f1f3f9; }
.comment-item:last-child { border-bottom: none; }
.c-avatar { background: linear-gradient(135deg, #10b981, #34d399); color: #fff; flex-shrink: 0; font-weight: 700; }
.c-body { flex: 1; }
.c-head { display: flex; align-items: center; gap: 10px; }
.c-name { font-weight: 700; font-size: 14px; }
.c-time { font-size: 12px; color: var(--ink-3); }
.c-content { margin-top: 5px; color: var(--ink-2); line-height: 1.65; }

@media (max-width: 900px) {
  .detail-layout { flex-direction: column; }
  .detail-left { flex: none; width: 100%; }
}
</style>

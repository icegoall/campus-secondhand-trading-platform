<template>
  <div class="home">
    <div class="hero">
      <div class="hero-content">
        <h1>Give your pre-loved items a second life 🌱</h1>
        <p>Books, electronics, daily essentials — great finds from fellow students at student-friendly prices.</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round @click="goPublish" v-if="userStore.isLoggedIn">Publish an Item</el-button>
          <el-button size="large" round @click="scrollToList">Browse Market</el-button>
        </div>
      </div>
    </div>

    <div class="filter-bar" ref="listRef">
      <div class="filter-left">
        <el-input v-model="keyword" placeholder="Search by title or description…" clearable class="search-input"
          :prefix-icon="Search" @keyup.enter="reload" @clear="reload" />
        <el-select v-model="category" placeholder="All Categories" clearable class="cat-select" @change="reload">
          <el-option v-for="c in CATEGORIES" :key="c" :label="c" :value="c" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-radio-group v-model="status" @change="reload">
          <el-radio-button value="Available">Available</el-radio-button>
          <el-radio-button value="Reserved">Reserved</el-radio-button>
          <el-radio-button value="Sold">Sold</el-radio-button>
          <el-radio-button value="all">All</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div v-if="loading" class="skeleton-grid">
      <div v-for="i in 8" :key="i" class="skeleton-card">
        <el-skeleton animated>
          <template #template>
            <el-skeleton-item variant="image" style="width: 100%; height: 178px; border-radius: 12px" />
            <div style="padding-top: 12px">
              <el-skeleton-item variant="h3" style="width: 80%" />
              <el-skeleton-item variant="text" style="width: 55%; margin-top: 10px" />
              <el-skeleton-item variant="text" style="width: 35%" />
            </div>
          </template>
        </el-skeleton>
      </div>
    </div>

    <div v-else class="product-grid">
      <ProductCard v-for="p in products" :key="p.id" :product="p" />
      <div v-if="products.length === 0" class="empty-tip">
        <el-empty :image-size="160" :description="emptyText">
          <el-button type="primary" round @click="resetFilters">Reset filters</el-button>
        </el-empty>
      </div>
    </div>

    <div class="pager" v-if="total > 0">
      <el-pagination background layout="prev, pager, next, total" :total="total" :page-size="pageSize"
        :current-page="page" @current-change="onPageChange" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { productApi } from '../api'
import { useUserStore } from '../stores/user'
import { CATEGORIES } from '../constants'
import ProductCard from '../components/ProductCard.vue'

const router = useRouter()
const userStore = useUserStore()

const keyword = ref('')
const category = ref('')
const status = ref('Available')
const page = ref(1)
const pageSize = 12
const products = ref([])
const total = ref(0)
const loading = ref(false)
const listRef = ref(null)

const emptyText = computed(() => {
  if (keyword.value) return `No items found for "${keyword.value}"`
  if (category.value) return `No items found in ${category.value}`
  if (status.value !== 'all') return `No ${status.value.toLowerCase()} items right now`
  return 'No items yet — be the first to publish one!'
})

let timer = null
watch(keyword, () => {
  clearTimeout(timer)
  timer = setTimeout(reload, 350)
})
onBeforeUnmount(() => clearTimeout(timer))

async function load() {
  loading.value = true
  try {
    const res = await productApi.list({
      page: page.value, size: pageSize,
      keyword: keyword.value, category: category.value, status: status.value
    })
    products.value = res.data.list
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}
function reload() { page.value = 1; load() }
function resetFilters() { keyword.value = ''; category.value = ''; status.value = 'Available'; reload() }
function onPageChange(p) { page.value = p; load(); listRef.value?.scrollIntoView({ behavior: 'smooth' }) }
function goPublish() { router.push('/publish') }
function scrollToList() { listRef.value?.scrollIntoView({ behavior: 'smooth' }) }

onMounted(load)
</script>

<style scoped>
.hero {
  background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 55%, #0ea5e9 130%);
  border-radius: 20px;
  padding: 52px 40px;
  color: #fff;
  margin-bottom: 24px;
  box-shadow: var(--shadow-primary);
  position: relative;
  overflow: hidden;
}
.hero::after {
  content: '';
  position: absolute; right: -60px; top: -60px;
  width: 260px; height: 260px; border-radius: 50%;
  background: rgba(255, 255, 255, .12);
}
.hero-content { position: relative; z-index: 1; }
.hero h1 { margin: 0 0 12px; font-size: 32px; font-weight: 800; letter-spacing: -.5px; }
.hero p { margin: 0 0 22px; opacity: .92; font-size: 15.5px; max-width: 520px; line-height: 1.6; }
.hero-actions { display: flex; gap: 12px; }
.hero-actions .el-button--primary { background: #fff; color: #4f46e5; border: none; font-weight: 700; }
.hero-actions .el-button:not(.el-button--primary) { background: rgba(255,255,255,.14); color: #fff; border-color: rgba(255,255,255,.35); }

.filter-bar {
  display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;
  background: var(--surface); border-radius: var(--radius-lg); padding: 16px 18px;
  margin-bottom: 22px; box-shadow: var(--shadow-sm); border: 1px solid var(--line);
}
.filter-left { display: flex; gap: 10px; flex-wrap: wrap; }
.search-input { width: 280px; }
.cat-select { width: 180px; }
.product-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px;
  min-height: 240px;
}
.empty-tip { grid-column: 1 / -1; }
.pager { display: flex; justify-content: center; margin-top: 32px; }
</style>

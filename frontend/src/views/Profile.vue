<template>
  <div class="profile-page">
    <el-card class="section-card user-banner" shadow="never">
      <div class="banner-inner">
        <el-avatar :size="64" class="banner-avatar">{{ userStore.user?.nickname?.[0] }}</el-avatar>
        <div class="banner-info">
          <div class="banner-name">{{ userStore.user?.nickname }}</div>
          <div class="banner-meta">ID {{ userStore.user?.student_id }} · {{ userStore.user?.campus }} · {{ userStore.user?.dorm }}</div>
        </div>
        <el-button type="primary" round @click="router.push('/publish')">
          <el-icon><Plus /></el-icon> Publish Item
        </el-button>
      </div>
    </el-card>

    <el-tabs v-model="activeTab" class="profile-tabs" @tab-change="onTabChange">
      <el-tab-pane label="My Listings" name="products">
        <div v-loading="loadingProducts">
          <div class="grid" v-if="myProducts.length">
            <el-card v-for="p in myProducts" :key="p.id" class="my-card" shadow="never">
              <div class="my-img">
                <img v-if="p.image_url && !failed[p.id]" :src="p.image_url" @error="failed[p.id] = true" />
                <div v-else class="my-fallback" :style="{ background: catMeta(p.category).gradient }">{{ catMeta(p.category).emoji }}</div>
              </div>
              <div class="my-info">
                <div class="my-title" @click="router.push(`/product/${p.id}`)">{{ p.title }}</div>
                <div class="my-meta">
                  <span class="price">{{ formatPrice(p.price) }}</span>
                  <el-tag size="small" :type="statusInfo(p.status).type" round>{{ statusInfo(p.status).label }}</el-tag>
                </div>
                <div class="my-actions">
                  <el-button size="small" round @click="router.push(`/product/${p.id}`)">View</el-button>
                  <el-button size="small" round type="danger" plain :disabled="p.status !== 'Available'" @click="onDelete(p)">Delete</el-button>
                </div>
              </div>
            </el-card>
          </div>
          <el-empty v-else description="You haven't published anything yet" :image-size="140">
            <el-button type="primary" round @click="router.push('/publish')">Publish your first item</el-button>
          </el-empty>
        </div>
      </el-tab-pane>

      <el-tab-pane label="My Bookings" name="bookings">
        <div v-loading="loadingOrders">
          <el-table :data="buyerOrders" stripe v-if="buyerOrders.length" class="order-table">
            <el-table-column label="Item" min-width="220">
              <template #default="{ row }">
                <div class="order-prod" @click="router.push(`/product/${row.product_id}`)">
                  <img v-if="row.product_image && !failed['b' + row.id]" :src="row.product_image" class="order-thumb" @error="failed['b' + row.id] = true" />
                  <div v-else class="thumb-fallback">🛍️</div>
                  <span>{{ row.product_title }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="Seller" width="120" prop="seller_name" />
            <el-table-column label="Price" width="110"><template #default="{ row }">{{ formatPrice(row.product_price) }}</template></el-table-column>
            <el-table-column label="Status" width="120">
              <template #default="{ row }"><el-tag size="small" :type="orderInfo(row.status).type" round>{{ orderInfo(row.status).label }}</el-tag></template>
            </el-table-column>
            <el-table-column label="Booked At" width="170" prop="created_at" />
            <el-table-column label="Action" width="140">
              <template #default="{ row }">
                <el-button size="small" round type="warning" plain v-if="row.status === 'Reserved'" @click="onCancelOrder(row)">Cancel</el-button>
                <span v-else>—</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="No bookings yet — find something you like!" :image-size="140" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="Received Bookings" name="incoming">
        <div v-loading="loadingOrders">
          <el-table :data="sellerOrders" stripe v-if="sellerOrders.length" class="order-table">
            <el-table-column label="Item" min-width="180">
              <template #default="{ row }">
                <span class="link" @click="router.push(`/product/${row.product_id}`)">{{ row.product_title }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Buyer" width="110" prop="buyer_name" />
            <el-table-column label="Buyer Dorm" width="110" prop="buyer_dorm" />
            <el-table-column label="Contact" width="150" prop="buyer_phone" />
            <el-table-column label="Status" width="120">
              <template #default="{ row }"><el-tag size="small" :type="orderInfo(row.status).type" round>{{ orderInfo(row.status).label }}</el-tag></template>
            </el-table-column>
            <el-table-column label="Action" width="200">
              <template #default="{ row }">
                <template v-if="row.status === 'Reserved'">
                  <el-button size="small" round type="success" @click="onFinishOrder(row)">Mark Completed</el-button>
                  <el-button size="small" round type="warning" plain @click="onCancelOrder(row)">Decline</el-button>
                </template>
                <span v-else>—</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="No bookings received yet" :image-size="140" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { productApi, orderApi } from '../api'
import { useUserStore } from '../stores/user'
import { PRODUCT_STATUS, ORDER_STATUS, CATEGORY_META, formatPrice } from '../constants'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('products')
const myProducts = ref([])
const buyerOrders = ref([])
const sellerOrders = ref([])
const loadingProducts = ref(false)
const loadingOrders = ref(false)
const failed = reactive({})

const statusInfo = (s) => PRODUCT_STATUS[s] || PRODUCT_STATUS.Available
const orderInfo = (s) => ORDER_STATUS[s] || ORDER_STATUS.Reserved
const catMeta = (c) => CATEGORY_META[c] || CATEGORY_META['Fashion & Others']

async function loadProducts() {
  loadingProducts.value = true
  try { const res = await productApi.mine(); myProducts.value = res.data } finally { loadingProducts.value = false }
}
async function loadOrders() {
  loadingOrders.value = true
  try {
    const b = await orderApi.list('buyer'); buyerOrders.value = b.data
    const s = await orderApi.list('seller'); sellerOrders.value = s.data
  } finally { loadingOrders.value = false }
}
function onTabChange(tab) {
  if (tab === 'products' && !myProducts.value.length) loadProducts()
  if ((tab === 'bookings' || tab === 'incoming') && !buyerOrders.value.length) loadOrders()
}

async function onDelete(p) {
  await ElMessageBox.confirm(`Delete "${p.title}"? This cannot be undone.`, 'Delete Listing', { type: 'warning', confirmButtonText: 'Delete', cancelButtonText: 'Keep' })
  await productApi.remove(p.id)
  ElMessage.success('Listing deleted')
  await loadProducts()
}
async function onFinishOrder(row) {
  await ElMessageBox.confirm('Mark this order as completed? The item will be marked as sold.', 'Complete Order', { type: 'warning', confirmButtonText: 'Complete', cancelButtonText: 'Cancel' })
  await orderApi.updateStatus(row.id, 'Completed')
  ElMessage.success('Order completed 🎉')
  await loadOrders()
}
async function onCancelOrder(row) {
  await ElMessageBox.confirm('Cancel this booking? The item will be relisted as available.', 'Cancel Booking', { type: 'warning', confirmButtonText: 'Yes, cancel', cancelButtonText: 'Keep' })
  await orderApi.updateStatus(row.id, 'Cancelled')
  ElMessage.success('Booking cancelled — item is available again')
  await loadOrders()
}

onMounted(loadProducts)
</script>

<style scoped>
.user-banner { margin-bottom: 20px; }
.banner-inner { display: flex; align-items: center; gap: 18px; }
.banner-avatar { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; font-size: 26px; font-weight: 800; }
.banner-info { flex: 1; }
.banner-name { font-size: 22px; font-weight: 800; letter-spacing: -.2px; }
.banner-meta { color: var(--ink-3); margin-top: 4px; font-size: 14px; }
.profile-tabs { background: var(--surface); border-radius: var(--radius-lg); padding: 18px 22px; box-shadow: var(--shadow-sm); border: 1px solid var(--line); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.my-card { border-radius: var(--radius-lg); border: 1px solid var(--line); box-shadow: var(--shadow-sm); }
.my-card :deep(.el-card__body) { display: flex; gap: 14px; padding: 14px; }
.my-img { flex-shrink: 0; }
.my-img img, .my-fallback { width: 96px; height: 74px; border-radius: 10px; }
.my-img img { object-fit: cover; }
.my-fallback { display: flex; align-items: center; justify-content: center; font-size: 28px; }
.my-info { flex: 1; min-width: 0; }
.my-title { font-weight: 700; cursor: pointer; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.my-title:hover { color: var(--brand); }
.my-meta { display: flex; align-items: center; gap: 8px; margin: 9px 0; }
.my-actions { display: flex; gap: 8px; }
.order-table { margin-top: 8px; }
.order-prod { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.order-prod:hover { color: var(--brand); }
.order-thumb, .thumb-fallback { width: 44px; height: 34px; border-radius: 6px; }
.order-thumb { object-fit: cover; }
.thumb-fallback { background: #f1f3f9; display: flex; align-items: center; justify-content: center; font-size: 16px; }
.link { cursor: pointer; color: var(--brand); font-weight: 600; }
</style>

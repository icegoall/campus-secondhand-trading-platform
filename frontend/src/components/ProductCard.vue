<template>
  <el-card class="product-card" shadow="never" :body-style="{ padding: '14px' }" @click="router.push(`/product/${product.id}`)">
    <div class="img-wrap">
      <img v-if="showImg" :src="product.image_url" :alt="product.title" loading="lazy" @error="onImgError" />
      <div v-else class="img-fallback" :style="{ background: meta.gradient }">
        <span class="fallback-emoji">{{ meta.emoji }}</span>
        <span class="fallback-label">{{ product.category }}</span>
      </div>
      <el-tag class="status-tag" :type="statusInfo.type" size="small" effect="dark" round>{{ statusLabel }}</el-tag>
    </div>
    <div class="card-body">
      <div class="title" :title="product.title">{{ product.title }}</div>
      <div class="meta">
        <span class="chip">{{ product.category }}</span>
        <span class="chip">{{ product.condition }}</span>
      </div>
      <div class="price-row">
        <span class="price">{{ formatPrice(product.price) }}</span>
        <span class="price-origin" v-if="product.original_price">{{ formatPrice(product.original_price) }}</span>
        <span class="off" v-if="offLabel">{{ offLabel }}</span>
      </div>
      <div class="seller">
        <el-avatar :size="20" class="seller-avatar">{{ product.seller?.nickname?.[0] }}</el-avatar>
        <span class="seller-name">{{ product.seller?.nickname }}</span>
        <span class="seller-dorm" v-if="product.seller?.dorm">· {{ product.seller.dorm }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { PRODUCT_STATUS, CATEGORY_META, formatPrice, discountLabel } from '../constants'

const props = defineProps({ product: { type: Object, required: true } })
const router = useRouter()

const imgFailed = ref(false)
const showImg = computed(() => !!props.product.image_url && !imgFailed.value)
const onImgError = () => { imgFailed.value = true }

const meta = computed(() => CATEGORY_META[props.product.category] || CATEGORY_META['Fashion & Others'])
const statusInfo = computed(() => PRODUCT_STATUS[props.product.status] || PRODUCT_STATUS.Available)
const statusLabel = computed(() => statusInfo.value.label)
const offLabel = computed(() => discountLabel(props.product.price, props.product.original_price))
</script>

<style scoped>
.product-card {
  cursor: pointer;
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  transition: transform .22s ease, box-shadow .22s ease;
  overflow: hidden;
}
.product-card:hover { transform: translateY(-5px); box-shadow: var(--shadow-md); }
.img-wrap { position: relative; width: 100%; height: 178px; border-radius: var(--radius-md); overflow: hidden; background: #f1f3f9; }
.img-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .3s ease; }
.product-card:hover .img-wrap img { transform: scale(1.04); }
.img-fallback {
  width: 100%; height: 100%;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px;
}
.fallback-emoji { font-size: 44px; filter: drop-shadow(0 4px 6px rgba(15,23,42,.15)); }
.fallback-label { font-size: 12px; font-weight: 700; color: var(--ink-2); letter-spacing: .4px; text-transform: uppercase; }
.status-tag { position: absolute; top: 10px; right: 10px; box-shadow: 0 4px 10px rgba(15,23,42,.18); }
.title { font-size: 15px; font-weight: 700; line-height: 1.4; height: 42px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; margin-top: 12px; color: var(--ink); }
.meta { display: flex; gap: 6px; margin: 10px 0; flex-wrap: wrap; }
.chip {
  font-size: 11.5px; font-weight: 600; color: var(--ink-2);
  background: #f1f3f9; padding: 3px 9px; border-radius: 999px;
}
.price-row { display: flex; align-items: baseline; gap: 8px; }
.price { font-size: 21px; }
.off { font-size: 11px; font-weight: 700; color: #e11d48; background: #ffe4e6; padding: 2px 7px; border-radius: 999px; }
.seller { display: flex; align-items: center; gap: 6px; margin-top: 11px; color: var(--ink-3); font-size: 12.5px; }
.seller-avatar { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; font-size: 11px; font-weight: 700; }
</style>

export const CATEGORIES = ['Books', 'Electronics', 'Daily Essentials', 'Sports & Fitness', 'Fashion & Others']

export const CONDITIONS = [
  { value: 'Brand New', hint: '10/10' },
  { value: 'Like New', hint: '9/10' },
  { value: 'Good', hint: '8/10' },
  { value: 'Fair', hint: '7/10' }
]

export const CAMPUSES = ['Main Campus', 'South Campus', 'North Campus']

export const PRODUCT_STATUS = {
  Available: { type: 'success', label: 'Available' },
  Reserved: { type: 'warning', label: 'Reserved' },
  Sold: { type: 'info', label: 'Sold' }
}

export const ORDER_STATUS = {
  Reserved: { type: 'warning', label: 'Reserved' },
  Completed: { type: 'success', label: 'Completed' },
  Cancelled: { type: 'info', label: 'Cancelled' }
}

export const CATEGORY_META = {
  Books: { emoji: '📚', gradient: 'linear-gradient(135deg,#eef2ff,#e0e7ff)' },
  Electronics: { emoji: '💻', gradient: 'linear-gradient(135deg,#eff6ff,#dbeafe)' },
  'Daily Essentials': { emoji: '🏠', gradient: 'linear-gradient(135deg,#f0fdf4,#dcfce7)' },
  'Sports & Fitness': { emoji: '🏸', gradient: 'linear-gradient(135deg,#fff7ed,#ffedd5)' },
  'Fashion & Others': { emoji: '👟', gradient: 'linear-gradient(135deg,#fdf2f8,#fce7f3)' }
}

export const CURRENCY = '¥'

export function formatPrice(value) {
  const n = Number(value)
  if (Number.isNaN(n)) return `${CURRENCY}0`
  return CURRENCY + n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

export function discountLabel(price, original) {
  const p = Number(price)
  const o = Number(original)
  if (!o || o <= p) return ''
  return Math.round((1 - p / o) * 100) + '% OFF'
}

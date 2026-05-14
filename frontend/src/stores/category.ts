import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '../api/modules'
import type { Category, CategoryCreate, CategoryUpdate } from '../types'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<Category[]>([])
  const loading = ref(false)

  async function fetchCategories() {
    loading.value = true
    try {
      categories.value = await api.getCategories()
    } finally {
      loading.value = false
    }
  }

  async function createCategory(data: CategoryCreate) {
    const cat = await api.createCategory(data)
    categories.value.push(cat)
    return cat
  }

  async function updateCategory(id: number, data: CategoryUpdate) {
    const cat = await api.updateCategory(id, data)
    const idx = categories.value.findIndex(c => c.id === id)
    if (idx >= 0) categories.value[idx] = cat
    return cat
  }

  async function deleteCategory(id: number) {
    await api.deleteCategory(id)
    categories.value = categories.value.filter(c => c.id !== id)
  }

  return { categories, loading, fetchCategories, createCategory, updateCategory, deleteCategory }
})

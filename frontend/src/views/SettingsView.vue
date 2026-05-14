<template>
  <div class="settings-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>GitHub Connection</template>
          <el-descriptions :column="1" border size="small" v-if="githubStatus">
            <el-descriptions-item label="Status">
              <el-tag :type="githubStatus.connected ? 'success' : 'danger'" size="small">
                {{ githubStatus.connected ? 'Connected' : 'Disconnected' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="User">{{ githubStatus.user || '—' }}</el-descriptions-item>
            <el-descriptions-item label="Repo">{{ githubStatus.repo || '—' }}</el-descriptions-item>
            <el-descriptions-item label="Branch">{{ githubStatus.branch || '—' }}</el-descriptions-item>
          </el-descriptions>
          <el-button type="primary" @click="testConnection" :loading="testing" style="margin-top: 12px">
            Test Connection
          </el-button>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="panel-header">
              <span>Categories</span>
              <el-button type="primary" size="small" :icon="Plus" @click="openCategoryDialog()">Add</el-button>
            </div>
          </template>
          <el-table :data="categoryStore.categories" size="small" stripe>
            <el-table-column prop="name" label="Name" />
            <el-table-column prop="slug" label="Slug" />
            <el-table-column prop="template_count" label="Templates" width="90" />
            <el-table-column label="Actions" width="120">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="openCategoryDialog(row)">Edit</el-button>
                <el-button link type="danger" size="small" @click="handleDeleteCategory(row)">Del</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Category Dialog -->
    <el-dialog v-model="showCatDialog" :title="editCat ? 'Edit Category' : 'Add Category'" width="400px" @close="resetCatForm">
      <el-form :model="catForm" label-width="90px">
        <el-form-item label="Name"><el-input v-model="catForm.name" /></el-form-item>
        <el-form-item label="Slug"><el-input v-model="catForm.slug" /></el-form-item>
        <el-form-item label="Description"><el-input v-model="catForm.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="Sort"><el-input-number v-model="catForm.sort_order" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCatDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveCategory">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useCategoryStore } from '../stores/category'
import { getGitHubStatus, testGitHubConnection } from '../api/modules'
import type { Category, GitHubStatus } from '../types'

const categoryStore = useCategoryStore()
const githubStatus = ref<GitHubStatus | null>(null)
const testing = ref(false)
const showCatDialog = ref(false)
const editCat = ref<Category | null>(null)
const catForm = reactive({ name: '', slug: '', description: '', sort_order: 0 })

function resetCatForm() {
  editCat.value = null
  Object.assign(catForm, { name: '', slug: '', description: '', sort_order: 0 })
}

function openCategoryDialog(cat?: Category) {
  if (cat) {
    editCat.value = cat
    Object.assign(catForm, { name: cat.name, slug: cat.slug, description: cat.description || '', sort_order: cat.sort_order })
  }
  showCatDialog.value = true
}

async function saveCategory() {
  try {
    if (editCat.value) {
      await categoryStore.updateCategory(editCat.value.id, catForm)
      ElMessage.success('Updated')
    } else {
      await categoryStore.createCategory(catForm)
      ElMessage.success('Created')
    }
    showCatDialog.value = false
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Failed')
  }
}

async function handleDeleteCategory(cat: Category) {
  try {
    await ElMessageBox.confirm(`Delete category "${cat.name}"?`, 'Warning', { type: 'warning' })
    await categoryStore.deleteCategory(cat.id)
    ElMessage.success('Deleted')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || 'Delete failed')
  }
}

async function testConnection() {
  testing.value = true
  try {
    const result = await testGitHubConnection()
    githubStatus.value = result
    ElMessage.success(result.connected ? 'Connection OK' : 'Connection failed')
  } catch {
    githubStatus.value = { connected: false, error: 'Test failed' }
    ElMessage.error('Connection test failed')
  } finally {
    testing.value = false
  }
}

onMounted(async () => {
  await categoryStore.fetchCategories()
  try {
    githubStatus.value = await getGitHubStatus()
  } catch { /* optional */ }
})
</script>

<style scoped>
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

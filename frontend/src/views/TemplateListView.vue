<template>
  <div class="template-list">
    <el-row :gutter="20">
      <el-col :span="5">
        <el-card class="category-panel">
          <template #header>
            <div class="panel-header">
              <span>Categories</span>
              <el-button type="primary" :icon="Plus" circle size="small" @click="showCategoryDialog = true" />
            </div>
          </template>
          <div v-loading="categoryStore.loading">
            <div
              v-for="cat in categoryStore.categories"
              :key="cat.id"
              class="category-item"
              :class="{ active: selectedCategoryId === cat.id }"
              @click="selectCategory(cat.id)"
            >
              <span>{{ cat.name }}</span>
              <el-badge :value="cat.template_count" type="info" />
            </div>
            <div
              class="category-item"
              :class="{ active: selectedCategoryId === null }"
              @click="selectCategory(null)"
            >
              All
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="19">
        <el-card>
          <template #header>
            <div class="panel-header">
              <span>Templates</span>
              <el-button type="primary" :icon="Plus" @click="showTemplateDialog = true">New Template</el-button>
            </div>
          </template>
          <el-table :data="templateStore.templates" v-loading="templateStore.loading" stripe>
            <el-table-column prop="name" label="Name" min-width="150" />
            <el-table-column prop="filename" label="Filename" min-width="150" />
            <el-table-column prop="category_name" label="Category" width="120" />
            <el-table-column prop="current_version" label="Version" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.current_version" size="small">v{{ row.current_version }}</el-tag>
                <el-tag v-else type="info" size="small">none</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="160" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="router.push(`/templates/${row.id}`)">Detail</el-button>
                <el-button link type="primary" @click="editTemplate(row)">Edit</el-button>
                <el-button link type="danger" @click="handleArchive(row)">Archive</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Category Dialog -->
    <el-dialog v-model="showCategoryDialog" :title="editingCategory ? 'Edit Category' : 'New Category'" width="450px" @close="resetCategoryForm">
      <el-form :model="categoryForm" label-width="90px">
        <el-form-item label="Name">
          <el-input v-model="categoryForm.name" />
        </el-form-item>
        <el-form-item label="Slug">
          <el-input v-model="categoryForm.slug" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="categoryForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="Sort Order">
          <el-input-number v-model="categoryForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCategoryDialog = false">Cancel</el-button>
        <el-button type="danger" v-if="editingCategory" @click="handleDeleteCategory">Delete</el-button>
        <el-button type="primary" @click="handleSaveCategory">Save</el-button>
      </template>
    </el-dialog>

    <!-- Template Dialog -->
    <el-dialog v-model="showTemplateDialog" :title="editingTemplate ? 'Edit Template' : 'New Template'" width="500px" @close="resetTemplateForm">
      <el-form :model="templateForm" label-width="100px">
        <el-form-item label="Name">
          <el-input v-model="templateForm.name" />
        </el-form-item>
        <el-form-item label="Filename">
          <el-input v-model="templateForm.filename" placeholder="e.g. S12500.cfg" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="templateForm.category_id" style="width: 100%">
            <el-option v-for="cat in categoryStore.categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="GitHub Path">
          <el-input v-model="templateForm.github_path" placeholder="e.g. CORE/S12500.cfg" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTemplateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveTemplate">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useCategoryStore } from '../stores/category'
import { useTemplateStore } from '../stores/template'
import type { Template, Category } from '../types'

const router = useRouter()
const categoryStore = useCategoryStore()
const templateStore = useTemplateStore()

const selectedCategoryId = ref<number | null>(null)
const showCategoryDialog = ref(false)
const showTemplateDialog = ref(false)
const editingCategory = ref<Category | null>(null)
const editingTemplate = ref<Template | null>(null)

const categoryForm = reactive({ name: '', slug: '', description: '', sort_order: 0 })
const templateForm = reactive({ name: '', filename: '', category_id: 0, github_path: '' })

function statusType(status: string) {
  const map: Record<string, string> = { active: 'success', draft: 'warning', archived: 'info' }
  return map[status] || ''
}

function selectCategory(id: number | null) {
  selectedCategoryId.value = id
  templateStore.fetchTemplates(id ? { category_id: id, status: 'active' } : { status: 'active' })
}

function resetCategoryForm() {
  editingCategory.value = null
  Object.assign(categoryForm, { name: '', slug: '', description: '', sort_order: 0 })
}

function resetTemplateForm() {
  editingTemplate.value = null
  Object.assign(templateForm, { name: '', filename: '', category_id: 0, github_path: '' })
}

function editTemplate(tpl: Template) {
  editingTemplate.value = tpl
  Object.assign(templateForm, {
    name: tpl.name,
    filename: tpl.filename,
    category_id: tpl.category_id,
    github_path: tpl.github_path || '',
  })
  showTemplateDialog.value = true
}

async function handleSaveCategory() {
  try {
    if (editingCategory.value) {
      await categoryStore.updateCategory(editingCategory.value.id, categoryForm)
      ElMessage.success('Category updated')
    } else {
      await categoryStore.createCategory(categoryForm)
      ElMessage.success('Category created')
    }
    showCategoryDialog.value = false
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Operation failed')
  }
}

async function handleDeleteCategory() {
  if (!editingCategory.value) return
  try {
    await ElMessageBox.confirm('Delete this category?', 'Warning', { type: 'warning' })
    await categoryStore.deleteCategory(editingCategory.value.id)
    ElMessage.success('Category deleted')
    showCategoryDialog.value = false
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || 'Delete failed')
  }
}

async function handleSaveTemplate() {
  try {
    if (editingTemplate.value) {
      await templateStore.updateTemplate(editingTemplate.value.id, templateForm)
      ElMessage.success('Template updated')
    } else {
      await templateStore.createTemplate(templateForm)
      ElMessage.success('Template created')
    }
    showTemplateDialog.value = false
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Operation failed')
  }
}

async function handleArchive(tpl: Template) {
  try {
    await ElMessageBox.confirm(`Archive "${tpl.name}"?`, 'Warning', { type: 'warning' })
    await templateStore.archiveTemplate(tpl.id)
    ElMessage.success('Template archived')
  } catch {
    // cancelled
  }
}

onMounted(() => {
  categoryStore.fetchCategories()
  templateStore.fetchTemplates({ status: 'active' })
})
</script>

<style scoped>
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.category-item {
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
}
.category-item:hover { background: #f5f7fa; }
.category-item.active { background: #ecf5ff; color: #409eff; }
</style>

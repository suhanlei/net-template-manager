<template>
  <div class="release-list">
    <el-card>
      <template #header>
        <div class="panel-header">
          <span>Releases</span>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">New Release</el-button>
        </div>
      </template>
      <el-table :data="releaseStore.releases" v-loading="releaseStore.loading" stripe>
        <el-table-column prop="name" label="Name" min-width="200" />
        <el-table-column prop="version" label="Version" width="120">
          <template #default="{ row }">
            <el-tag type="primary" size="small">v{{ row.version }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="template_count" label="Templates" width="100" />
        <el-table-column prop="created_at" label="Created" width="180">
          <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="router.push(`/releases/${row.id}`)">Detail</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create Release Dialog -->
    <el-dialog v-model="showCreateDialog" title="New Release" width="450px" @close="resetForm">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="Name">
          <el-input v-model="createForm.name" placeholder="e.g. Q2 2026 Core Update" />
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="createForm.version" placeholder="e.g. 2.0.0" />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="createForm.release_notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="handleCreate">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useReleaseStore } from '../stores/release'

const router = useRouter()
const releaseStore = useReleaseStore()
const showCreateDialog = ref(false)
const createForm = reactive({ name: '', version: '', release_notes: '' })

function resetForm() {
  Object.assign(createForm, { name: '', version: '', release_notes: '' })
}

async function handleCreate() {
  try {
    await releaseStore.createRelease(createForm)
    ElMessage.success('Release created')
    showCreateDialog.value = false
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Create failed')
  }
}

onMounted(() => {
  releaseStore.fetchReleases()
})
</script>

<style scoped>
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

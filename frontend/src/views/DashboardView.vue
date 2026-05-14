<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6" v-for="(item, key) in stats?.counts" :key="key">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ item }}</div>
          <div class="stat-label">{{ statLabels[key as string] || key }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>Recent Templates</template>
          <el-table :data="stats?.recent_templates || []" size="small" stripe>
            <el-table-column prop="name" label="Name" />
            <el-table-column prop="current_version" label="Version" width="100" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="80">
              <template #default="{ row }">
                <el-button link type="primary" @click="router.push(`/templates/${row.id}`)">View</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>Recent Activity</template>
          <el-timeline v-if="stats?.recent_logs?.length">
            <el-timeline-item
              v-for="log in stats.recent_logs"
              :key="log.id"
              :timestamp="log.created_at"
              placement="top"
              :type="log.status === 'success' ? 'success' : 'danger'"
            >
              {{ log.action }} — {{ log.detail || log.target_type }}
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="No activity yet" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardStats } from '../api/modules'
import type { DashboardStats } from '../types'

const router = useRouter()
const stats = ref<DashboardStats | null>(null)

const statLabels: Record<string, string> = {
  templates: 'Templates',
  versions: 'Versions',
  releases: 'Releases',
  categories: 'Categories',
}

function statusType(status: string) {
  const map: Record<string, string> = { active: 'success', draft: 'warning', archived: 'info', committed: '', tagged: '', released: 'success' }
  return map[status] || ''
}

onMounted(async () => {
  try {
    stats.value = await getDashboardStats()
  } catch {
    // Dashboard is optional, don't block
  }
})
</script>

<style scoped>
.stat-card { text-align: center; cursor: pointer; }
.stat-value { font-size: 32px; font-weight: bold; color: #409eff; }
.stat-label { font-size: 13px; color: #999; margin-top: 4px; }
</style>

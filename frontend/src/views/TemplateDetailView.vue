<template>
  <div class="template-detail" v-loading="templateStore.loading">
    <template v-if="template">
      <el-page-header @back="router.push('/templates')" :title="'Back'">
        <template #content>
          <span class="page-title">{{ template.name }}</span>
          <el-tag :type="statusType(template.status)" size="small" style="margin-left: 8px">{{ template.status }}</el-tag>
          <el-tag v-if="template.current_version" type="primary" size="small" style="margin-left: 4px">v{{ template.current_version }}</el-tag>
        </template>
        <template #extra>
          <el-button type="primary" @click="showVersionDialog = true">New Version</el-button>
        </template>
      </el-page-header>

      <el-descriptions :column="3" border size="small" style="margin-top: 16px">
        <el-descriptions-item label="Filename">{{ template.filename }}</el-descriptions-item>
        <el-descriptions-item label="Category">{{ template.category_name }}</el-descriptions-item>
        <el-descriptions-item label="GitHub Path">{{ template.github_path || '—' }}</el-descriptions-item>
      </el-descriptions>

      <el-card style="margin-top: 16px">
        <template #header>
          <span>Version History</span>
        </template>
        <el-table :data="template.versions" size="small" stripe>
          <el-table-column prop="version" label="Version" width="100">
            <template #default="{ row }">v{{ row.version }}</template>
          </el-table-column>
          <el-table-column prop="change_type" label="Type" width="80">
            <template #default="{ row }">
              <el-tag :type="changeTypeColor(row.change_type)" size="small">{{ row.change_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="commit_message" label="Message" min-width="200" show-overflow-tooltip />
          <el-table-column prop="created_by" label="Author" width="100" />
          <el-table-column label="Actions" width="240" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewContent(row.version)">View</el-button>
              <el-button link type="primary" @click="editVersion(row.version)">Edit</el-button>
              <el-button link type="primary" @click="openDiff(row)">Diff</el-button>
              <el-button
                v-if="row.status === 'draft'"
                link type="success"
                @click="handleCommit(row.version)"
              >Commit</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </template>

    <!-- New Version Dialog -->
    <el-dialog v-model="showVersionDialog" title="New Version" width="80%" @close="resetVersionForm">
      <el-form :model="versionForm" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Change Type">
              <el-radio-group v-model="versionForm.change_type">
                <el-radio value="patch">Patch</el-radio>
                <el-radio value="minor">Minor</el-radio>
                <el-radio value="major">Major</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="Commit Message">
              <el-input v-model="versionForm.commit_message" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item label="Change Summary">
              <el-input v-model="versionForm.diff_summary" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item label="Author">
              <el-input v-model="versionForm.created_by" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Content">
              <el-input v-model="versionForm.content" type="textarea" :rows="16" style="font-family: monospace" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showVersionDialog = false">Cancel</el-button>
        <el-button type="primary" @click="handleCreateVersion">Create Version</el-button>
      </template>
    </el-dialog>

    <!-- Diff Dialog -->
    <el-dialog v-model="showDiffDialog" title="Version Diff" width="80%">
      <el-form :inline="true" style="margin-bottom: 12px">
        <el-form-item label="From">
          <el-select v-model="diffV1" style="width: 120px">
            <el-option v-for="v in versionOptions" :key="v" :label="'v' + v" :value="v" />
          </el-select>
        </el-form-item>
        <el-form-item label="To">
          <el-select v-model="diffV2" style="width: 120px">
            <el-option v-for="v in versionOptions" :key="v" :label="'v' + v" :value="v" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadDiff">Compare</el-button>
        </el-form-item>
      </el-form>
      <pre class="diff-output">{{ diffText }}</pre>
    </el-dialog>

    <!-- Content View Dialog -->
    <el-dialog v-model="showContentDialog" :title="'Content — v' + contentVersion" width="70%">
      <pre class="content-view">{{ contentText }}</pre>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useTemplateStore } from '../stores/template'

const route = useRoute()
const router = useRouter()
const templateStore = useTemplateStore()
const templateId = Number(route.params.id)
const template = computed(() => templateStore.currentTemplate)

const showVersionDialog = ref(false)
const showDiffDialog = ref(false)
const showContentDialog = ref(false)
const contentText = ref('')
const contentVersion = ref('')
const diffText = ref('')
const diffV1 = ref('')
const diffV2 = ref('')

const versionForm = ref({
  content: '',
  change_type: 'patch' as 'major' | 'minor' | 'patch',
  commit_message: '',
  diff_summary: '',
  created_by: 'anonymous',
})

const versionOptions = computed(() => {
  if (!template.value) return []
  return template.value.versions.map(v => v.version)
})

function statusType(status: string) {
  const map: Record<string, string> = { active: 'success', draft: 'warning', archived: 'info', committed: '', tagged: 'warning', released: 'success' }
  return map[status] || ''
}

function changeTypeColor(type: string) {
  const map: Record<string, string> = { major: 'danger', minor: 'warning', patch: 'success' }
  return map[type] || ''
}

function resetVersionForm() {
  versionForm.value = { content: '', change_type: 'patch', commit_message: '', diff_summary: '', created_by: 'anonymous' }
}

async function viewContent(version: string) {
  try {
    const vc = await templateStore.getVersionContent(templateId, version)
    contentText.value = vc.content
    contentVersion.value = version
    showContentDialog.value = true
  } catch (e: any) {
    ElMessage.error('Failed to load content')
  }
}

async function editVersion(version: string) {
  try {
    const vc = await templateStore.getVersionContent(templateId, version)
    versionForm.value.content = vc.content
    showVersionDialog.value = true
  } catch {
    ElMessage.error('Failed to load version')
  }
}

function openDiff() {
  if (template.value?.versions?.length >= 2) {
    const vs = template.value.versions
    diffV1.value = vs[vs.length - 1].version
    diffV2.value = vs[0].version
  }
  showDiffDialog.value = true
}

async function loadDiff() {
  if (!diffV1.value || !diffV2.value) return
  try {
    const result = await templateStore.diffVersions(templateId, diffV1.value, diffV2.value)
    diffText.value = result.unified_diff || 'No differences found.'
  } catch {
    ElMessage.error('Failed to generate diff')
  }
}

async function handleCommit(version: string) {
  try {
    const result = await templateStore.commitVersion(templateId, version)
    ElMessage.success(`Committed! SHA: ${result.commit_sha}`)
    templateStore.fetchTemplate(templateId)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Commit failed')
  }
}

async function handleCreateVersion() {
  try {
    await templateStore.createVersion(templateId, versionForm.value)
    ElMessage.success('Version created')
    showVersionDialog.value = false
    templateStore.fetchTemplate(templateId)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Create failed')
  }
}

onMounted(() => {
  templateStore.fetchTemplate(templateId)
})
</script>

<style scoped>
.page-title { font-size: 18px; font-weight: 600; }
.diff-output, .content-view {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 500px;
  overflow-y: auto;
}
</style>

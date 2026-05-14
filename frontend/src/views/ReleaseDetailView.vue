<template>
  <div class="release-detail" v-loading="releaseStore.loading">
    <template v-if="release">
      <el-page-header @back="router.push('/releases')" title="Back">
        <template #content>
          <span class="page-title">{{ release.name }}</span>
          <el-tag type="primary" size="small" style="margin-left: 8px">v{{ release.version }}</el-tag>
          <el-tag :type="release.status === 'published' ? 'success' : 'warning'" size="small" style="margin-left: 4px">{{ release.status }}</el-tag>
        </template>
        <template #extra>
          <el-button-group>
            <el-button type="primary" @click="showAddDialog = true" :disabled="release.status === 'published'">Add Template</el-button>
            <el-button @click="handleGenerateChangelog" :disabled="release.status === 'published'">Generate Changelog</el-button>
            <el-button type="success" @click="handlePublish" :disabled="release.status === 'published'">Publish</el-button>
          </el-button-group>
        </template>
      </el-page-header>

      <el-row :gutter="20" style="margin-top: 16px">
        <el-col :span="14">
          <el-card>
            <template #header>Included Templates</template>
            <el-table :data="release.snapshots" size="small" stripe>
              <el-table-column prop="template_name" label="Template" min-width="150" />
              <el-table-column prop="template_filename" label="Filename" min-width="120" />
              <el-table-column prop="version" label="Version" width="100">
                <template #default="{ row }">
                  <el-tag size="small">v{{ row.version }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Actions" width="80" v-if="release.status !== 'published'">
                <template #default="{ row }">
                  <el-button link type="danger" @click="handleRemove(row.template_id)">Remove</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="10">
          <el-card>
            <template #header>
              <div class="panel-header">
                <span>Changelog</span>
                <el-button v-if="release.status !== 'published'" link type="primary" @click="editingChangelog = true">Edit</el-button>
              </div>
            </template>
            <div v-if="editingChangelog">
              <el-input v-model="changelogEdit" type="textarea" :rows="12" />
              <el-button type="primary" size="small" style="margin-top: 8px" @click="handleSaveChangelog">Save</el-button>
            </div>
            <div v-else class="changelog-preview" v-html="renderedChangelog"></div>
          </el-card>
          <el-card style="margin-top: 16px" v-if="release.github_release_url">
            <template #header>GitHub Release</template>
            <el-link :href="release.github_release_url" target="_blank" type="primary">
              {{ release.github_tag }} — Open in GitHub
            </el-link>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <!-- Add Template Dialog -->
    <el-dialog v-model="showAddDialog" title="Add Template to Release" width="500px">
      <el-form label-width="120px">
        <el-form-item label="Template">
          <el-select v-model="addForm.template_id" style="width: 100%" @change="onTemplateSelect">
            <el-option v-for="t in availableTemplates" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version">
          <el-select v-model="addForm.template_version_id" style="width: 100%">
            <el-option v-for="v in selectedVersions" :key="v.id" :label="'v' + v.version" :value="v.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">Cancel</el-button>
        <el-button type="primary" @click="handleAddTemplate">Add</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import MarkdownIt from 'markdown-it'
import { useReleaseStore } from '../stores/release'
import { useTemplateStore } from '../stores/template'
import type { TemplateVersion } from '../types'

const md = new MarkdownIt()
const route = useRoute()
const router = useRouter()
const releaseStore = useReleaseStore()
const templateStore = useTemplateStore()
const releaseId = Number(route.params.id)
const release = computed(() => releaseStore.currentRelease)

const showAddDialog = ref(false)
const editingChangelog = ref(false)
const changelogEdit = ref('')
const addForm = ref({ template_id: 0, template_version_id: 0 })
const selectedVersions = ref<TemplateVersion[]>([])

const availableTemplates = computed(() => templateStore.templates)
const renderedChangelog = computed(() => {
  const text = release.value?.changelog || '*No changelog generated yet.*'
  return md.render(text)
})

function onTemplateSelect(templateId: number) {
  const tpl = availableTemplates.value.find(t => t.id === templateId)
  if (tpl) {
    templateStore.fetchVersions(tpl.id)
    selectedVersions.value = templateStore.versions
    addForm.value.template_version_id = 0
  }
}

async function handleAddTemplate() {
  try {
    await releaseStore.addTemplate(releaseId, addForm.value)
    ElMessage.success('Template added')
    showAddDialog.value = false
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Add failed')
  }
}

async function handleRemove(templateId: number) {
  try {
    await ElMessageBox.confirm('Remove this template from the release?', 'Warning', { type: 'warning' })
    await releaseStore.removeTemplate(releaseId, templateId)
    ElMessage.success('Template removed')
  } catch { /* cancelled */ }
}

async function handleGenerateChangelog() {
  try {
    const changelog = await releaseStore.generateChangelog(releaseId)
    changelogEdit.value = changelog
    ElMessage.success('Changelog generated')
  } catch {
    ElMessage.error('Generation failed')
  }
}

async function handleSaveChangelog() {
  try {
    await releaseStore.updateRelease(releaseId, { changelog: changelogEdit.value })
    editingChangelog.value = false
    ElMessage.success('Changelog saved')
  } catch {
    ElMessage.error('Save failed')
  }
}

async function handlePublish() {
  try {
    await ElMessageBox.confirm(
      'Publish this release? This will create a GitHub tag and release.',
      'Confirm Publish',
      { type: 'warning' }
    )
    const result = await releaseStore.publishRelease(releaseId)
    ElMessage.success(`Published! Tag: ${result.tag}`)
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || 'Publish failed')
  }
}

onMounted(async () => {
  await releaseStore.fetchRelease(releaseId)
  await templateStore.fetchTemplates()
  if (release.value?.changelog) {
    changelogEdit.value = release.value.changelog
  }
})
</script>

<style scoped>
.page-title { font-size: 18px; font-weight: 600; }
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.changelog-preview {
  max-height: 400px;
  overflow-y: auto;
  font-size: 13px;
  line-height: 1.6;
}
.changelog-preview :deep(h1) { font-size: 18px; }
.changelog-preview :deep(h2) { font-size: 16px; }
.changelog-preview :deep(h3) { font-size: 14px; }
.changelog-preview :deep(ul) { padding-left: 20px; }
</style>

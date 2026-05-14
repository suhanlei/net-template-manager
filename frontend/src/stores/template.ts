import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '../api/modules'
import type { Template, TemplateDetail, TemplateCreate, TemplateUpdate, TemplateVersion, TemplateVersionCreate, TemplateVersionContent, DiffResult } from '../types'

export const useTemplateStore = defineStore('template', () => {
  const templates = ref<Template[]>([])
  const currentTemplate = ref<TemplateDetail | null>(null)
  const versions = ref<TemplateVersion[]>([])
  const loading = ref(false)

  async function fetchTemplates(params?: { category_id?: number; status?: string; page?: number }) {
    loading.value = true
    try {
      templates.value = await api.getTemplates(params)
    } finally {
      loading.value = false
    }
  }

  async function fetchTemplate(id: number) {
    loading.value = true
    try {
      currentTemplate.value = await api.getTemplate(id)
    } finally {
      loading.value = false
    }
  }

  async function createTemplate(data: TemplateCreate) {
    const tpl = await api.createTemplate(data)
    templates.value.unshift(tpl)
    return tpl
  }

  async function updateTemplate(id: number, data: TemplateUpdate) {
    const tpl = await api.updateTemplate(id, data)
    const idx = templates.value.findIndex(t => t.id === id)
    if (idx >= 0) templates.value[idx] = tpl
    return tpl
  }

  async function archiveTemplate(id: number) {
    await api.archiveTemplate(id)
    templates.value = templates.value.filter(t => t.id !== id)
  }

  async function fetchVersions(templateId: number) {
    versions.value = await api.getVersions(templateId)
  }

  async function createVersion(templateId: number, data: TemplateVersionCreate) {
    const tv = await api.createVersion(templateId, data)
    versions.value.unshift(tv)
    return tv
  }

  async function getVersionContent(templateId: number, version: string): Promise<TemplateVersionContent> {
    return api.getVersionContent(templateId, version)
  }

  async function diffVersions(templateId: number, v1: string, v2: string): Promise<DiffResult> {
    return api.diffVersions(templateId, v1, v2)
  }

  async function commitVersion(templateId: number, version: string) {
    return api.commitVersion(templateId, version)
  }

  return {
    templates, currentTemplate, versions, loading,
    fetchTemplates, fetchTemplate, createTemplate, updateTemplate, archiveTemplate,
    fetchVersions, createVersion, getVersionContent, diffVersions, commitVersion,
  }
})

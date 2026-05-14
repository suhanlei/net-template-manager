import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '../api/modules'
import type { Release, ReleaseDetail, ReleaseCreate, ReleaseUpdate, ReleaseTemplateAdd } from '../types'

export const useReleaseStore = defineStore('release', () => {
  const releases = ref<Release[]>([])
  const currentRelease = ref<ReleaseDetail | null>(null)
  const loading = ref(false)

  async function fetchReleases() {
    loading.value = true
    try {
      releases.value = await api.getReleases()
    } finally {
      loading.value = false
    }
  }

  async function fetchRelease(id: number) {
    loading.value = true
    try {
      currentRelease.value = await api.getRelease(id)
    } finally {
      loading.value = false
    }
  }

  async function createRelease(data: ReleaseCreate) {
    const rel = await api.createRelease(data)
    releases.value.unshift(rel)
    return rel
  }

  async function updateRelease(id: number, data: ReleaseUpdate) {
    const rel = await api.updateRelease(id, data)
    const idx = releases.value.findIndex(r => r.id === id)
    if (idx >= 0) releases.value[idx] = rel
    return rel
  }

  async function addTemplate(id: number, data: ReleaseTemplateAdd) {
    await api.addTemplateToRelease(id, data)
    await fetchRelease(id)
  }

  async function removeTemplate(id: number, templateId: number) {
    await api.removeTemplateFromRelease(id, templateId)
    await fetchRelease(id)
  }

  async function generateChangelog(id: number) {
    const result = await api.generateChangelog(id)
    if (currentRelease.value) {
      currentRelease.value.changelog = result.changelog
    }
    return result.changelog
  }

  async function publishRelease(id: number) {
    const result = await api.publishRelease(id)
    await fetchRelease(id)
    return result
  }

  return {
    releases, currentRelease, loading,
    fetchReleases, fetchRelease, createRelease, updateRelease,
    addTemplate, removeTemplate, generateChangelog, publishRelease,
  }
})

import api from '.'
import type {
  Category, CategoryCreate, CategoryUpdate,
  Template, TemplateDetail, TemplateCreate, TemplateUpdate,
  TemplateVersion, TemplateVersionContent, TemplateVersionCreate,
  DiffResult,
  Release, ReleaseDetail, ReleaseCreate, ReleaseUpdate, ReleaseTemplateAdd, Snapshot,
  DashboardStats, GitHubStatus,
} from '../types'

// --- Categories ---
export const getCategories = () => api.get<Category[]>('/categories').then(r => r.data)
export const createCategory = (data: CategoryCreate) => api.post<Category>('/categories', data).then(r => r.data)
export const updateCategory = (id: number, data: CategoryUpdate) => api.put<Category>(`/categories/${id}`, data).then(r => r.data)
export const deleteCategory = (id: number) => api.delete(`/categories/${id}`)

// --- Templates ---
export const getTemplates = (params?: { category_id?: number; status?: string; page?: number; page_size?: number }) =>
  api.get<Template[]>('/templates', { params }).then(r => r.data)
export const createTemplate = (data: TemplateCreate) => api.post<Template>('/templates', data).then(r => r.data)
export const getTemplate = (id: number) => api.get<TemplateDetail>(`/templates/${id}`).then(r => r.data)
export const updateTemplate = (id: number, data: TemplateUpdate) => api.put<Template>(`/templates/${id}`, data).then(r => r.data)
export const archiveTemplate = (id: number) => api.delete(`/templates/${id}`)

// --- Template Versions ---
export const getVersions = (templateId: number) => api.get<TemplateVersion[]>(`/templates/${templateId}/versions`).then(r => r.data)
export const createVersion = (templateId: number, data: TemplateVersionCreate) =>
  api.post<TemplateVersion>(`/templates/${templateId}/versions`, data).then(r => r.data)
export const getVersionContent = (templateId: number, version: string) =>
  api.get<TemplateVersionContent>(`/templates/${templateId}/versions/${version}`).then(r => r.data)
export const diffVersions = (templateId: number, v1: string, v2: string) =>
  api.get<DiffResult>(`/templates/${templateId}/versions/${v1}/diff/${v2}`).then(r => r.data)
export const commitVersion = (templateId: number, version: string) =>
  api.post<{ status: string; commit_sha: string }>(`/templates/${templateId}/versions/${version}/commit`).then(r => r.data)

// --- Releases ---
export const getReleases = () => api.get<Release[]>('/releases').then(r => r.data)
export const createRelease = (data: ReleaseCreate) => api.post<Release>('/releases', data).then(r => r.data)
export const getRelease = (id: number) => api.get<ReleaseDetail>(`/releases/${id}`).then(r => r.data)
export const updateRelease = (id: number, data: ReleaseUpdate) => api.put<Release>(`/releases/${id}`, data).then(r => r.data)
export const addTemplateToRelease = (id: number, data: ReleaseTemplateAdd) =>
  api.post<Snapshot>(`/releases/${id}/add-template`, data).then(r => r.data)
export const removeTemplateFromRelease = (id: number, templateId: number) =>
  api.delete(`/releases/${id}/templates/${templateId}`)
export const generateChangelog = (id: number) =>
  api.post<{ changelog: string }>(`/releases/${id}/generate-changelog`).then(r => r.data)
export const publishRelease = (id: number) =>
  api.post<{ status: string; tag: string; release_url: string }>(`/releases/${id}/publish`).then(r => r.data)

// --- GitHub ---
export const getGitHubStatus = () => api.get<GitHubStatus>('/github/status').then(r => r.data)
export const testGitHubConnection = () => api.post<GitHubStatus>('/github/test-connection').then(r => r.data)
export const getRepoInfo = () => api.get('/github/repo-info').then(r => r.data)
export const syncGitHub = () => api.post('/github/sync').then(r => r.data)

// --- Dashboard ---
export const getDashboardStats = () => api.get<DashboardStats>('/dashboard/stats').then(r => r.data)
export const healthCheck = () => api.get('/health').then(r => r.data)

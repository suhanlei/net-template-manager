export interface Category {
  id: number
  name: string
  slug: string
  description: string | null
  sort_order: number
  template_count: number
  created_at: string
  updated_at: string
}

export interface CategoryCreate {
  name: string
  slug: string
  description?: string | null
  sort_order?: number
}

export interface CategoryUpdate {
  name?: string
  slug?: string
  description?: string | null
  sort_order?: number
}

export interface Template {
  id: number
  name: string
  filename: string
  category_id: number
  category_name: string
  current_version: string | null
  status: string
  github_path: string | null
  created_at: string
  updated_at: string
}

export interface TemplateDetail extends Template {
  versions: TemplateVersion[]
}

export interface TemplateCreate {
  name: string
  filename: string
  category_id: number
  github_path?: string | null
  status?: string
}

export interface TemplateUpdate {
  name?: string
  filename?: string
  category_id?: number
  github_path?: string | null
  status?: string
}

export interface TemplateVersion {
  id: number
  template_id: number
  version: string
  content_hash: string
  change_type: string
  commit_message: string | null
  github_commit_sha: string | null
  status: string
  diff_summary: string | null
  created_by: string
  created_at: string
}

export interface TemplateVersionContent extends TemplateVersion {
  content: string
}

export interface TemplateVersionCreate {
  content: string
  change_type: 'major' | 'minor' | 'patch'
  commit_message?: string | null
  diff_summary?: string | null
  created_by?: string
}

export interface DiffResult {
  template_id: number
  version1: string
  version2: string
  unified_diff: string
}

export interface Release {
  id: number
  name: string
  version: string
  status: string
  changelog: string | null
  release_notes: string | null
  github_tag: string | null
  github_release_url: string | null
  template_count: number
  created_at: string
  updated_at: string
}

export interface ReleaseDetail extends Release {
  snapshots: Snapshot[]
}

export interface Snapshot {
  id: number
  release_id: number
  template_id: number
  template_version_id: number
  template_name: string
  template_filename: string
  version: string
}

export interface ReleaseCreate {
  name: string
  version: string
  release_notes?: string | null
}

export interface ReleaseUpdate {
  name?: string
  changelog?: string | null
  release_notes?: string | null
}

export interface ReleaseTemplateAdd {
  template_id: number
  template_version_id: number
}

export interface DashboardStats {
  counts: {
    templates: number
    versions: number
    releases: number
    categories: number
  }
  recent_templates: Array<{
    id: number
    name: string
    status: string
    current_version: string | null
    updated_at: string
  }>
  recent_logs: Array<{
    id: number
    action: string
    target_type: string
    detail: string | null
    status: string
    created_at: string
  }>
}

export interface GitHubStatus {
  connected: boolean
  user?: string
  repo?: string
  branch?: string
  error?: string
}

<template>
  <el-container class="app-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="app-aside">
      <div class="logo" @click="isCollapse = !isCollapse">
        <span v-if="!isCollapse" class="logo-text">NTM</span>
        <span v-else class="logo-icon">N</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        router
        class="app-menu"
      >
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <template #title>Dashboard</template>
        </el-menu-item>
        <el-menu-item index="/templates">
          <el-icon><Document /></el-icon>
          <template #title>Templates</template>
        </el-menu-item>
        <el-menu-item index="/releases">
          <el-icon><Upload /></el-icon>
          <template #title>Releases</template>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>Settings</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentPage">{{ currentPage }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag :type="githubConnected ? 'success' : 'danger'" effect="dark" size="small">
            GitHub: {{ githubConnected ? 'Connected' : 'Disconnected' }}
          </el-tag>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Odometer, Document, Upload, Setting } from '@element-plus/icons-vue'
import { getGitHubStatus } from '../../api/modules'
import type { GitHubStatus } from '../types'

const route = useRoute()
const isCollapse = ref(false)
const githubConnected = ref(false)

const currentPage = computed(() => {
  const map: Record<string, string> = {
    '/': 'Dashboard',
    '/templates': 'Templates',
    '/releases': 'Releases',
    '/settings': 'Settings',
  }
  return map[route.path] || ''
})

onMounted(async () => {
  try {
    const status: GitHubStatus = await getGitHubStatus()
    githubConnected.value = status.connected
  } catch {
    githubConnected.value = false
  }
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
}
.app-aside {
  background: #304156;
  transition: width 0.3s;
  overflow: hidden;
}
.logo {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  user-select: none;
}
.logo-text { font-size: 22px; }
.logo-icon { font-size: 24px; }
.app-menu {
  border-right: none;
  background: #304156;
}
.app-menu .el-menu-item {
  color: #bfcbd9;
}
.app-menu .el-menu-item.is-active {
  background: #263445;
  color: #409eff;
}
.app-header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 50px;
}
.app-main {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>

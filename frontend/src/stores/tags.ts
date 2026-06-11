import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RouteLocationNormalized } from 'vue-router'

export interface TagItem {
  path: string
  title: string
  closable: boolean
}

export const useTagsStore = defineStore('tags', () => {
  const tags = ref<TagItem[]>([
    { path: '/dashboard', title: '概览', closable: false },
  ])
  const activeTag = ref('/dashboard')

  function addTag(route: RouteLocationNormalized) {
    const title = (route.meta?.title as string) || route.name?.toString() || ''
    if (!title) return

    const exists = tags.value.some((t) => t.path === route.path)
    if (!exists) {
      tags.value.push({ path: route.path, title, closable: true })
    }
    activeTag.value = route.path
  }

  function removeTag(path: string) {
    const idx = tags.value.findIndex((t) => t.path === path)
    if (idx === -1) return

    tags.value.splice(idx, 1)
    if (activeTag.value === path) {
      const next = tags.value[idx] || tags.value[idx - 1]
      activeTag.value = next?.path || '/dashboard'
    }
  }

  function removeOthers(path: string) {
    tags.value = tags.value.filter((t) => !t.closable || t.path === path)
    activeTag.value = path
  }

  function removeAll() {
    tags.value = tags.value.filter((t) => !t.closable)
    activeTag.value = '/dashboard'
  }

  return { tags, activeTag, addTag, removeTag, removeOthers, removeAll }
})

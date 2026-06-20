<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useUserProgress } from './composables/useUserProgress'

const { loadProgress } = useUserProgress()

onMounted(() => {
  loadProgress()
})
</script>

<template>
  <RouterView />
</template>

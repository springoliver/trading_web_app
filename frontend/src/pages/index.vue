<template>
  <div />
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  const token = localStorage.getItem('access_token')
  if (token) {
    router.replace('/trade')
  } else {
    router.replace('/login')
  }
})
</script>

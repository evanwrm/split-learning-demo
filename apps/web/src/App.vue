<script setup lang="ts">
import BackToTop from "@/components/navigation/BackToTop.vue";
import Header from "@/components/templates/Header.vue";
</script>

<template>
    <div class="flex min-h-screen flex-col overflow-clip bg-base-100 text-base-content transition">
        <Header />
        <RouterView />
        <BackToTop />
    </div>
</template>

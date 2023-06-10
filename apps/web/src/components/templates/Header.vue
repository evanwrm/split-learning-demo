<script setup lang="ts">
import ThemeToggle from "@/components/inputs/ThemeToggle.vue";
import { quickRoutes } from "@/config/routes";
import { RouterLink, useRoute } from "vue-router";

const router = useRoute();
</script>

<template>
    <header>
        <nav
            class="flex h-16 w-full items-center justify-center border-b border-base-200 bg-base-100 text-base-content shadow-inner"
        >
            <ul class="container flex items-center p-3">
                <li
                    v-for="route in quickRoutes"
                    :key="route.path"
                    :class="
                        router.path === route.path
                            ? 'border-primary'
                            : 'border-transparent hover:border-primary'
                    "
                    class="mx-1.5 border-b-2 text-base-content opacity-80 transition hover:opacity-100 sm:mx-3"
                >
                    <RouterLink :to="route.path">
                        {{ route.name }}
                    </RouterLink>
                </li>
            </ul>
            <div class="flex items-center justify-center gap-x-3">
                <a
                    href="https://github.com/evanwrm/split-learning-demo"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    <v-icon name="si-github" class="h-6 w-6 opacity-80 hover:opacity-100" />
                </a>
                <ThemeToggle class="h-6 w-6 opacity-80 hover:opacity-100" />
            </div>
        </nav>
    </header>
</template>

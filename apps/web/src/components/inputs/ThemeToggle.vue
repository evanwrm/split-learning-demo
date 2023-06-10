<script setup lang="ts">
import { slideInTopBottomVariants } from "@/lib/animation/variants";
import { useThemeStore } from "@/stores/theme";
import { Motion, Presence } from "motion/vue";

const store = useThemeStore();
</script>
<template>
    <button
        aria-label="Toggle Dark Mode"
        class="flex items-center justify-center transition"
        @click="store.toggleDarkMode()"
    >
        <Presence>
            <Motion
                v-if="store.isDark"
                class="absolute"
                :initial="slideInTopBottomVariants.initial"
                :animate="slideInTopBottomVariants.visible"
                :exit="slideInTopBottomVariants.exit"
                :transition="{ duration: 0.2 }"
            >
                <v-icon name="hi-sun" class="h-6 w-6" />
            </Motion>
        </Presence>
        <Presence>
            <Motion
                v-if="!store.isDark"
                class="absolute"
                :initial="slideInTopBottomVariants.initial"
                :animate="slideInTopBottomVariants.visible"
                :exit="slideInTopBottomVariants.exit"
                :transition="{ duration: 0.2 }"
            >
                <v-icon name="hi-moon" class="h-6 w-6" />
            </Motion>
        </Presence>
    </button>
</template>

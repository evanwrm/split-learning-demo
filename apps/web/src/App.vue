<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import { quickRoutes } from "./config/routes";
</script>

<template>
    <header>
        <div class="wrapper">
            <nav>
                <RouterLink v-for="route in quickRoutes" :key="route.path" :to="route.path">{{
                    route.name
                }}</RouterLink>
            </nav>
        </div>
    </header>
    <RouterView />
</template>

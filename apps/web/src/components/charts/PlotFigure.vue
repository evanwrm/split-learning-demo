<script setup lang="ts">
import * as Plot from "@observablehq/plot";
import type { PropType } from "vue";
import { ref, watchEffect } from "vue";

const props = defineProps({
    options: {
        type: Object as PropType<Plot.PlotOptions>,
        required: true
    }
});

const el = ref<HTMLElement | null>(null);

watchEffect(() => {
    if (!el.value) return;
    el.value.replaceChildren(Plot.plot(props.options));
});
</script>

<template>
    <div ref="el" />
</template>

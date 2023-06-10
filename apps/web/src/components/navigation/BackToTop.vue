<script setup lang="ts">
import { fadePopVariants } from "@/lib/animation/variants";
import { useWindowScroll } from "@vueuse/core";
import { Motion, Presence } from "motion/vue";
import { ref, watchEffect } from "vue";

const { x, y } = useWindowScroll();
const prevScroll = ref({ x: 0, y: 0 });
const velocity = ref(0);

const hidden = ref(true);

watchEffect(() => {
    velocity.value = y.value - prevScroll.value.y;
    prevScroll.value = { x: x.value, y: y.value };
});
watchEffect(() => {
    if (y.value < 100) hidden.value = true;
    else {
        if (velocity.value < 0) hidden.value = false;
        else if (velocity.value > 0) hidden.value = true;
    }
});

const handleClick = (e: MouseEvent) => {
    e.preventDefault();
    scrollTo({ top: 0, behavior: "smooth" });
};
</script>

<template>
    <Teleport to="body">
        <Presence>
            <Motion
                v-if="!hidden"
                tag="button"
                class="btn-ghost btn-circle fixed bottom-6 right-8 z-40 flex select-none items-center justify-center bg-clip-padding shadow shadow-base-content/10"
                :initial="fadePopVariants.hidden"
                :animate="fadePopVariants.visible"
                :exit="fadePopVariants.hidden"
                :transition="{ duration: 0.2 }"
                @onClick="handleClick"
            >
                <div
                    class="inline-flex items-center justify-center rounded-full bg-base-content/10 p-3 text-center"
                >
                    <v-icon name="hi-chevron-up" class="h-6 w-6" />
                </div>
            </Motion>
        </Presence>
    </Teleport>
</template>

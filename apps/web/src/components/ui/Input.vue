<script setup lang="ts">
import { fadePopVariants } from "@/lib/animation/variants";
import { Motion, Presence } from "motion/vue";
import { ref, watchEffect } from "vue";

const props = defineProps({
    value: {
        type: String,
        default: ""
    },
    label: {
        type: String,
        default: ""
    },
    placeholder: {
        type: String,
        default: ""
    },
    disabled: {
        type: Boolean,
        default: false
    },
    error: {
        type: String,
        default: ""
    },
    type: {
        type: String,
        default: "text"
    }
});
const emit = defineEmits(["update:value"]);

const localValue = ref<string>(props.value);
const focused = ref<boolean>(false);
watchEffect(() => {
    localValue.value = props.value;
});

const handleInput = (event: Event) => {
    const inputValue = (event.target as HTMLInputElement)?.value;
    localValue.value = inputValue;
    emit("update:value", inputValue);
};
</script>
<template>
    <div class="flex flex-col">
        <div class="relative ml-1 flex text-xs font-medium text-base-content text-opacity-80">
            <label
                for=""
                class="absolute bottom-1 left-1 transition-all"
                :class="{
                    '!bottom-2': focused
                }"
            >
                {{ label }}
            </label>
        </div>
        <input
            :value="localValue"
            :placeholder="placeholder"
            :disabled="disabled"
            :type="type"
            @input="handleInput"
            @focus="focused = true"
            @blur="focused = false"
            class="flex w-72 items-center justify-between rounded-lg border border-base-300 bg-base-100 px-3 py-2 outline-none ring-base-300 ring-offset-0 transition focus:ring-2 focus:ring-base-300 focus:ring-offset-2 focus:ring-offset-base-100"
            :class="{
                '!border-error': error
            }"
        />
        <Presence>
            <Motion
                v-if="error"
                :initial="fadePopVariants.hidden"
                :animate="fadePopVariants.visible"
                :exit="fadePopVariants.hidden"
                :transition="{ duration: 0.2 }"
                class="ml-1 mt-1 text-xs text-error"
            >
                {{ error }}
            </Motion>
        </Presence>
    </div>
</template>

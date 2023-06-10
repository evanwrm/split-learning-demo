<script setup lang="ts">
import { Checkbox, CheckboxControl, CheckboxInput, CheckboxLabel } from "@ark-ui/vue";

defineProps({
    checked: { type: Boolean, default: false },
    label: {
        type: String
    }
});
defineEmits(["update:checked"]);
</script>
<template>
    <Checkbox
        v-slot="{ isChecked, isIntermediate }"
        :checked="checked"
        @input="$emit('update:checked', $event.target.value)"
        class="flex cursor-pointer items-center justify-center p-2"
    >
        <CheckboxControl
            :class="{ 'bg-base-200': isChecked }"
            class="mr-2 mt-0.5 flex h-6 w-6 items-center justify-center rounded-md border border-base-300"
        >
            <v-icon name="hi-check" v-if="isChecked" class="p-0.5" />
            <v-icon name="hi-minus" v-if="isIntermediate" class="p-0.5" />
        </CheckboxControl>
        <CheckboxInput />
        <CheckboxLabel>{{ label }}</CheckboxLabel>
    </Checkbox>
</template>

<script setup lang="ts">
import {
    SelectOption as ArkSelectOption,
    Select,
    SelectContent,
    SelectLabel,
    SelectOptionGroup,
    SelectOptionGroupLabel,
    SelectPositioner,
    SelectTrigger
} from "@ark-ui/vue";
import { Motion, Presence } from "motion/vue";
import type { PropType } from "vue";
import { computed } from "vue";

export interface SelectOption {
    value: string;
    label?: string;
    group?: string;
}

const props = defineProps({
    label: { type: String },
    placeholder: { type: String, default: "Select option..." },
    options: { type: Array as PropType<SelectOption[]>, required: true },
    selectedOption: { type: String, default: null }
});
defineEmits(["change"]);
const currentOption = computed(() => {
    return props.options.find(option => option.value === props.selectedOption);
});
const optionGroups = computed(() => {
    const groups = new Map<string, SelectOption[]>();
    for (const option of props.options) {
        const group = option.group ?? "";
        if (!groups.has(group)) {
            groups.set(group, []);
        }
        groups.get(group)?.push(option);
    }
    return [...groups];
});
</script>
<template>
    <div class="flex flex-col items-start justify-center">
        <Select
            v-slot="{ selectedOption: arkSelected, isOpen }"
            :selected-option="
                currentOption
                    ? {
                          value: currentOption.value,
                          label: currentOption?.label ?? currentOption.value
                      }
                    : null
            "
            @change="d => d && $emit('change', d.value)"
        >
            <div class="relative ml-1 flex text-xs font-medium text-base-content text-opacity-80">
                <SelectLabel
                    v-if="label"
                    class="absolute bottom-1 left-1 transition-all"
                    :class="{
                        '!bottom-2': isOpen
                    }"
                >
                    {{ label }}
                </SelectLabel>
            </div>
            <SelectTrigger asChild>
                <button
                    class="flex w-72 items-center justify-between rounded-lg border border-base-300 bg-base-100 px-3 py-2 outline-none ring-base-300 ring-offset-0 transition"
                    :class="{
                        'ring-2 ring-base-300 ring-offset-2 ring-offset-base-100': isOpen
                    }"
                >
                    {{ (currentOption ?? arkSelected)?.label ?? placeholder }}
                    <v-icon
                        name="hi-chevron-down"
                        :class="{ '-rotate-180': isOpen }"
                        class="transition"
                    />
                </button>
            </SelectTrigger>
            <Teleport to="body">
                <Presence>
                    <Motion
                        v-show="isOpen"
                        :initial="{ opacity: 0 }"
                        :animate="{ opacity: 1 }"
                        :exit="{ opacity: 0 }"
                        :transition="{ duration: 0.5 }"
                    >
                        <SelectPositioner
                            :class="{ hidden: !isOpen }"
                            class="w-72 rounded-lg border border-base-300 bg-base-100"
                        >
                            <SelectContent>
                                <SelectOptionGroup
                                    v-for="[group, options] in optionGroups"
                                    :key="group"
                                    :id="group"
                                    class="flex flex-col"
                                >
                                    <SelectOptionGroupLabel
                                        v-if="group"
                                        :htmlFor="group"
                                        class="ml-3 mt-2 text-sm font-light"
                                    >
                                        {{ group }}
                                    </SelectOptionGroupLabel>
                                    <ArkSelectOption
                                        v-for="{ value, label } in options"
                                        :key="value as any"
                                        :value="value"
                                        :label="label ? label : value"
                                        class="m-1 cursor-pointer rounded-md bg-base-100 p-2 hover:bg-base-200"
                                        :class="{
                                            'bg-base-200/80': value === currentOption?.value
                                        }"
                                    />
                                    <hr v-if="group !== ''" class="mx-2 my-1 opacity-5" />
                                </SelectOptionGroup>
                            </SelectContent>
                        </SelectPositioner>
                    </Motion>
                </Presence>
            </Teleport>
        </Select>
    </div>
</template>

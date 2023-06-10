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
    selectedOption: { type: Object as PropType<SelectOption | null>, default: null }
});
defineEmits(["update:selectedOption"]);
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
    <Select
        v-slot="{ selectedOption: arkSelected, isOpen }"
        :selected-option="
            selectedOption
                ? {
                      value: selectedOption.value,
                      label: selectedOption?.label ?? selectedOption.value
                  }
                : null
        "
        @input="
            $emit(
                'update:selectedOption',
                options.find(d => d.value === $event.target.value)
            )
        "
    >
        <SelectLabel v-if="label">{{ label }}</SelectLabel>
        <SelectTrigger asChild>
            <button
                class="flex w-72 items-center justify-between rounded-lg border border-base-300 bg-base-100 px-3 py-2"
            >
                {{ (selectedOption ?? arkSelected)?.label ?? placeholder }}
                <v-icon
                    name="hi-chevron-down"
                    :class="{ '-rotate-180': isOpen }"
                    class="transition"
                />
            </button>
        </SelectTrigger>
        <Teleport to="body">
            <SelectPositioner
                :class="{ hidden: !isOpen }"
                class="w-72 rounded-lg border border-base-300"
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
                            :label="label"
                            class="m-1 cursor-pointer rounded-md bg-base-100 p-2 hover:bg-base-200"
                        />
                        <hr v-if="group !== ''" class="mx-2 my-1 opacity-5" />
                    </SelectOptionGroup>
                </SelectContent>
            </SelectPositioner>
        </Teleport>
    </Select>
</template>

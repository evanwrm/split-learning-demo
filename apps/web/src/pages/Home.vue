<script setup lang="ts">
import Checkbox from "@/components/ui/Checkbox.vue";
import Select from "@/components/ui/Select.vue";
</script>

<template>
    <main class="flex h-full w-full flex-1 flex-col items-center justify-center overflow-hidden">
        <section
            class="flex h-full w-full flex-1 flex-col items-center justify-center overflow-hidden px-4"
        >
            <div>
                <span>Hello</span>
                <Select
                    :options="[
                        { value: '1', label: 'One' },
                        { value: '2', label: 'Two' },
                        { value: '3', label: 'Three' }
                    ]"
                />
                <Checkbox label="hello" />
            </div>
        </section>
    </main>
</template>

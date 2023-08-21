<script setup lang="ts">
import PlotFigure from "@/components/charts/PlotFigure.vue";
import DrawingCanvas from "@/components/inputs/DrawingCanvas.vue";
import Select from "@/components/ui/Select.vue";
import { imageDataToGrayscaleF32, rescaleImageData } from "@/lib/utils/image";
import { argmax, softmax } from "@/lib/utils/math";
import { useOnnxStore } from "@/stores/onnx";
import * as Plot from "@observablehq/plot";
import { Tensor } from "onnxruntime-web";
import { ref, watch, watchEffect } from "vue";

const canvasRef = ref<InstanceType<typeof DrawingCanvas> | null>(null);
const imageData = ref<ImageData | null>(null);
const probabilities = ref<number[]>([]);
const prediction = ref<number | null>(null);

const onnx = useOnnxStore();
const dataset = ref<"mnist" | "quickdraw">("mnist");

watch([imageData, () => onnx.session], async () => {
    if (!imageData.value || !onnx.session || onnx.modelLoading) return;

    // preprocess
    const rescaled = rescaleImageData(imageData.value, 28, 28);
    const f32array = imageDataToGrayscaleF32(rescaled);
    const input = new Tensor("float32", f32array, [1, 1, 28, 28]);

    const { output } = await onnx.runModel(input);
    const outputData = [...output.data] as number[];
    const proba = softmax(outputData);
    if (!proba.some(v => v !== 0)) return;
    const predicted = argmax(proba);
    probabilities.value = proba;
    prediction.value = predicted;
});

const saveImage = (data: ImageData) => {
    imageData.value = data;
};

const modelFiles = {
    mnist: "/models/mnist.onnx",
    quickdraw: "/models/quickdraw.onnx"
};
watchEffect(() => onnx.loadModel(modelFiles[dataset.value]));
</script>

<template>
    <main class="flex h-full w-full flex-1 flex-col items-center justify-center overflow-hidden">
        <section
            class="flex h-full w-full flex-1 flex-col items-center justify-center overflow-hidden px-4"
        >
            <Select
                label="Dataset"
                :options="[
                    { value: 'mnist', label: 'MNIST' },
                    { value: 'quickdraw', label: 'QuickDraw' }
                ]"
                :selected-option="dataset"
                @change="d => (dataset = d)"
                class="mb-4"
            />
            <div class="flex">
                <div>
                    <div class="flex items-center justify-center">
                        <DrawingCanvas
                            ref="canvasRef"
                            class="rounded-md border border-base-300 outline-none ring-base-300 ring-offset-0 transition"
                            :class="{
                                'ring-2 ring-secondary ring-offset-2 ring-offset-base-100':
                                    canvasRef?.dirty
                            }"
                            :width="400"
                            :height="400"
                            :line-width="20"
                            stroke="currentColor"
                            background-color="#ffffff00"
                            save-as="data"
                            @update:image="saveImage"
                        />
                        <span
                            v-if="!canvasRef?.dirty"
                            class="pointer-events-none absolute select-none font-semibold text-base-content text-opacity-80"
                        >
                            Start drawing here...
                        </span>
                    </div>
                    <div class="flex gap-2">
                        <button
                            class="mt-2 rounded-lg border border-base-300 px-3 py-2"
                            @click="() => canvasRef?.reset()"
                        >
                            Clear
                        </button>
                    </div>
                </div>
                <div class="flex flex-col items-end justify-center">
                    <span class="text-5xl font-bold">
                        {{ prediction }}
                    </span>
                    <PlotFigure
                        :options="{
                            style: { background: 'transparent' },
                            marks: [Plot.barX(probabilities), Plot.ruleX([0, 1], { opacity: 0 })]
                        }"
                    />
                </div>
            </div>
        </section>
    </main>
</template>

<script setup lang="ts">
import PlotFigure from "@/components/charts/PlotFigure.vue";
import DrawingCanvas from "@/components/inputs/DrawingCanvas.vue";
import Select from "@/components/ui/Select.vue";
import {
    f32Normalize,
    imageDataRescale,
    imageDataToF32,
    imageDataToGrayscale
} from "@/lib/utils/image";
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
const modelPath = ref<string | null>(null);

watch([imageData, () => onnx.session], async () => {
    if (!imageData.value || !onnx.session || onnx.modelLoading) return;

    // preprocess
    const rescaled = imageDataRescale(imageData.value, 28, 28);
    const grayscale = imageDataToGrayscale(rescaled);
    const f32array = imageDataToF32(grayscale);
    const normalized = f32Normalize(f32array, [0.1307], [0.3081]);
    const input = new Tensor("float32", normalized, [1, 1, 28, 28]);
    let image = "";
    for (let i = 0; i < 28; i++) {
        for (let j = 0; j < 28; j++) {
            image += f32array[i * 28 + j];
        }
        image += "\n";
    }
    console.log(image);

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
    mnist: [
        { name: "MNIST", path: "/models/mnist.onnx" },
        { name: "MNIST~old", path: "/models/mnist_default.onnx" }
    ],
    quickdraw: [{ name: "Quickdraw", path: "/models/quickdraw.onnx" }]
};
watchEffect(() => {
    const availableModels = modelFiles[dataset.value];
    const validModel = availableModels.find(m => m.path === modelPath.value);
    const model = validModel && modelPath.value ? modelPath.value : availableModels[0].path;

    modelPath.value = model;
    onnx.loadModel(model);
});
</script>

<template>
    <main class="flex h-full w-full flex-1 flex-col items-center justify-center overflow-hidden">
        <section
            class="flex h-full w-full flex-1 flex-col items-center justify-center overflow-hidden px-4"
        >
            <div class="flex items-center justify-center gap-4">
                <Select
                    label="Backend"
                    :options="[
                        { value: 'wasm', label: 'WASM' },
                        { value: 'webgl', label: 'WebGL' }
                    ]"
                    :selected-option="onnx.sessionBackend"
                    @change="d => onnx.setBackend(d)"
                    class="mb-4"
                />
                <Select
                    label="Model"
                    :options="modelFiles[dataset].map(m => ({ value: m.path, label: m.name }))"
                    :selected-option="modelPath ?? modelFiles[dataset][0].path"
                    @change="d => (modelPath = d)"
                    class="mb-4"
                />
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
            </div>
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

<script setup lang="ts">
import PlotFigure from "@/components/charts/PlotFigure.vue";
import DrawingCanvas from "@/components/inputs/DrawingCanvas.vue";
import Button from "@/components/ui/Button.vue";
import Input from "@/components/ui/Input.vue";
import Select from "@/components/ui/Select.vue";
import { models, type ModelConfig } from "@/config/models";
import {
    f32Normalize,
    imageDataRescale,
    imageDataToF32,
    imageDataToGrayscale
} from "@/lib/utils/image";
import { argmax, softmax } from "@/lib/utils/math";
import { deserializeTensor, serializeTensor } from "@/lib/utils/onnx";
import { useOnnxStore } from "@/stores/onnx";
import { useWebsocketStore } from "@/stores/websocket";
import * as Plot from "@observablehq/plot";
import { Tensor } from "onnxruntime-web";
import { ref, watch, watchEffect } from "vue";

const canvasRef = ref<InstanceType<typeof DrawingCanvas> | null>(null);
const imageData = ref<ImageData | null>(null);
const probabilities = ref<number[]>([]);
const prediction = ref<number | null>(null);

const dataset = ref<"mnist" | "quickdraw">("mnist");
const model = ref<ModelConfig | null>(null);
const parameterServer = ref<string>("ws://127.0.0.1:8000/ws");

const onnx = useOnnxStore();
const websocket = useWebsocketStore();

// prediction
const displayPrediction = (output: Tensor) => {
    const outputData = [...output.data].map(Number);
    const proba = softmax(outputData);
    if (!proba.some(v => v !== 0)) return;
    const predicted = argmax(proba);
    probabilities.value = proba;
    prediction.value = predicted;
};
watch([imageData, () => onnx.session], async () => {
    if (!imageData.value || !onnx.session || onnx.modelLoading) return;

    // preprocess
    const rescaled = imageDataRescale(imageData.value, 28, 28);
    const grayscale = imageDataToGrayscale(rescaled);
    const f32array = imageDataToF32(grayscale);
    const normalized = f32Normalize(f32array, [0.1307], [0.3081]);
    const input = new Tensor("float32", normalized, [1, 1, 28, 28]);

    const modelType = model.value?.type;
    if (modelType === "local") {
        const { output } = await onnx.runModel(input);
        displayPrediction(output);
    } else if (modelType === "splitnn") {
        const { output } = await onnx.runModel(input);
        const message = {
            type: "activations",
            data: { tensor_shape: output.dims },
            raw: { tensor: serializeTensor(output) }
        };
        const json = JSON.stringify(message);
        const b64 = btoa(json);

        const encoder = new TextEncoder();
        const bytes = encoder.encode(b64);
        console.log("Sending message prediction request...");
        websocket.sendMessage(bytes);
    }
});
const saveImage = (data: ImageData) => {
    imageData.value = data;
};

// websocket
const connect = (url: string) => {
    if (websocket.status === "open") websocket.disconnect();
    websocket.connect(url, {
        onMessage: message => {
            const json = atob(message);
            const response = JSON.parse(json);
            if (response.type === "logits") {
                const tensorShape = response.data.tensor_shape;
                const output = deserializeTensor(response.raw.tensor, tensorShape);
                console.log("Received message prediction response...", tensorShape);
                displayPrediction(output);
            }
        }
    });
};
watch(
    [parameterServer],
    () => {
        if (!parameterServer.value || websocket.url === parameterServer.value) return;
        connect(parameterServer.value);
    },
    { immediate: true }
);

// model loading
const selectModel = (path?: string) => {
    const availableModels = models[dataset.value];
    const defaultModel = availableModels[0];
    const validModel = availableModels.find(m => m.path === path);
    const modelConfig = validModel ? validModel : defaultModel;

    model.value = modelConfig;
};
watchEffect(() => {
    selectModel(model.value?.path);
    if (!model.value) return;

    onnx.loadModel(model.value.path);
});
</script>

<template>
    <main class="flex h-full w-full flex-1 flex-col items-center justify-center overflow-hidden">
        <section
            class="flex h-full w-full flex-1 flex-col items-center justify-center overflow-hidden px-4"
        >
            <div class="mt-6 flex flex-col items-center justify-center gap-4 md:mt-2 md:flex-row">
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
                    :options="models[dataset].map(m => ({ value: m.path, label: m.name }))"
                    :selected-option="model ? model.path : models[dataset][0].path"
                    @change="selectModel"
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
                <Input
                    label="Parameter Server"
                    placeholder="Enter server URL"
                    :error="websocket.status === 'closed' ? 'Connection failed' : ''"
                    v-model:value="parameterServer"
                    class="mb-4"
                />
                <Button class="mb-4" @click="() => connect(parameterServer)">Reconnect</Button>
            </div>
            <div class="flex flex-col items-center justify-center md:flex-row">
                <div class="flex flex-col items-start justify-end">
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
                        <Button class="mt-2" @click="() => canvasRef?.reset()">Clear</Button>
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

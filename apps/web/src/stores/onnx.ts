import type { ONNXBackend } from "@/lib/utils/onnx";
import {
    createModelCpu,
    createModelGpu,
    fetchModel,
    runModel as runOnnxModel
} from "@/lib/utils/onnx";
import type { InferenceSession, Tensor } from "onnxruntime-web";
import { defineStore } from "pinia";
import { ref } from "vue";

export const useOnnxStore = defineStore("onnx", () => {
    const sessionBackend = ref<ONNXBackend>("wasm");
    const session = ref<InferenceSession | null>(null);
    const cpuSession = ref<InferenceSession | null>(null);
    const gpuSession = ref<InferenceSession | null>(null);
    const modelLoading = ref(false);
    const modelFile = ref<ArrayBuffer | null>(null);

    const initSession = async (backend: ONNXBackend, modelFile: ArrayBuffer) => {
        modelLoading.value = true;
        try {
            if (backend === "wasm") {
                cpuSession.value = await createModelCpu(modelFile);
                session.value = cpuSession.value;
            } else {
                gpuSession.value = await createModelGpu(modelFile);
                session.value = gpuSession.value;
            }
        } catch (e) {
            console.error(e);
        } finally {
            modelLoading.value = false;
        }
    };

    const setBackend = async (backend: ONNXBackend) => {
        sessionBackend.value = backend;
        if (modelFile.value) {
            initSession(backend, modelFile.value);
        }
    };
    const loadModel = async (modelPath: string) => {
        const model = await fetchModel(modelPath);
        modelFile.value = model;

        initSession(sessionBackend.value, model);
    };
    const runModel = async (input: Tensor) => {
        if (!session.value) throw new Error("No session loaded");

        return await runOnnxModel(session.value, input);
    };

    return {
        sessionBackend,
        session,
        cpuSession,
        gpuSession,
        modelLoading,
        modelFile,
        setBackend,
        loadModel,
        runModel
    };
});

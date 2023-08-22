import { arrayToB64, b64ToArray } from "@/lib/utils/serde";
import { InferenceSession, Tensor } from "onnxruntime-web";

export type ONNXBackend = "wasm" | "webgl";

const init = () => {
    // env.wasm.simd = false;
};

export const createModelCpu = async (model: ArrayBuffer): Promise<InferenceSession> => {
    init();
    return await InferenceSession.create(model, { executionProviders: ["wasm"] });
};
export const createModelGpu = async (model: ArrayBuffer): Promise<InferenceSession> => {
    init();
    return await InferenceSession.create(model, { executionProviders: ["webgl"] });
};

export const runModel = async (
    model: InferenceSession,
    preprocessedData: Tensor
): Promise<{ output: Tensor; inferenceTime: number }> => {
    try {
        const start = Date.now();
        const feeds = { [model.inputNames[0]]: preprocessedData };
        const outputData = await model.run(feeds);
        const inferenceTime = Date.now() - start;

        return {
            output: outputData[model.outputNames[0]],
            inferenceTime
        };
    } catch (e) {
        console.error(e);
        throw new Error("Failed to run model");
    }
};
export const fetchModel = async (modelPath: string) => {
    const res = await fetch(modelPath);
    return await res.arrayBuffer();
};

export const serializeTensor = (tensor: Tensor) => {
    return arrayToB64(tensor.data as any);
};
export const deserializeTensor = (b64: string, shape: number[], type: Tensor.Type = "float32") => {
    const array = b64ToArray(b64, type as any);
    return new Tensor(type, array as any, shape);
};

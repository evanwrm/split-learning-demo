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

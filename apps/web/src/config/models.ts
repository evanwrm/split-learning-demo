export type ModelType = "splitnn" | "local";
export interface ModelConfig {
    type: ModelType;
    name: string;
    path: string;
}

export const models: Record<string, ModelConfig[]> = {
    mnist: [
        { name: "LeNet-5", path: "/models/mnist.onnx", type: "local" },
        { name: "ORT Demo", path: "/models/mnist_default.onnx", type: "local" },
        { name: "LeNet-5 SplitNN", path: "/models/client_mnist.onnx", type: "splitnn" }
    ],
    quickdraw: [{ name: "LeNet-5", path: "/models/quickdraw.onnx", type: "local" }]
};

import { createCanvas } from "@/lib/utils/dom";

export const imageDataRescale = (imageData: ImageData, width: number, height: number) => {
    const { canvas: tempCanvas, ctx: tempCtx } = createCanvas(imageData.width, imageData.height);
    tempCtx.putImageData(imageData, 0, 0);

    const { ctx } = createCanvas(width, height);
    ctx.drawImage(tempCanvas, 0, 0, width, height);
    const imageDataScaled = ctx.getImageData(0, 0, width, height);

    return imageDataScaled;
};

export const imageDataToGrayscale = (imageData: ImageData) => {
    const channels = imageData.data.length / (imageData.width * imageData.height);
    const size = imageData.data.length / channels;
    const array = new ImageData(imageData.width, imageData.height);
    for (let i = 0; i < size; i++) {
        const gray = imageData.data[i * channels + 3];
        // const gray = 0.299 * imageData.data[i] + 0.587 * imageData.data[i + 1] + 0.114 * imageData.data[i + 2];
        array.data[i] = gray;
        array.data[i + 1] = gray;
        array.data[i + 2] = gray;
        array.data[i + 3] = imageData.data[i * channels + 3];
    }
    return array;
};

export const f32ToGrayscale = (f32: Float32Array, channels = 3) => {
    const size = f32.length / channels;
    const array = new Float32Array(size);
    for (let i = 0; i < size; i++) {
        const gray = 0.299 * f32[i] + 0.587 * f32[i + 1] + 0.114 * f32[i + 2];
        array[i] = gray;
        array[i + 1] = gray;
        array[i + 2] = gray;
    }
    return array;
};

export const imageDataNormalize = (imageData: ImageData, mean: number[], std: number[]) => {
    const channels = imageData.data.length / (imageData.width * imageData.height);
    const size = imageData.data.length / channels;
    const array = new ImageData(imageData.width, imageData.height);
    for (let i = 0; i < size; i++) {
        for (let c = 0; c < channels; c++) {
            array.data[i * channels + c] = (imageData.data[i * channels + c] - mean[c]) / std[c];
        }
    }
    return array;
};

export const f32Normalize = (f32: Float32Array, mean: number[], std: number[]) => {
    const channels = Math.max(mean.length, std.length);
    const size = f32.length / channels;
    const array = new Float32Array(size);
    for (let i = 0; i < size; i++) {
        for (let c = 0; c < channels; c++) {
            array[i * channels + c] = (f32[i * channels + c] - mean[c]) / std[c];
        }
    }
    return array;
};

export const imageDataToF32 = (imageData: ImageData) => {
    const channels = imageData.data.length / (imageData.width * imageData.height);
    const size = imageData.data.length / channels;
    const array = new Float32Array(size);
    for (let i = 0; i < size; i++) {
        for (let c = 0; c < channels; c++) {
            array[i * channels + c] = imageData.data[i * channels + c] / 255;
        }
    }
    return array;
};

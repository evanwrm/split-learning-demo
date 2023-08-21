import { createCanvas } from "@/lib/utils/dom";

export const rescaleImageData = (imageData: ImageData, width: number, height: number) => {
    const { canvas: tempCanvas, ctx: tempCtx } = createCanvas(imageData.width, imageData.height);
    tempCtx.putImageData(imageData, 0, 0);

    const { canvas, ctx } = createCanvas(width, height);
    ctx.drawImage(tempCanvas, 0, 0, width, height);
    const imageDataScaled = ctx.getImageData(0, 0, width, height);

    return imageDataScaled;
};

export const imageDataToGrayscaleF32 = (imageData: ImageData) => {
    const channels = imageData.data.length / (imageData.width * imageData.height);
    const size = imageData.data.length / channels;
    const array = new Float32Array(size);
    for (let i = 0; i < size; i++) {
        array[i] = imageData.data[i * channels + 3] / 255;
    }
    return array;
};

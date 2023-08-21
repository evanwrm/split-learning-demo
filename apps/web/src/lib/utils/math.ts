export const softmax = (arr: number[]) => {
    const C = Math.max(...arr);
    const d = arr.map(y => Math.exp(y - C)).reduce((a, b) => a + b);
    return arr.map((value, _index) => {
        return Math.exp(value - C) / d;
    });
};

export const argmax = (output: number[]) => {
    return output.reduce(
        (maxIndex, item, index) => (item > output[maxIndex] ? index : maxIndex),
        0
    );
};

const dataTypes = {
    float32: Float32Array,
    uint8: Uint8Array,
    int8: Int8Array,
    uint16: Uint16Array,
    int16: Int16Array,
    int32: Int32Array,
    int64: BigInt64Array,
    bool: Uint8Array,
    float64: Float64Array,
    uint32: Uint32Array,
    uint64: BigUint64Array
};

export const arrayToB64 = (array: ArrayBufferView) => {
    const bytes = new Uint8Array(array.buffer);
    const binary = String.fromCharCode.apply(null, bytes as any);
    return btoa(binary);
};

export const b64ToArray = (
    str: string,
    constructor: { new (buffer: ArrayBuffer): ArrayBufferView } | keyof typeof dataTypes
) => {
    const binary = atob(str);
    const buffer = new ArrayBuffer(binary.length);
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    const ctor = typeof constructor === "string" ? dataTypes[constructor] : constructor;
    return new ctor(buffer);
};

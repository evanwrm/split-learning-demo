<script setup lang="ts">
// Inspired from: https://github.com/razztyfication/vue-drawing-canvas
import { createCanvas } from "@/lib/utils/dom";
import { computed, onMounted, ref } from "vue";

const props = defineProps({
    canvasId: { type: String },
    width: {
        type: Number,
        default: 600
    },
    height: {
        type: Number,
        default: 400
    },
    backgroundColor: {
        type: String,
        default: "#ffffff"
    },
    stroke: {
        type: String,
        default: "#000000"
    },
    lineWidth: {
        type: Number,
        default: 20
    },
    lineCap: {
        type: String,
        validator: (value: string) => ["round", "square", "butt"].includes(value),
        default: "round"
    },
    lineJoin: {
        type: String,
        validator: (value: string) => ["round", "bevel", "miter"].includes(value),
        default: "round"
    },
    disabled: { type: Boolean, default: false },
    saveAs: {
        type: String,
        validator: (value: string) => ["png", "jpeg", "data"].includes(value),
        default: "png"
    },
    autoSave: { type: Boolean, default: true },
    outputWidth: { type: Number },
    outputHeight: { type: Number }
});
const emit = defineEmits(["update:image"]);

const canvas = ref<HTMLCanvasElement | null>(null);
const ctx = ref<CanvasRenderingContext2D | null>(null);

interface DrawingAction {
    stroke: string;
    lineWidth: number;
    lineCap: "round" | "square" | "butt";
    lineJoin: "round" | "bevel" | "miter";
    coordinates: { x: number; y: number }[];
}
const actions = ref<DrawingAction[]>([]);
const dirty = computed(() => actions.value.length > 0);
const drawing = ref(false);

// helpers
const getCanvas = () => {
    if (!canvas.value) throw new Error("Could not get canvas element");
    return canvas.value;
};
const getContext = () => {
    if (!ctx.value) throw new Error("Could not get context of canvas");
    return ctx.value;
};
const initContext = () => {
    const canvas = getCanvas();
    if (!ctx.value) ctx.value = canvas.getContext("2d");
};
const getCoordinates = (e: PointerEvent | TouchEvent) => {
    if (e instanceof TouchEvent) {
        const canvas = getCanvas();
        const rect = canvas.getBoundingClientRect();
        const touch = e.touches[0];
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        return { x, y };
    } else {
        const x = e.offsetX;
        const y = e.offsetY;
        return { x, y };
    }
};

// drawing
const startDraw = (e: PointerEvent | TouchEvent) => {
    if (props.disabled) return;

    const { x, y } = getCoordinates(e);
    drawing.value = true;

    const strokeStyle =
        props.stroke.toLowerCase() === "currentcolor"
            ? window.getComputedStyle(canvas.value!).color
            : props.stroke;
    actions.value.push({
        stroke: strokeStyle,
        lineWidth: props.lineWidth,
        lineCap: props.lineCap as any,
        lineJoin: props.lineJoin as any,
        coordinates: [{ x, y }]
    });
};
const stopDraw = (e: PointerEvent | TouchEvent) => {
    if (
        actions.value.length > 0 &&
        actions.value[actions.value.length - 1].coordinates.length === 1
    ) {
        draw(e);
    }

    // auto save
    if (props.autoSave && drawing.value) {
        setTimeout(() => {
            if (!drawing.value) save();
        }, 100);
    }

    drawing.value = false;
};
const draw = (e: PointerEvent | TouchEvent) => {
    if (!drawing.value) return;

    const { x, y } = getCoordinates(e);
    const lastAction = actions.value[actions.value.length - 1];
    lastAction.coordinates.push({ x, y });

    const ctx = getContext();

    ctx.beginPath();
    ctx.setLineDash([]);
    for (const action of actions.value) {
        ctx.strokeStyle = action.stroke;
        ctx.fillStyle = action.stroke;
        ctx.lineWidth = action.lineWidth;
        ctx.lineCap = action.lineCap;
        ctx.lineJoin = action.lineJoin;

        const from = action.coordinates[0];

        ctx.moveTo(from.x, from.y);
        for (const { x, y } of action.coordinates) {
            ctx.lineTo(x, y);
        }
        ctx.stroke(); // ctx.fill()
    }
};
const clear = () => {
    const ctx = getContext();
    ctx.clearRect(0, 0, canvas.value?.width ?? props.width, canvas.value?.height ?? props.height);
};
const drawBackground = () => {
    const ctx = getContext();
    clear();
    ctx.fillStyle = props.backgroundColor;
    ctx.fillRect(0, 0, canvas.value?.width ?? props.width, canvas.value?.height ?? props.height);
    save();
};
const reset = () => {
    actions.value = [];
    drawBackground();
};

// save
const save = () => {
    const canvas = getCanvas();
    const { canvas: tempCanvas, ctx: tempCtx } = createCanvas(
        props.outputWidth ?? canvas.width,
        props.outputHeight ?? canvas.height
    );

    tempCtx.drawImage(canvas, 0, 0, tempCanvas.width, tempCanvas.height);
    if (["png", "jpeg"].includes(props.saveAs)) {
        const image = tempCanvas.toDataURL(`image/${props.saveAs}`, 1);
        emit("update:image", image);
        return image;
    } else if (["data"].includes(props.saveAs)) {
        const image = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
        emit("update:image", image);
        return image;
    }
    throw new Error("Invalid saveAs value");
};

onMounted(() => {
    if (canvas.value) {
        initContext();
        reset();
    }
});
defineExpose({ save, reset, drawing, dirty });
</script>

<template>
    <canvas
        ref="canvas"
        :id="canvasId"
        :width="width"
        :height="height"
        @touchstart="startDraw"
        @touchmove="draw"
        @touchend="stopDraw"
        @touchleave="stopDraw"
        @touchcancel="stopDraw"
        @pointerdown="startDraw"
        @pointermove="draw"
        @pointerup="stopDraw"
        @pointerleave="stopDraw"
        @pointercancel="stopDraw"
        class="cursor-auto touch-none"
    >
        Your browser does not support the canvas element.
    </canvas>
</template>

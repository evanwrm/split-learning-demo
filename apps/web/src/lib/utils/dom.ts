type ContextType = {
    "2d": CanvasRenderingContext2D;
    bitmaprenderer: ImageBitmapRenderingContext;
    webgl: WebGLRenderingContext;
    webgl2: WebGL2RenderingContext;
};

const defaultContext: keyof ContextType = "2d";
export const createCanvas = <T extends keyof ContextType = typeof defaultContext>(
    width: number,
    height: number,
    context?: T
): { canvas: HTMLCanvasElement; ctx: ContextType[T] } => {
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;

    const contextType = context ?? defaultContext;
    const ctx = canvas.getContext(contextType) as ContextType[T];
    if (!ctx) throw new Error("Could not get canvas context");

    return { canvas, ctx };
};

type Variant = {
    [key: string]: any;
};

// Variants
export const fadePopVariants: Record<string, Variant> = {
    hidden: { scale: 0, opacity: 0 },
    visible: { scale: 1, opacity: 1 }
};
export const slideFadeRightVariants: Record<string, Variant> = {
    hidden: { x: 25, opacity: 0 },
    visible: { x: 0, opacity: 1 }
};
export const slideFadeLeftOffscreenVariants: Record<string, Variant> = {
    hidden: { x: -400, opacity: 0 },
    visible: { x: 0, opacity: 1 }
};
export const slideInTopVariants: Record<string, Variant> = {
    hidden: { y: -75, opacity: 0 },
    visible: { y: 0.1, opacity: 1 }
};
export const slideInTopBottomVariants: Record<string, Variant> = {
    initial: { y: -20, opacity: 0 },
    exit: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
};
export const buttonVariants: Record<string, Variant> = {
    hover: { scale: 1.1, opacity: 1, y: -4 },
    tap: { scale: 0.9, opacity: 1 }
};

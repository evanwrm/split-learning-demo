import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useWebsocketStore = defineStore("websockets", () => {
    const socket = ref<WebSocket | undefined>(undefined);
    const status = ref<"connecting" | "open" | "closed">("closed");
    const url = computed(() => socket.value?.url);
    const errors = ref<Event[]>([]);

    const disconnect = () => {
        if (socket.value) socket.value.close();
    };
    const connect = (
        url: string,
        options?: {
            onOpen?: () => void;
            onMessage?: (data: string) => void;
            onClose?: () => void;
            onError?: (error: Event) => void;
        }
    ) => {
        const websocket = new WebSocket(url);

        websocket.onopen = () => {
            status.value = "open";
            options?.onOpen?.();
        };
        websocket.onmessage = event => {
            const data = event.data;

            if (typeof data === "string") {
                options?.onMessage?.(data);
            } else if (data instanceof ArrayBuffer) {
                const decoder = new TextDecoder();
                const decoded = decoder.decode(data);
                options?.onMessage?.(decoded);
            } else if (data instanceof Blob) {
                const reader = new FileReader();
                reader.onload = () => {
                    const decoded = reader.result as string;
                    options?.onMessage?.(decoded);
                };
                reader.readAsText(data);
            }
        };
        websocket.onclose = () => {
            options?.onClose?.();
            socket.value = undefined;
            status.value = "closed";
            errors.value = [];
        };
        websocket.onerror = error => {
            errors.value.push(error);
            options?.onError?.(error);
        };

        socket.value = websocket;
        status.value = "connecting";
    };
    const sendMessage = (message: string | ArrayBufferLike | Blob | ArrayBufferView) => {
        if (socket.value && socket.value.readyState === WebSocket.OPEN) {
            socket.value.send(message);
        }
    };

    return {
        url,
        status,
        errors,
        connect,
        sendMessage,
        disconnect
    };
});

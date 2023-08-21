import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        viteStaticCopy({
            targets: [
                {
                    src: "node_modules/onnxruntime-web/dist/*.wasm",
                    dest: "."
                }
            ]
        })
    ],
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url))
        }
    },
    optimizeDeps: {
        exclude: ["oh-vue-icons/icons"]
    }
});

import { defineStore } from "pinia";
import { computed, ref } from "vue";

const isServer = typeof window === "undefined";
const defaultTheme = "system";
const storageKey = "theme";
const attribute = "data-theme";

// helpers
export const colorSchemes = ["light", "dark"];
export const MEDIA = "(prefers-color-scheme: dark)";

export const getTheme = (key: string, fallback?: string) => {
    if (isServer) return undefined;
    let theme;
    try {
        theme = localStorage.getItem(key) ?? undefined;
    } catch (e) {
        // pass
    }
    return theme ?? fallback;
};
export const applyTheme = (newTheme: string, attribute: string, fallback?: string) => {
    if (attribute === "class") {
        document.documentElement.classList.remove(...colorSchemes);
        if (newTheme) document.documentElement.classList.add(newTheme);
    } else {
        if (newTheme) document.documentElement.setAttribute(attribute, newTheme);
        else document.documentElement.removeAttribute(attribute);
    }

    const fallbackScheme = colorSchemes.includes(fallback ?? "") ? fallback : null;
    const colorScheme = colorSchemes.includes(newTheme) ? newTheme : fallbackScheme;
    // @ts-ignore
    document.documentElement.style.colorScheme = colorScheme;
};
export const getSystemTheme = (e?: MediaQueryList | MediaQueryListEvent) => {
    if (!e) e = window.matchMedia(MEDIA);
    return e.matches ? "dark" : "light";
};

export const useThemeStore = defineStore("theme", () => {
    const theme = ref("theme");
    const resolvedTheme = computed(() =>
        theme.value === "system" ? getSystemTheme() : theme.value
    );
    const isDark = computed(() => resolvedTheme.value === "dark");

    const setTheme = (newTheme: string) => {
        applyTheme(newTheme, attribute, defaultTheme);
        theme.value = newTheme;
        try {
            localStorage.setItem(storageKey, newTheme);
        } catch (e) {
            // pass
        }
    };
    const toggleDarkMode = () => {
        if (isDark.value) setTheme("light");
        else setTheme("dark");
    };

    const handleStorage = (e: StorageEvent) => {
        if (e.key !== storageKey) return;
        // If default theme set, use it if localstorage === null (happens on local storage manual deletion)
        const theme = e.newValue ?? defaultTheme!;
        setTheme(theme);
    };
    const handleMediaQuery = (e: MediaQueryListEvent | MediaQueryList) => {
        setTheme(getSystemTheme(e));
    };

    const media = window.matchMedia(MEDIA);
    media.addListener(handleMediaQuery);
    window.addEventListener("storage", handleStorage);
    setTheme(getTheme(storageKey, defaultTheme) ?? getSystemTheme(media));

    return { theme, resolvedTheme, isDark, setTheme, toggleDarkMode };
});

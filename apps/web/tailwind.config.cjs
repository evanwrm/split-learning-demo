const { fontFamily } = require("tailwindcss/defaultTheme");

/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./src/**/*.{vue,html,js,jsx,ts,tsx}"],
    theme: {
        extend: {
            fontFamily: {
                sans: ["Inter", ...fontFamily.sans],
                mono: ["var(--font-mono)", ...fontFamily.mono]
            }
        }
    },
    plugins: [require("daisyui"), require("@tailwindcss/typography")],
    daisyui: {
        themes: [
            {
                light: {
                    primary: "#ed3b53",
                    secondary: "#13acf2",
                    accent: "#e9411a",
                    neutral: "#eaeaea",
                    "base-100": "#ffffff",
                    "base-200": "#ededed",
                    "base-300": "#dbdbdb",
                    "--rounded-box": "0.5rem",
                    "--rounded-btn": ".25rem"
                }
            },
            {
                dark: {
                    primary: "#ed3b53",
                    secondary: "#13acf2",
                    accent: "#e9411a",
                    neutral: "#1a1a1a",
                    "base-100": "#070707",
                    "base-200": "#151515",
                    "base-300": "#232323",
                    info: "#66c6ff",
                    success: "#87d039",
                    warning: "#e2d562",
                    error: "#ff6f6f",
                    "--rounded-box": "0.5rem",
                    "--rounded-btn": ".25rem"
                }
            }
        ]
    }
};

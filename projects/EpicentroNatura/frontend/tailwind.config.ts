import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        natura: {
          50: "#f2f8f4",
          100: "#e1efe6",
          200: "#c4dfcf",
          300: "#9ac8b0",
          400: "#6aa98c",
          500: "#498e70",
          600: "#377259",
          700: "#2d5b48",
          800: "#274a3c",
          900: "#223d32",
          950: "#0f221c",
        },
        earth: {
          50: "#fdf8f4",
          100: "#f9ede2",
          200: "#f2d8c3",
          300: "#e8bd9b",
          400: "#dc9c71",
          500: "#d38050",
          600: "#c56844",
          700: "#a4513a",
          800: "#844234",
          900: "#6d382d",
        }
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;

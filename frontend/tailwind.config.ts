import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
      colors: {
        warm: {
          gray: "#F7F6F3",
        },
        teal: {
          DEFAULT: "#00B894",
          light: "#F0FAF6",
          dark: "#00897B",
        },
        primary: {
          50: "#F0FAF6",
          100: "#ccfbf1",
          200: "#99f6e4",
          300: "#5eead4",
          400: "#2dd4bf",
          500: "#00B894",
          600: "#00897B",
          700: "#0f766e",
          800: "#115e59",
          900: "#134e4a",
        },
        surface: {
          50: "#fafafa",
          100: "#f4f4f5",
          200: "#e4e4e7",
          300: "#d4d4d8",
          400: "#a1a1aa",
          500: "#71717a",
        },
      },
      spacing: {
        "18": "4.5rem",
        "22": "5.5rem",
      },
      borderRadius: {
        "xl": "0.875rem",
        "2xl": "1rem",
        "3xl": "1.25rem",
      },
      boxShadow: {
        soft: "0 2px 15px -3px rgba(0,0,0,0.07), 0 10px 20px -2px rgba(0,0,0,0.04)",
        card: "0 1px 3px 0 rgba(0,0,0,0.06), 0 1px 2px -1px rgba(0,0,0,0.06)",
        "card-hover": "0 4px 20px -4px rgba(0,0,0,0.08), 0 4px 12px -2px rgba(0,0,0,0.04)",
        glow: "0 0 0 3px rgba(0, 184, 148, 0.35)",
        "glow-strong": "0 0 0 4px rgba(0, 184, 148, 0.4)",
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-out forwards",
        "fade-in-delay": "fadeIn 0.6s ease-out 0.2s forwards",
        "slide-up": "slideUp 0.4s ease-out forwards",
        "slide-up-slow": "slideUp 0.5s ease-out forwards",
        "pulse-oval": "pulseOval 2s ease-in-out infinite",
        "shimmer": "shimmer 2s ease-in-out",
        "ring-glow": "ringGlow 1.2s ease-in-out infinite",
        ripple: "ripple 0.5s ease-out forwards",
      },
      keyframes: {
        ripple: {
          "0%": { transform: "translate(-50%, -50%) scale(0)", opacity: "0.5" },
          "100%": { transform: "translate(-50%, -50%) scale(1)", opacity: "0" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseOval: {
          "0%, 100%": { opacity: "0.7" },
          "50%": { opacity: "1" },
        },
        ringGlow: {
          "0%, 100%": { boxShadow: "0 0 0 2px rgba(0, 184, 148, 0.3)" },
          "50%": { boxShadow: "0 0 0 6px rgba(0, 184, 148, 0.2)" },
        },
      },
      transitionDuration: {
        "250": "250ms",
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
      },
    },
  },
  plugins: [],
};
export default config;

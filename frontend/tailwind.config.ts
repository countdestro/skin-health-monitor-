import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        skin: {
          excellent: "#2ECC71",
          good: "#A9DFBF",
          fair: "#F39C12",
          moderate: "#E67E22",
          poor: "#E74C3C",
          severe: "#922B21",
        },
      },
    },
  },
  plugins: [],
};
export default config;

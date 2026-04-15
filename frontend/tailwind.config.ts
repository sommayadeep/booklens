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
        ink: "#111111",
        body: "#555555",
        muted: "#999999",
        sand: "#ece4db",
        clay: "#d9cec1",
        fog: "#f7f4ef",
        smoke: "#cbc3bb",
        accent: "#6f6276",
      },
      boxShadow: {
        glass: "0 12px 34px rgba(30, 20, 10, 0.10)",
        float: "0 24px 48px rgba(20, 15, 10, 0.08)",
      },
      borderRadius: {
        panel: "22px",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.35" },
          "50%": { opacity: "0.9" },
        },
      },
      animation: {
        fadeUp: "fadeUp 420ms ease-out",
        pulseSoft: "pulseSoft 1.2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;

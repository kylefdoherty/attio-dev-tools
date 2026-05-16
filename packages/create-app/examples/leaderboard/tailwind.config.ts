import type { Config } from "tailwindcss";
import tailwindcssAnimate from "tailwindcss-animate";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        gold: {
          DEFAULT: "#FFD700",
          muted: "#B8860B",
        },
        silver: {
          DEFAULT: "#C0C0C0",
          muted: "#808080",
        },
        bronze: {
          DEFAULT: "#CD7F32",
          muted: "#8B4513",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "rank-shift": {
          "0%": { transform: "translateY(-4px)", opacity: "0.7" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "count-up": {
          "0%": { transform: "scale(0.95)", opacity: "0.5" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        "pulse-gold": {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(255, 215, 0, 0.4)" },
          "50%": { boxShadow: "0 0 0 8px rgba(255, 215, 0, 0)" },
        },
      },
      animation: {
        "rank-shift": "rank-shift 0.3s ease-out",
        "count-up": "count-up 0.4s ease-out",
        "pulse-gold": "pulse-gold 2s infinite",
      },
    },
  },
  plugins: [tailwindcssAnimate],
};

export default config;

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F6F1E7",
        "paper-shade": "#EDE4D0",
        "paper-card": "#FBF8F1",
        rule: "#D8CBAE",
        ink: "#22201B",
        "ink-soft": "#6F6656",
        "slot-blue": "#2E5C88",
        ochre: "#9C6B2E",
        "postal-green": "#3F7A4E",
        "stamp-red": "#B5402F",
        kraft: "#8C6A3F",
        "digest-border": "#C9B689",
        "digest-notch": "#DED0AC",
      },
      fontFamily: {
        title: ["Cinzel", "Fraunces", "Georgia", "serif"],
        serif: ["Fraunces", "Georgia", "serif"],
        sans: ["IBM Plex Sans", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "Menlo", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(34,32,27,0.06), 0 6px 16px rgba(34,32,27,0.05)",
        modal: "0 12px 32px rgba(34,32,27,0.25)",
      },
      keyframes: {
        cardFlash: {
          "0%": { backgroundColor: "#E4EEF6" },
          "100%": { backgroundColor: "#FBF8F1" },
        },
        stampDown: {
          "0%": { transform: "rotate(-9deg) scale(1.9)", opacity: "0" },
          "70%": { opacity: "1" },
          "100%": { transform: "rotate(-9deg) scale(1)", opacity: "1" },
        },
        pulse: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.25" },
        },
      },
      animation: {
        cardFlash: "cardFlash 1.1s ease",
        stampDown: "stampDown 0.4s cubic-bezier(0.2, 1.4, 0.4, 1)",
        pulse: "pulse 1s infinite",
      },
      screens: {
        stack: { max: "880px" },
      },
    },
  },
  plugins: [],
};

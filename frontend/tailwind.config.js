/** @type {import('tailwindcss').Config} */
export default {
  content: [
  './index.html',
  './src/**/*.{js,ts,jsx,tsx}'
],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        forest: {
          DEFAULT: "#1B4332",
          light: "#2D6A4F",
          dark: "#0D2B1F",
        },
        gold: {
          DEFAULT: "#D4AF37",
          light: "#F0D060",
          dark: "#A88B20",
        },
        cream: "#F8FAF7",
      },
      fontFamily: {
        heading: ["Playfair Display", "Georgia", "serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 2px 16px rgba(27, 67, 50, 0.08)",
        "card-hover": "0 8px 32px rgba(27, 67, 50, 0.16)",
        gold: "0 0 0 2px rgba(212, 175, 55, 0.4)",
      },
    },
  },
  plugins: [],
};

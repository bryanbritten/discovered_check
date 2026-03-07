/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        chess: {
          dark: "#1a1a2e",
          darker: "#16213e",
          accent: "#e2b96f",
          "accent-dark": "#c9a05a",
          light: "#f0d9b5",
          board: "#b58863",
        },
      },
    },
  },
  plugins: [],
};

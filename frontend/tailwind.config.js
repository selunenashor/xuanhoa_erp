/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        xh: {
          red: '#CB2026',      // Cardinal Red - Primary
          gold: '#ECB34C',     // Ronchi Gold - Accent  
          black: '#030303',    // Text
        }
      }
    },
  },
  plugins: [],
}

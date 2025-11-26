/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand Colors
        primary: {
          DEFAULT: '#055568',
          light: '#2090AC',
        },
        secondary: {
          DEFAULT: '#33CAB1',
          dark: '#25A590',
        },
        // Accent Colors
        accent: {
          cyan: '#6CFFFE',
          blue: '#07D0C9',
          'dark-blue': '#263B95',
        },
        // Semantic Colors
        error: '#F12B2B',
        success: '#33CAB1',
        warning: '#FF9800',
        info: '#2090AC',
        // Grayscale
        gray: {
          50: '#F5F5F5',
          100: '#F2F2F2',
          200: '#E5E5E5',
          300: '#DDDDDD',
          400: '#999999',
          500: '#666666',
          600: '#444444',
          700: '#333333',
          800: '#222222',
          900: '#111111',
        }
      }
    },
  },
  plugins: [],
}

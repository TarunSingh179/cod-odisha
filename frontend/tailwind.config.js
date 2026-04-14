/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Odisha Nature Palette
        odisha: {
          primary: '#2D5A3D',      // Deep forest green
          secondary: '#4A7C59',     // Sage green
          accent: '#FF8C00',         // Tiger orange
          water: '#0080C8',          // Chilika blue
          mangrove: '#00B496',       // Mangrove teal
          paddy: '#50C850',          // Fresh green
          earth: '#8B4513',          // Forest brown
          sand: '#D4B896',           // Dry leaf
          cream: '#F5F0E8',          // Off-white
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

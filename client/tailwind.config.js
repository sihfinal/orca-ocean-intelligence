/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ocean: {
          950: '#030712',
          900: '#050E1F',
          850: '#08162E',
          800: '#0C1E3D',
          700: '#142E5C',
          cyan: '#00F0FF',
          teal: '#00D1B2',
          emerald: '#10B981',
          amber: '#F59E0B',
          rose: '#EF4444',
          isro: '#FF9933',
        }
      },
      animation: {
        'pulse-glow': 'pulseGlow 2.5s infinite',
        'radar-sweep': 'radarSweep 4s linear infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: '0.6', filter: 'drop-shadow(0 0 8px rgba(0, 240, 255, 0.4))' },
          '50%': { opacity: '1', filter: 'drop-shadow(0 0 20px rgba(0, 240, 255, 0.9))' },
        },
        radarSweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' }
        }
      }
    },
  },
  plugins: [],
}

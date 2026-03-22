/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#06B6D4', dark: '#0891B2', darker: '#0E7490' },
        surface: { DEFAULT: '#0F172A', light: '#1E293B', lighter: '#334155' },
        txt: { DEFAULT: '#F1F5F9', muted: '#94A3B8', dim: '#64748B' },
        success: '#22C55E',
        danger: '#EF4444',
        warn: '#F59E0B',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

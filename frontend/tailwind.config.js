/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#3B82F6",
        primaryDark: "#2563EB",
        secondary: "#10B981",
        darkBg: "#0B1120",
        cardBg: "#151E32",
        cardHover: "#1A2540",
        lightText: "#F8FAFC",
        mutedText: "#94A3B8",
        border: "#2A3650",
        borderLight: "#3D4F6F",
        warning: "#F59E0B",
        error: "#EF4444",
        accent: "#8B5CF6",
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 0 48px rgba(59, 130, 246, 0.12)',
        glowGreen: '0 0 48px rgba(16, 185, 129, 0.1)',
        card: '0 8px 32px rgba(0, 0, 0, 0.35)',
        inner: 'inset 0 1px 0 rgba(255, 255, 255, 0.05)',
      },
      animation: {
        'fade-in': 'fadeIn 0.45s ease-out forwards',
        'slide-up': 'slideUp 0.45s ease-out forwards',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(16px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
}

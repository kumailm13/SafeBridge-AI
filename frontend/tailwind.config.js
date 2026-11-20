/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        shield: {
          dark: '#0A0E17',    // Deep obsidian background
          card: '#121824',    // Elevated surface
          border: '#1E293B',  // Crisp structural border
          accent: '#10B981',  // Electric emerald (Security / Active)
          warning: '#F59E0B', // Amber warning for PII redaction
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      }
    }
  },
  plugins: [],
}

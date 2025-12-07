/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    fontFamily: {
      sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
    },
    extend: {
      colors: {
        surface: '#F8FAFC',   // 全局背景：极浅灰
        panel: '#FFFFFF',     // 卡片背景：纯白
        primary: '#4F46E5',   // 主色：靛蓝 Indigo-600
        secondary: '#64748B', // 次要文字：Slate-500
        dark: '#0F172A',      // 深色强调：Slate-900
      },
      boxShadow: {
        'soft': '0 2px 10px rgba(0, 0, 0, 0.03)',
        'float': '0 10px 30px rgba(79, 70, 229, 0.1)',
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '24px',
      }
    },
  },
  plugins: [],
}

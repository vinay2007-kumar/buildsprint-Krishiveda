/** @type {import('tailwindcss').Config} */
// Design tokens — built from designer-skills (design-token / color-system / typography-scale / spacing-system / motion-system)
import plugin from 'tailwindcss/plugin'

export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Brand: agricultural green — full tonal scale (color-system skill)
        farm: {
          50: '#f0f9f0',
          100: '#dcf0dc',
          200: '#bce0bc',
          300: '#8acb8a',
          400: '#5ab15a',
          500: '#2E8B57',
          600: '#28784c',
          700: '#226541',
          800: '#1d5236',
          900: '#18402b',
          950: '#0c2016',
        },
        // Semantic colors (success / warning / danger / info) with AA-compliant pairs
        success: {
          50: '#f0fdf4', 100: '#dcfce7', 200: '#bbf7d0', 300: '#86efac',
          400: '#4ade80', 500: '#22c55e', 600: '#16a34a', 700: '#15803d', 800: '#166534', 900: '#14532d',
        },
        warn: {
          50: '#fffbeb', 100: '#fef3c7', 200: '#fde68a', 300: '#fcd34d',
          400: '#fbbf24', 500: '#f59e0b', 600: '#d97706', 700: '#b45309', 800: '#92400e', 900: '#78350f',
        },
        danger: {
          50: '#fef2f2', 100: '#fee2e2', 200: '#fecaca', 300: '#fca5a5',
          400: '#f87171', 500: '#ef4444', 600: '#dc2626', 700: '#b91c1c', 800: '#991b1b', 900: '#7f1d1d',
        },
        info: {
          50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe', 300: '#93c5fd',
          400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af', 900: '#1e3a8a',
        },
        // Neutral scale for text, backgrounds, borders
        stone: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917',
          950: '#0c0a09',
        },
      },
      fontFamily: {
        // UI stack with Devanagari + Gujarati + Bengali + Tamil + Telugu + Kannada + Malayalam + Punjabi + Odia + Assamese support
        sans: [
          'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Noto Sans',
          'Noto Sans Devanagari', 'Noto Sans Gujarati', 'Noto Sans Bengali',
          'Noto Sans Tamil', 'Noto Sans Telugu', 'Noto Sans Kannada',
          'Noto Sans Malayalam', 'Noto Sans Gurmukhi', 'Noto Sans Oriya',
          'sans-serif',
        ],
        display: ['Georgia', 'Noto Sans Devanagari', 'Noto Sans Gujarati', 'serif'],
      },
      fontSize: {
        'display': ['48px', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '700' }],
        'h1': ['36px', { lineHeight: '1.2', letterSpacing: '-0.01em', fontWeight: '700' }],
        'h2': ['28px', { lineHeight: '1.25', letterSpacing: '-0.01em', fontWeight: '600' }],
        'h3': ['24px', { lineHeight: '1.3', fontWeight: '600' }],
        'subheading': ['20px', { lineHeight: '1.4', fontWeight: '500' }],
        'body': ['16px', { lineHeight: '1.5', fontWeight: '400' }],
        'body-sm': ['14px', { lineHeight: '1.4', fontWeight: '400' }],
        'caption': ['12px', { lineHeight: '1.4', letterSpacing: '0.05em', fontWeight: '500' }],
      },
      spacing: {
        '2xs': '2px',
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
        '3xl': '64px',
      },
      borderRadius: {
        '2xl': '1.125rem',   // 18px
        '3xl': '1.5rem',     // 24px
        '4xl': '2rem',       // 32px
      },
      boxShadow: {
        soft: '0 1px 2px rgba(12, 32, 22, 0.05), 0 4px 12px rgba(12, 32, 22, 0.08)',
        lift: '0 2px 4px rgba(12, 32, 22, 0.06), 0 12px 28px rgba(12, 32, 22, 0.12)',
        card: '0 1px 3px rgba(12, 32, 22, 0.06), 0 4px 16px rgba(12, 32, 22, 0.08)',
        elevated: '0 4px 6px rgba(12, 32, 22, 0.07), 0 18px 48px rgba(12, 32, 22, 0.1)',
      },
      letterSpacing: {
        caption: '0.05em',
        tight: '-0.02em',
        tighter: '-0.01em',
      },
      maxWidth: {
        app: '28rem',
        'app-lg': '32rem',
        'content': '72rem',
      },
      // Motion tokens (motion-system / animation-principles / micro-interaction-spec)
      transitionDuration: {
        instant: '50ms',
        fast: '120ms',
        base: '200ms',
        moderate: '300ms',
        slow: '400ms',
        deliberate: '600ms',
      },
      transitionTimingFunction: {
        standard: 'cubic-bezier(0.2, 0, 0, 1)',
        decelerate: 'cubic-bezier(0, 0, 0.2, 1)',
        accelerate: 'cubic-bezier(0.3, 0, 1, 0.3)',
        spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        linear: 'linear',
      },
      keyframes: {
        shimmer: { '0%': { backgroundPosition: '-400px 0' }, '100%': { backgroundPosition: '400px 0' } },
        fadeUp: { from: { opacity: '0', transform: 'translateY(6px)' }, to: { opacity: '1', transform: 'none' } },
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        pop: { '0%': { transform: 'scale(0.95)', opacity: '0' }, '100%': { transform: 'scale(1)', opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(8px)' }, to: { opacity: '1', transform: 'none' } },
        slideDown: { from: { opacity: '0', transform: 'translateY(-8px)' }, to: { opacity: '1', transform: 'none' } },
        pulseSoft: { '0%, 100%': { opacity: '1' }, '50%': { opacity: '0.6' } },
        float: { '0%, 100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-4px)' } },
        barGrow: { from: { transform: 'scaleX(0)' }, to: { transform: 'scaleX(1)' } },
        messageSlide: { from: { opacity: '0', transform: 'translateY(10px) scale(0.98)' }, to: { opacity: '1', transform: 'translateY(0) scale(1)' } },
        cardEntrance: { from: { opacity: '0', transform: 'translateY(8px)' }, to: { opacity: '1', transform: 'none' } },
        pulseRing: { '0%': { transform: 'scale(0.8)', opacity: '1' }, '100%': { transform: 'scale(2)', opacity: '0' } },
        shake: { '0%, 100%': { transform: 'translateX(0)' }, '25%': { transform: 'translateX(-2px)' }, '75%': { transform: 'translateX(2px)' } },
      },
      animation: {
        shimmer: 'shimmer 1.4s linear infinite',
        fadeUp: 'fadeUp 0.25s cubic-bezier(0,0,0.2,1) both',
        fadeIn: 'fadeIn 0.2s cubic-bezier(0.2,0,0,1) both',
        pop: 'pop 0.18s cubic-bezier(0.34,1.56,0.64,1) both',
        slideUp: 'slideUp 0.3s cubic-bezier(0,0,0.2,1) both',
        slideDown: 'slideDown 0.3s cubic-bezier(0,0,0.2,1) both',
        pulseSoft: 'pulseSoft 2s ease-in-out infinite',
        float: 'float 3s ease-in-out infinite',
        barGrow: 'barGrow 0.6s cubic-bezier(0.2,0,0,1) both',
        messageSlide: 'messageSlide 0.25s cubic-bezier(0,0,0.2,1) both',
        cardEntrance: 'cardEntrance 0.3s cubic-bezier(0,0,0.2,1) both',
        pulseRing: 'pulseRing 1.5s cubic-bezier(0,0,0.2,1) infinite',
        shake: 'shake 0.3s ease-in-out',
      },
    },
  },
  plugins: [
    // `landscape:` variant — device rotated to landscape (mobile/tablet)
    plugin(({ addVariant }) => addVariant('landscape', '@media (orientation: landscape)')),
    // `reduced:` variant — respects prefers-reduced-motion
    plugin(({ addVariant }) => addVariant('reduced', '@media (prefers-reduced-motion: reduce)')),
    // Custom utility for scrollbar hiding
    plugin(({ addUtilities }) => {
      addUtilities({
        '.no-scrollbar': {
          '-ms-overflow-style': 'none',
          'scrollbar-width': 'none',
          '&::-webkit-scrollbar': { display: 'none' },
        },
        '.scrollbar-thin': {
          'scrollbar-width': 'thin',
          'scrollbar-color': 'theme(colors.farm.300) transparent',
          '&::-webkit-scrollbar': { width: '6px', height: '6px' },
          '&::-webkit-scrollbar-track': { background: 'transparent' },
          '&::-webkit-scrollbar-thumb': { backgroundColor: 'theme(colors.farm.300)', borderRadius: '3px' },
          '&::-webkit-scrollbar-thumb:hover': { backgroundColor: 'theme(colors.farm.400)' },
        },
      })
    }),
  ],
}
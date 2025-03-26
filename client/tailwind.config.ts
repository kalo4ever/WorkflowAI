import type { Config } from 'tailwindcss';
import plugin from 'tailwindcss/plugin';

const config = {
  darkMode: ['class'],
  content: ['./src/**/*.{ts,tsx}'],
  prefix: '',
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        outline: 'hsl(var(--outline))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontFamily: {
        sans: ['var(--font-geist-sans)'],
        mono: ['var(--font-geist-mono)'],
        runde: ['var(--font-open-runde)'],
        inter: ['var(--font-inter)'],
        lato: ['var(--font-lato)'],
      },
      fontSize: {
        xsm: ['0.8125rem', '1.125rem'],
      },
      maxHeight: {
        inherit: 'inherit',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        'collapsible-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-collapsible-content-height)' },
        },
        'collapsible-up': {
          from: { height: 'var(--radix-collapsible-content-height)' },
          to: { height: '0' },
        },
        jump: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pulse-scale': {
          '0%, 100%': {
            opacity: '1',
            transform: 'scale(1)',
          },
          '50%': {
            opacity: '.5',
            transform: 'scale(1.3)',
          },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'collapsible-down': 'collapsible-down 0.2s ease-out',
        'collapsible-up': 'collapsible-up 0.2s ease-out',
        jump1: 'jump 0.8s infinite ease-in-out',
        jump2: 'jump 0.8s infinite ease-in-out 0.2s',
        jump3: 'jump 0.8s infinite ease-in-out 0.4s',
        'pulse-scale': 'pulse-scale 2s ease-in-out infinite',
      },
      boxShadow: {
        floating: '0px 4px 24px 0px rgba(0, 0, 0, 0.08)',
        modal: '0 4px 24px rgba(0, 0, 0, 0.12)',
      },
      screens: {
        lg: '900px',
      },
      backgroundImage: {
        'custom-gradient-1': `linear-gradient(135deg, 
          #ffffff 0%,
          rgb(243 232 255 / 0.4) 20%,
          rgb(253 242 255 / 0.35) 40%,
          rgb(255 242 247 / 0.35) 60%,
          rgb(255 235 245 / 0.4) 80%,
          rgb(255 240 252 / 0.45) 100%
        ), linear-gradient(to bottom, white, white)`,
        'custom-gradient-2': `linear-gradient(135deg, 
          #ffffff 0%,
          rgb(243 232 255 / 0.2) 20%,
          rgb(253 242 255 / 0.15) 40%,
          rgb(255 242 247 / 0.15) 60%,
          rgb(255 235 245 / 0.2) 80%,
          rgb(255 240 252 / 0.25) 100%
        ), linear-gradient(to bottom, white, white)`,
        'custom-gradient-3': `linear-gradient(135deg, 
          #ffffff 0%,
          rgb(243 232 255 / 0.15) 20%,
          rgb(253 242 255 / 0.1) 40%,
          rgb(255 242 247 / 0.1) 60%,
          rgb(255 235 245 / 0.15) 80%,
          rgb(255 240 252 / 0.2) 100%
        ), linear-gradient(to bottom, white, white)`,
        'custom-indigo-gradient': 'linear-gradient(to right, #8759E3, #4235F8)',
        'custom-indigo-gradient-hover': 'linear-gradient(to right, #784CD0, #3B30DF)',
        'custom-gradient-solid': `linear-gradient(90deg,
          #A960EE,
          #C789CB,
          #C788CB,
          #B778E1,
          #C789CB,
          #C788CB,
          #A960EE
        )`,
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
    require('@tailwindcss/typography'),
    plugin(({ addUtilities }) => {
      addUtilities({
        '.bg-gradient-image': {
          'background-image': 'url("/images/Gradient.png")',
          'background-size': 'cover',
          'background-position': 'center',
          'background-repeat': 'no-repeat',
        },
      });
    }),
  ],
} satisfies Config;

export default config;

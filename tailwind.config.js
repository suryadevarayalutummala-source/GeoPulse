/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#F4F7F4',
          100: '#E4ECE4',
          200: '#C8DAC8',
          300: '#9EBF9E',
          400: '#719F71',
          500: '#4F804F',
          600: '#3D6838',
          700: '#2F4F2B',
          800: '#233C21',
          900: '#182A1B',
          950: '#0F1C11',
        },
        sage: {
          100: '#F0F4EF',
          200: '#D9E6D5',
          300: '#BCCDBC',
          400: '#9EBE98',
          500: '#76A370',
          600: '#54854E',
          700: '#3F673A',
        },
        beige: {
          50: '#FAF8F3',
          100: '#F9F5EC',
          150: '#F4EFE5',
          200: '#EFEAE0',
          300: '#E4DDD0',
          400: '#D4C9B6',
          500: '#C1B39D',
          600: '#A99A82',
          700: '#8A7A64',
          800: '#695B49',
          900: '#473C2F',
        },
        olive: {
          100: '#F5F6EB',
          200: '#E6E9CD',
          300: '#D3D8A6',
          400: '#BCC37A',
          500: '#A3AC52',
          600: '#8E9B4B',
          700: '#6C7736',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Outfit', 'Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

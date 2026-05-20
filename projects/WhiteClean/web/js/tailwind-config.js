tailwind.config = {
  theme: {
    extend: {
      colors: {
        clean: {
          primary: '#00BAF2',
          primaryHover: '#0099C7',
          darkBlue: '#0F3D64',
          darkBlueHover: '#0A2B47',
          text: '#1E293B',
          muted: '#64748B',
          border: '#E2E8F0',
          surface: '#F8FAFC',
          bg: '#FFFFFF',
        }
      },
      fontFamily: {
        sans: ['Raleway', 'sans-serif'],
        primary: ['Montserrat', 'sans-serif'],
        exo: ['Exo', 'sans-serif'],
        quicksand: ['Quicksand', 'sans-serif']
      },
      animation: {
        'infinite-scroll': 'infinite-scroll 25s linear infinite',
      },
      keyframes: {
        'infinite-scroll': {
          from: { transform: 'translateX(0)' },
          to: { transform: 'translateX(-50%)' },
        }
      }
    }
  }
}

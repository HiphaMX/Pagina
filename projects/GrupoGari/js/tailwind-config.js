module.exports = {
    darkMode: 'class', // Disable auto dark mode
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#fff9eb',
                    100: '#ffefc6',
                    200: '#ffe088',
                    300: '#ffca4a',
                    400: '#ffb21b',
                    500: '#f7a808', // Grupo Gari Yellow (Acento)
                    600: '#e28800',
                    700: '#bb6002',
                    800: '#944908',
                    900: '#7a3d0b',
                    950: '#461f02',
                },
                base: {
                    bg: '#F8F9FA', // Ice White/Off-white
                    surface: '#FFFFFF', // Pure white for cards
                    text: '#1A1A1A', // Deep Charcoal for solid headers
                    muted: '#666666', // Medium Gray for paragraph text
                    border: '#EAEAEA',
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            letterSpacing: {
                tighter: '-.04em',
                tightest: '-.06em',
            },
            borderRadius: {
                '4xl': '2.5rem',
                '5xl': '3.5rem',
            },
            boxShadow: {
                'soft': '0 20px 40px -15px rgba(0,0,0,0.05)',
                'float': '0 30px 60px -20px rgba(0,0,0,0.08)',
            }
        }
    }
}

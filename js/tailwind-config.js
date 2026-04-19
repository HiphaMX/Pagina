tailwind.config = {
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            colors: {
                primary: {
                    50: '#ecfeff',
                    100: '#cffafe',
                    400: '#22d3ee',
                    500: '#06b6d4', // Bioluminescent Cyan 500
                    600: '#0891b2',
                    900: '#164e63',
                },
                darkbase: '#050810',
                glass: 'rgba(255, 255, 255, 0.03)',
                glassBorder: 'rgba(6, 182, 212, 0.15)',
            }
        }
    }
}

// Configuración de los colores corporativos para Tailwind CDN
tailwind.config = {
    theme: {
        extend: {
            colors: {
                brandRed: '#d91b1b', // Rojo Torque Bikers
                darkBg: '#2a2a2a',   // Fondo principal
                cardBg: '#000000',   // Fondo de la tarjeta
                inputBg: '#333333'   // Fondo de los inputs
            }
        }
    }
}

// Lógica para mostrar/ocultar contraseña
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    }
}
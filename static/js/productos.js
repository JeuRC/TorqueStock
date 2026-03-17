// Configuración de Tailwind CDN
tailwind.config = {
    theme: {
        extend: {
            colors: {
                brandRed: '#d91b1b', 
                darkBg: '#0f0f0f',   
                sidebarBg: '#1a1a1a',
                cardBg: '#222222',   
                tableRowHover: '#2a2a2a'
            }
        }
    }
}

// Funciones para abrir y cerrar modales (agregadas al objeto global window para ser llamadas desde HTML)
window.openModal = function(modalId) {
    document.getElementById(modalId).classList.add('active');
    document.body.style.overflow = 'hidden';
}

window.closeModal = function(modalId) {
    document.getElementById(modalId).classList.remove('active');
    document.body.style.overflow = 'auto';
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

// Inicialización de lógica del DOM al cargar la página
document.addEventListener("DOMContentLoaded", function() {
    
    // Prevenir envío del formulario
    const formRegistrar = document.getElementById('formRegistrarProducto');
    if (formRegistrar) {
        formRegistrar.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Producto registrado correctamente');
            window.closeModal('registrarProductoModal');
        });
    }

    // Gráfico de ventas usando la variable inyectada desde Flask
    const canvasElement = document.getElementById('sideSalesChart');
    if (canvasElement) {
        const ctx = canvasElement.getContext('2d');
        // Recuperamos la variable desde el entorno global (inyectada en el HTML)
        const dataValues = window.ventasData || []; 
        
        let gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(217, 27, 27, 0.4)');
        gradient.addColorStop(1, 'rgba(217, 27, 27, 0.0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['May 23', '', '', '', 'May 23', '', '', '', 'Jul 23', '', ''],
                datasets: [{
                    label: 'Ventas',
                    data: dataValues,
                    borderColor: '#d91b1b',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 600,
                        grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                        ticks: { color: '#666', font: {size: 10} }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#666', font: {size: 10} }
                    }
                }
            }
        });
    }
});
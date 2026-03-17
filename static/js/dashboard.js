// Configuración de los colores corporativos para Tailwind CDN
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

// Inicialización de gráficos y lógica del DOM
document.addEventListener("DOMContentLoaded", function() {
    const canvasElement = document.getElementById('salesChart');
    
    // Verificamos que el canvas exista para evitar errores
    if (canvasElement) {
        const ctx = canvasElement.getContext('2d');
        
        // Crear gradiente para rellenar debajo de la línea
        let gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(217, 27, 27, 0.5)'); // Rojo transparente arriba
        gradient.addColorStop(1, 'rgba(217, 27, 27, 0)');   // Transparente abajo

        const salesChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['May 23', '', 'Jun 23', '', 'Jul 23', '', 'Ago 23'], // Simplificado para encajar
                datasets: [{
                    label: 'Ventas',
                    data: [50, 250, 190, 300, 240, 500, 240, 350, 500],
                    borderColor: '#d91b1b', // brandRed
                    backgroundColor: gradient,
                    borderWidth: 2,
                    pointBackgroundColor: '#d91b1b',
                    pointBorderColor: '#fff',
                    pointRadius: 0, // Ocultar puntos como en tu diseño
                    pointHoverRadius: 4,
                    fill: true,
                    tension: 0.4 // Hace la línea curva
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false } // Ocultamos la leyenda
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 600,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false,
                        },
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
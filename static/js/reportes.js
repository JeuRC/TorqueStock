// Configuración de los colores corporativos para Tailwind CDN
tailwind.config = {
    theme: {
        extend: {
            colors: {
                brandRed: '#d91b1b', 
                darkBg: '#0f0f0f',   
                sidebarBg: '#1a1a1a',
                cardBg: '#222222',
                cardHover: '#2a2a2a'
            }
        }
    }
}

// Inicialización de gráficos y lógica del DOM
document.addEventListener("DOMContentLoaded", function() {
    const canvasElement = document.getElementById('detailedSalesChart');
    
    // Verificamos que el canvas exista
    if (canvasElement) {
        // Obtenemos los datos inyectados por Flask desde el objeto window
        const labels = window.reportesLabels || [];
        const dataValues = window.reportesData || [];
        
        const ctx = canvasElement.getContext('2d');
        
        // Gradiente para el relleno debajo de la línea
        let gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(217, 27, 27, 0.4)'); // brandRed con opacidad
        gradient.addColorStop(1, 'rgba(217, 27, 27, 0.0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ventas ($)',
                    data: dataValues,
                    borderColor: '#d91b1b', // Color de la línea
                    backgroundColor: gradient, // Relleno
                    borderWidth: 2,
                    pointBackgroundColor: '#0f0f0f', // Puntos oscuros con borde rojo
                    pointBorderColor: '#d91b1b',
                    pointBorderWidth: 2,
                    pointRadius: 3, // Puntos visibles como en el mockup
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#d91b1b',
                    fill: true,
                    tension: 0.3 // Suavidad de la curva
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#222',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#444',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return 'Data valor: ' + context.parsed.y;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 450, // Ajustado según el mockup
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false,
                        },
                        ticks: { 
                            color: '#666', 
                            font: {size: 10},
                            stepSize: 50
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { 
                            color: '#666', 
                            font: {size: 9},
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                }
            }
        });
    }
});
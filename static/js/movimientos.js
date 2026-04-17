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

// Funciones para abrir y cerrar modales (asignadas a window para usarlas en HTML)
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

window.seleccionarProductoIngreso = function(nombre, sku, stock, precio) {
    // 1. Asignar el valor al input
    const inputBusqueda = document.getElementById('busquedaProductoIngreso');
    inputBusqueda.value = nombre;
    
    // 2. Mostrar la tarjeta de información
    const infoDiv = document.getElementById('infoProductoIngreso');
    const detalleDiv = document.getElementById('detalleProductoIngreso');
    
    detalleDiv.innerHTML = `
        <p class="text-white font-medium">${nombre}</p>
        <p class="text-xs text-gray-400 mt-1">SKU: <span class="text-white">${sku}</span> | Stock: <span class="text-white">${stock}</span> | Precio: <span class="text-white">${precio}</span></p>
    `;
    
    infoDiv.classList.remove('hidden');
    
    // 3. Ocultar la lista INMEDIATAMENTE
    document.getElementById('listaProductosIngreso').classList.add('hidden');
}

window.seleccionarProductoSalida = function(nombre, sku, stock, precio) {
    const inputBusqueda = document.getElementById('busquedaProductoSalida');
    inputBusqueda.value = nombre;
    
    const infoDiv = document.getElementById('infoProductoSalida');
    const detalleDiv = document.getElementById('detalleProductoSalida');
    
    detalleDiv.innerHTML = `
        <p class="text-white font-medium">${nombre}</p>
        <p class="text-xs text-gray-400 mt-1">SKU: <span class="text-white">${sku}</span> | Disponible: <span class="text-white">${stock}</span> | Precio: <span class="text-white">${precio}</span></p>
    `;
    
    infoDiv.classList.remove('hidden');
    document.getElementById('listaProductosSalida').classList.add('hidden');
}

// Manejo de búsquedas y envío de formularios al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Búsqueda en ingreso
    const busquedaIngreso = document.getElementById('busquedaProductoIngreso');
    const listaIngreso = document.getElementById('listaProductosIngreso');
    
    if (busquedaIngreso) {
        busquedaIngreso.addEventListener('focus', function() {
            listaIngreso.classList.remove('hidden');
        });
        
        busquedaIngreso.addEventListener('blur', function() {
            setTimeout(() => {
                listaIngreso.classList.add('hidden');
            }, 200);
        });
    }
    
    // Búsqueda en salida
    const busquedaSalida = document.getElementById('busquedaProductoSalida');
    const listaSalida = document.getElementById('listaProductosSalida');
    
    if (busquedaSalida) {
        busquedaSalida.addEventListener('focus', function() {
            listaSalida.classList.remove('hidden');
        });
        
        busquedaSalida.addEventListener('blur', function() {
            setTimeout(() => {
                listaSalida.classList.add('hidden');
            }, 200);
        });
    }
    
    const formRegistrar = document.getElementById('formRegistrarProducto');
    if (formRegistrar) {
        formRegistrar.addEventListener('submit', function(e) {
            const btn = this.querySelector('button[type="submit"]');
            if(btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Guardando...';
        });
    }
    
    const formIngreso = document.getElementById('formIngreso');
    if (formIngreso) {
        formIngreso.addEventListener('submit', function(e) {
            const btn = this.querySelector('button[type="submit"]');
            if(btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Registrando Ingreso...';
        });
    }
    
    const formSalida = document.getElementById('formSalida');
    if (formSalida) {
        formSalida.addEventListener('submit', function(e) {
            const btn = this.querySelector('button[type="submit"]');
            if(btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Registrando Venta...';
        });
    }
});
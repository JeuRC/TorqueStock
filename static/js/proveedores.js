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

// Funciones para abrir y cerrar modales
window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
        
        // Limpiar el formulario al cerrar
        const form = document.getElementById('formProveedor');
        if (form) {
            form.reset();
        }
    }
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    if (event.target.classList && event.target.classList.contains('modal-overlay')) {
        event.target.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

// Cerrar modal con tecla ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal-overlay');
        modals.forEach(modal => {
            if (modal.classList && modal.classList.contains('active')) {
                modal.classList.remove('active');
                document.body.style.overflow = 'auto';
            }
        });
    }
});

// Validación del formulario de proveedores
document.addEventListener("DOMContentLoaded", function() {
    const formProveedor = document.getElementById('formProveedor');
    if (formProveedor) {
        formProveedor.addEventListener('submit', function(e) {
            const nombre = document.getElementById('nombreProveedor').value.trim();
            const contacto = document.getElementById('contactoProveedor').value.trim();
            const correo = document.getElementById('correoProveedor').value.trim();
            const telefono = document.getElementById('telefonoProveedor').value.trim();
            const suministro = document.getElementById('suministroProveedor').value;
            const estado = document.querySelector('input[name="estado"]:checked');
            
            if (!nombre) {
                e.preventDefault();
                alert('Por favor, ingrese el nombre del proveedor');
                return false;
            }
            
            if (!contacto) {
                e.preventDefault();
                alert('Por favor, ingrese el nombre del contacto');
                return false;
            }
            
            if (!correo) {
                e.preventDefault();
                alert('Por favor, ingrese el correo electrónico');
                return false;
            }
            
            // Validar formato de email
            const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
            if (!emailRegex.test(correo)) {
                e.preventDefault();
                alert('Por favor, ingrese un correo electrónico válido');
                return false;
            }
            
            if (!telefono) {
                e.preventDefault();
                alert('Por favor, ingrese el teléfono');
                return false;
            }
            
            if (!suministro) {
                e.preventDefault();
                alert('Por favor, seleccione el suministro principal');
                return false;
            }
            
            if (!estado) {
                e.preventDefault();
                alert('Por favor, seleccione el estado del proveedor');
                return false;
            }
            
            // Mostrar mensaje de guardando
            const submitBtn = formProveedor.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Guardando...';
                submitBtn.disabled = true;
            }
        });
    }
});

// Función para filtrar proveedores por estado
function filtrarPorEstado(estado) {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const estadoCelda = row.querySelector('td:nth-child(6) span');
        if (estadoCelda) {
            const estadoTexto = estadoCelda.textContent;
            if (estado === 'todos' || estadoTexto === estado) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

// Función para filtrar proveedores por suministro
function filtrarPorSuministro() {
    const select = document.getElementById('filtroSuministro');
    const suministroSeleccionado = select.value;
    const rows = document.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const suministroCelda = row.querySelector('td:nth-child(5)');
        if (suministroCelda) {
            const suministroTexto = suministroCelda.textContent;
            if (suministroSeleccionado === 'todos' || suministroTexto === suministroSeleccionado) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

// Función para búsqueda en tiempo real
function buscarProveedores() {
    const searchInput = document.getElementById('buscarProveedor');
    if (searchInput) {
        const searchTerm = searchInput.value.toLowerCase();
        const tableRows = document.querySelectorAll('tbody tr');
        
        tableRows.forEach(row => {
            const nombre = row.querySelector('td:first-child')?.textContent.toLowerCase() || '';
            const contacto = row.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
            const correo = row.querySelector('td:nth-child(3)')?.textContent.toLowerCase() || '';
            
            if (nombre.includes(searchTerm) || contacto.includes(searchTerm) || correo.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
}

// Inicializar eventos
document.addEventListener("DOMContentLoaded", function() {
    // Evento para búsqueda
    const searchInput = document.getElementById('buscarProveedor');
    if (searchInput) {
        searchInput.addEventListener('keyup', buscarProveedores);
    }
    
    // Evento para búsqueda con botón
    const searchBtn = document.getElementById('buscarBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', buscarProveedores);
    }
    
    // Eventos para filtros de estado
    const btnActivo = document.getElementById('filtroActivo');
    const btnInactivo = document.getElementById('filtroInactivo');
    const btnTodos = document.getElementById('filtroTodos');
    
    if (btnActivo) {
        btnActivo.addEventListener('click', function() {
            filtrarPorEstado('Activo');
            actualizarBotonEstado('activo');
        });
    }
    
    if (btnInactivo) {
        btnInactivo.addEventListener('click', function() {
            filtrarPorEstado('Inactivo');
            actualizarBotonEstado('inactivo');
        });
    }
    
    if (btnTodos) {
        btnTodos.addEventListener('click', function() {
            filtrarPorEstado('todos');
            actualizarBotonEstado('todos');
        });
    }
    
    // Evento para filtro de suministro
    const filtroSuministro = document.getElementById('filtroSuministro');
    if (filtroSuministro) {
        filtroSuministro.addEventListener('change', filtrarPorSuministro);
    }
});

// Función para actualizar estilo de botones de estado
function actualizarBotonEstado(activo) {
    const btnActivo = document.getElementById('filtroActivo');
    const btnInactivo = document.getElementById('filtroInactivo');
    const btnTodos = document.getElementById('filtroTodos');
    
    // Resetear estilos
    [btnActivo, btnInactivo, btnTodos].forEach(btn => {
        if (btn) {
            btn.classList.remove('bg-gray-700', 'text-white');
            btn.classList.add('text-gray-400');
        }
    });
    
    // Aplicar estilo al botón activo
    if (activo === 'activo' && btnActivo) {
        btnActivo.classList.add('bg-gray-700', 'text-white');
        btnActivo.classList.remove('text-gray-400');
    } else if (activo === 'inactivo' && btnInactivo) {
        btnInactivo.classList.add('bg-gray-700', 'text-white');
        btnInactivo.classList.remove('text-gray-400');
    } else if (activo === 'todos' && btnTodos) {
        btnTodos.classList.add('bg-gray-700', 'text-white');
        btnTodos.classList.remove('text-gray-400');
    }
}
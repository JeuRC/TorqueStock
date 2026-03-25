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
        
        // Si es el modal de categorías, calcular el siguiente ID
        if (modalId === 'registrarCategoriaModal') {
            calcularSiguienteId();
        }
    }
}

window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
        
        // Limpiar el formulario al cerrar
        const form = document.getElementById('formCategoria');
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

// Función para calcular el siguiente ID de categoría
function calcularSiguienteId() {
    const rows = document.querySelectorAll('tbody tr');
    let maxId = 0;
    
    rows.forEach(row => {
        const idCell = row.querySelector('td:first-child');
        if (idCell) {
            let id = parseInt(idCell.textContent);
            if (isNaN(id)) {
                // Si el ID tiene formato como "C001", extraer el número
                const idText = idCell.textContent;
                const numero = parseInt(idText.replace(/[^0-9]/g, ''));
                if (!isNaN(numero)) {
                    id = numero;
                }
            }
            if (!isNaN(id) && id > maxId) {
                maxId = id;
            }
        }
    });
    
    const siguienteId = maxId + 1;
    const idSpan = document.getElementById('categoriaId');
    const idHidden = document.getElementById('categoriaIdHidden');
    
    if (idSpan) {
        idSpan.textContent = siguienteId;
    }
    if (idHidden) {
        idHidden.value = siguienteId;
    }
}

// Validación del formulario de categorías
document.addEventListener("DOMContentLoaded", function() {
    const formCategoria = document.getElementById('formCategoria');
    if (formCategoria) {
        formCategoria.addEventListener('submit', function(e) {
            const nombre = document.getElementById('nombreCategoria').value.trim();
            
            if (!nombre) {
                e.preventDefault();
                alert('Por favor, ingrese el nombre de la categoría');
                return false;
            }
            
            if (nombre.length < 2) {
                e.preventDefault();
                alert('El nombre de la categoría debe tener al menos 2 caracteres');
                return false;
            }
            
            // Mostrar mensaje de guardando
            const submitBtn = formCategoria.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Guardando...';
                submitBtn.disabled = true;
            }
        });
    }
});

// Función para búsqueda en tiempo real
function buscarCategorias() {
    const searchInput = document.querySelector('.buscar-categoria');
    if (searchInput) {
        const searchTerm = searchInput.value.toLowerCase();
        const tableRows = document.querySelectorAll('tbody tr');
        
        tableRows.forEach(row => {
            const nombreCategoria = row.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
            const idCategoria = row.querySelector('td:first-child')?.textContent.toLowerCase() || '';
            
            if (nombreCategoria.includes(searchTerm) || idCategoria.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
}

// Función para ordenar categorías
function ordenarCategorias() {
    const select = document.querySelector('select');
    if (select) {
        const order = select.value;
        const tbody = document.querySelector('tbody');
        if (tbody) {
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort((a, b) => {
                const nombreA = a.querySelector('td:nth-child(2)')?.textContent || '';
                const nombreB = b.querySelector('td:nth-child(2)')?.textContent || '';
                
                if (order === 'Nombre (A-Z)') {
                    return nombreA.localeCompare(nombreB);
                } else if (order === 'Nombre (Z-A)') {
                    return nombreB.localeCompare(nombreA);
                }
                return 0;
            });
            
            // Reordenar las filas
            rows.forEach(row => tbody.appendChild(row));
        }
    }
}

// Inicializar eventos
document.addEventListener("DOMContentLoaded", function() {
    // Evento para búsqueda
    const searchInput = document.querySelector('.buscar-categoria');
    if (searchInput) {
        searchInput.addEventListener('keyup', buscarCategorias);
    }
    
    // Evento para ordenar
    const orderSelect = document.querySelector('select');
    if (orderSelect) {
        orderSelect.addEventListener('change', ordenarCategorias);
    }
});
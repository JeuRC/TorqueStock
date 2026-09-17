let barcodeBuffer = "";
let barcodeTimeout;

document.addEventListener('keydown', function(e) {
    // 1. Ignorar si el usuario está escribiendo manualmente en un input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
        return;
    }

    // 2. La pistola láser envía 'Enter' al terminar de leer
    if (e.key === 'Enter' && barcodeBuffer.length > 4) {
        procesarLectura(barcodeBuffer);
        barcodeBuffer = "";
        return;
    }

    // 3. Acumular caracteres rápidamente
    if (e.key.length === 1) {
        barcodeBuffer += e.key;
        clearTimeout(barcodeTimeout);
        // Si pasan más de 50ms, asumimos que es una persona tecleando, no la pistola láser
        barcodeTimeout = setTimeout(() => { barcodeBuffer = ""; }, 50);
    }
});

function procesarLectura(codigo) {
    const toast = document.createElement('div');
    toast.className = "fixed top-4 left-1/2 transform -translate-x-1/2 bg-brandRed text-white px-6 py-2 rounded shadow-2xl z-[9999] flex items-center gap-2 font-bold animate-bounce";
    toast.innerHTML = `<i class="fa-solid fa-barcode"></i> Procesando: ${codigo}...`;
    document.body.appendChild(toast);

    fetch(`/api/escanear/${codigo}`)
        .then(res => res.json())
        .then(data => {
            toast.remove(); 
            if (data.existe) {
                // Producto EXISTE -> Mandar a Movimientos con la llave correcta
                sessionStorage.setItem('autoScanAccion', 'existente');
                sessionStorage.setItem('autoScanData', JSON.stringify(data));
                window.location.href = "/movimientos";
            } else {
                // Producto NUEVO -> Mandar a Productos con la llave correcta
                sessionStorage.setItem('autoScanAccion', 'nuevo');
                // Almacenamos el serial escaneado para pasarlo al input
                sessionStorage.setItem('autoScanCodigo', codigo); 
                window.location.href = "/productos";
            }
        })
        .catch(error => {
            toast.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Error de lectura`;
            setTimeout(() => toast.remove(), 2000);
        });
}
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Simulación de inicio de sesión exitoso, redirige al dashboard
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Datos simulados para las tarjetas (RF-06 Visualización de stock)
    resumen = {
        'total_productos': "5,420",
        'stock_bajo': "23",
        'valor_inventario': "$45,000.00"
    }
    
    # Datos simulados para la tabla de movimientos
    movimientos = [
        {'item': 'Casco MT Helmets - Vendido', 'descripcion': 'Vendido', 'fecha': '02/02/2026'},
        {'item': 'Aceite Motul - Entrada', 'descripcion': 'Entrada', 'fecha': '03/07/2026'},
        {'item': 'Llantas Pirelli - Salida', 'descripcion': 'Vendido', 'fecha': '03/07/2026'},
        {'item': 'Aceite Motul - Salida', 'descripcion': 'Entrada', 'fecha': '03/07/2026'},
        {'item': 'Llantas Pirelli - Salida', 'descripcion': 'Vendido', 'fecha': '03/02/2026'},
    ]
    
    return render_template('dashboard.html', resumen=resumen, movimientos=movimientos)

@app.route('/productos')
def productos():
    # Datos simulados para las tarjetas de resumen
    resumen_prod = {
        'total': '5,420',
        'stock_bajo': '23',
        'valor_total': '$125,000.00',
        'nuevas_adiciones': '12' # Número de ejemplo
    }
    
    # Datos simulados para el catálogo (RF-01 y RF-06)
    lista_productos = [
        {'sku': '100001', 'nombre': 'Casco MT Helmets Full Face', 'categoria': 'Categoría', 'marca': 'MT Helmets', 'stock': 23, 'precio': '$50.00', 'estado': 'Activo'},
        {'sku': '710002', 'nombre': 'Aceite Motul 7100 4T', 'categoria': 'Categoría', 'marca': 'Motul', 'stock': 23, 'precio': '$100.00', 'estado': 'Inactivo'},
        {'sku': '710003', 'nombre': 'Aceite Motul 7100 4T', 'categoria': 'Categoría', 'marca': 'Motul', 'stock': 150, 'precio': '$150.00', 'estado': 'Activo'},
        {'sku': '100004', 'nombre': 'Llantas Pirelli Angel GT', 'categoria': 'Categoría', 'marca': 'Pirelli', 'stock': 23, 'precio': '$50.00', 'estado': 'Activo'},
        {'sku': '100005', 'nombre': 'Llantas Pirelli Angel GT', 'categoria': 'Categoría', 'marca': 'Pirelli', 'stock': 150, 'precio': '$130.00', 'estado': 'Activo'},
        {'sku': '110007', 'nombre': 'Llantas Pirelli Angel GT', 'categoria': 'Categoría', 'marca': 'Pirelli', 'stock': 150, 'precio': '$150.00', 'estado': 'Inactivo'},
        {'sku': '100008', 'nombre': 'Llantas Pirelli Angel GT', 'categoria': 'Categoría', 'marca': 'Pirelli', 'stock': 23, 'precio': '$720.00', 'estado': 'Activo'},
    ]

    # Datos para la gráfica lateral
    datos_grafica = [50, 80, 250, 190, 300, 230, 480, 250, 350, 350, 500]

    return render_template('productos.html', resumen=resumen_prod, productos=lista_productos, ventas=datos_grafica)

@app.route('/categorias')
def categorias():
    # Datos simulados para las tarjetas de resumen de categorías
    resumen_cat = {
        'total_categorias': 12,
        'mas_rentable': 'Llantas',
        'detalle_rentable': '80% de Ingresos (Clase A)',
        'cat_stock_bajo': '8 Categories',
        'items_stock_bajo': '23 Items Total'
    }
    
    # Datos simulados para el Catálogo de Categorías
    lista_categorias = [
        {'id': 'C001', 'nombre': 'Cascos', 'descripcion': 'Cascos integrales, modulares y abiertos', 'cantidad': 150, 'valor': '$15,000', 'alerta': False},
        {'id': 'C002', 'nombre': 'Aceites', 'descripcion': 'Aceites para motor 2T y 4T', 'cantidad': 300, 'valor': '$6,000', 'alerta': False},
        {'id': 'C003', 'nombre': 'Llantas', 'descripcion': 'Llantas de calle, pista y doble propósito', 'cantidad': 120, 'valor': '$18,000', 'alerta': True, 'detalle_alerta': '23 Items Bajo Stock'},
        {'id': 'C004', 'nombre': 'Repuestos', 'descripcion': 'Pastillas, bujías y filtros', 'cantidad': 500, 'valor': '$4,500', 'alerta': False},
    ]
    
    return render_template('categorias.html', resumen=resumen_cat, categorias=lista_categorias)

@app.route('/proveedores')
def proveedores():
    # Datos simulados para las tarjetas de resumen
    resumen_prov = {
        'total': 28,
        'activos': 25,
        'ordenes_criticas': 3,
        'proximas_entregas': 7
    }
    
    # Datos simulados para la tabla de proveedores
    lista_proveedores = [
        {'nombre': 'Pirelli Tyres S.A.', 'contacto': 'John Doe', 'correo': 'j.doe@pirelli.com', 'telefono': '+34 600123456', 'suministro': 'Llantas', 'ultima_orden': '05/10/2023', 'estado': 'Activo'},
        {'nombre': 'MT Helmets Iberia', 'contacto': 'Jane Smith', 'correo': 'jane@mthelmets.com', 'telefono': '+34 600123456', 'suministro': 'Cascos', 'ultima_orden': '05/10/2023', 'estado': 'Activo'},
        {'nombre': 'Motul Oil Co.', 'contacto': 'Robert Brown', 'correo': 'robert@motul.com', 'telefono': '+34 600123456', 'suministro': 'Aceites', 'ultima_orden': '05/10/2023', 'estado': 'Activo'},
        {'nombre': 'Fox Racing Supply', 'contacto': 'Alice Davis', 'correo': 'alice@davis.com', 'telefono': '+34 600123456', 'suministro': 'Aceites', 'ultima_orden': '05/10/2023', 'estado': 'Crítico'},
        {'nombre': 'Bridgestone', 'contacto': 'Carlos Rodriguez', 'correo': 'carlos@bridguerz.com', 'telefono': '+34 600123456', 'suministro': 'Equipamiento', 'ultima_orden': '05/10/2023', 'estado': 'Activo'},
    ]
    
    return render_template('proveedores.html', resumen=resumen_prov, proveedores=lista_proveedores)

@app.route('/reportes')
def reportes():
    # Simulamos los días del mes (Nov 01 a Nov 30)
    dias_mes = [f"Nov {str(i).zfill(2)}" for i in range(1, 31)]
    
    # Simulamos los datos de ventas para la gráfica
    datos_ventas = [
        90, 40, 100, 150, 90, 120, 200, 150, 140, 220, 
        210, 230, 220, 390, 310, 250, 350, 320, 260, 200, 
        300, 190, 220, 240, 190, 210, 250, 180, 210, 230
    ]
    
    return render_template('reportes.html', dias=dias_mes, ventas=datos_ventas)

@app.route('/configuracion')
def configuracion():
    # Datos simulados para las tarjetas de resumen
    resumen_roles = {
        'total': 4,
        'administradores': 1,
        'operadores': 2,
        'visores': 1
    }
    
    # Datos simulados para la tabla de roles
    lista_roles = [
        {
            'rol': 'Administrador', 
            'descripcion': 'Acceso total al sistema.', 
            'icono_permiso': '<i class="fa-solid fa-lock text-brandRed mr-1"></i>',
            'permisos': 'candado total', 
            'icono_miembros': '<i class="fa-solid fa-user text-gray-400 mr-1"></i>',
            'miembros': 1, 
            'estado': 'Activo'
        },
        {
            'rol': 'Operador de Inventario', 
            'descripcion': 'Gestión de productos y categorías.', 
            'icono_permiso': '<i class="fa-solid fa-box text-brandRed mr-1"></i>',
            'permisos': 'Gestionar Productos, <i class="fa-solid fa-tags text-brandRed mx-1"></i> Categorías', 
            'icono_miembros': '<i class="fa-solid fa-user-group text-gray-400 mr-1"></i>',
            'miembros': 2, 
            'estado': 'Activo'
        },
        {
            'rol': 'Gestor de Proveedores', 
            'descripcion': 'Gestión de proveedores, ver productos.', 
            'icono_permiso': '<i class="fa-solid fa-truck text-brandRed mr-1"></i>',
            'permisos': 'Gestionar Proveedores, Ver Productos', 
            'icono_miembros': '<i class="fa-solid fa-user text-gray-400 mr-1"></i>',
            'miembros': 1, 
            'estado': 'Activo'
        },
        {
            'rol': 'Visor de Reportes', 
            'descripcion': 'Solo lectura de reportes.', 
            'icono_permiso': '<i class="fa-solid fa-chart-line text-brandRed mr-1"></i>',
            'permisos': 'Ver Reportes', 
            'icono_miembros': '<i class="fa-solid fa-user text-gray-400 mr-1"></i>',
            'miembros': 1, 
            'estado': 'Activo'
        }
    ]

    return render_template('configuracion.html', resumen=resumen_roles, roles=lista_roles)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
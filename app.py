from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///torquestock.db' # Crea un archivo torquestock.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DE BASE DE DATOS (Nuestra Tabla de Productos) ---
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))
    marca = db.Column(db.String(50))
    stock = db.Column(db.Integer, default=0)
    precio = db.Column(db.String(20))
    estado = db.Column(db.String(20), default='Activo')

# Crear la base de datos y las tablas automáticamente si no existen
with app.app_context():
    db.create_all()

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

@app.route('/productos', methods=['GET', 'POST'])
def productos():
    # 1. DE FRONTEND A BASE DE DATOS (Crear un producto)
    if request.method == 'POST':
        # Capturamos los datos que envíe tu formulario HTML
        nuevo_producto = Producto(
            sku=request.form['sku'],
            nombre=request.form['nombre'],
            categoria=request.form['categoria'],
            marca=request.form['marca'],
            stock=int(request.form['stock']),
            precio=request.form['precio'],
            estado=request.form.get('estado', 'Activo')
        )
        db.session.add(nuevo_producto) # Prepara el guardado
        db.session.commit()            # Guarda en la base de datos
        return redirect(url_for('productos')) # Recarga la página

    # 2. DE BASE DE DATOS A FRONTEND (Leer productos)
    productos_db = Producto.query.all() # Trae TODOS los productos de la BD

    # Calculamos datos reales para tus tarjetas basados en la BD!
    resumen_prod = {
        'total': len(productos_db),
        'stock_bajo': sum(1 for p in productos_db if p.stock < 25),
        'valor_total': '$---', # Lo dejaremos pendiente para no complicarlo
        'nuevas_adiciones': '0'
    }
    
    datos_grafica = [50, 80, 250, 190, 300, 230, 480, 250, 350, 350, 500]

    # Pasamos los productos reales en lugar de tu lista simulada
    return render_template('productos.html', resumen=resumen_prod, productos=productos_db, ventas=datos_grafica)

@app.route('/categorias')
def categorias():
    # Datos simulados para las tarjetas de resumen de categorías
    resumen_cat = {
        'total_categorias': 12,
        'mas_rentable': 'Llantas',
        'detalle_rentable': '80% de Ingresos (Clase A)',
        'menor_rotacion': 'Cascos',
        'detalle_rotacion': '1 venta'
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
    }
    
    # Datos simulados para la tabla de proveedores
    lista_proveedores = [
        {'nombre': 'Pirelli Tyres S.A.', 'contacto': 'John Doe', 'correo': 'j.doe@pirelli.com', 'telefono': '+34 600123456', 'suministro': 'Llantas', 'estado': 'Activo'},
        {'nombre': 'MT Helmets Iberia', 'contacto': 'Jane Smith', 'correo': 'jane@mthelmets.com', 'telefono': '+34 600123456', 'suministro': 'Cascos', 'estado': 'Activo'},
        {'nombre': 'Motul Oil Co.', 'contacto': 'Robert Brown', 'correo': 'robert@motul.com', 'telefono': '+34 600123456', 'suministro': 'Aceites', 'estado': 'Activo'},
        {'nombre': 'Fox Racing Supply', 'contacto': 'Alice Davis', 'correo': 'alice@davis.com', 'telefono': '+34 600123456', 'suministro': 'Aceites', 'estado': 'Crítico'},
        {'nombre': 'Bridgestone', 'contacto': 'Carlos Rodriguez', 'correo': 'carlos@bridguerz.com', 'telefono': '+34 600123456', 'suministro': 'Equipamiento', 'estado': 'Activo'},
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

# Ruta de MOVIMIENTOS (nueva página)
@app.route('/movimientos')
def movimientos():
    # Datos más completos para mostrar en la tabla
    movimientos = [
        {'item': 'Casco MT Helmets', 'tipo': 'entrada', 'cantidad': '+10', 'fecha': '02/02/2026', 'proveedor_cliente': 'Distribuidora Motos SAS'},
        {'item': 'Aceite Motul 10W40', 'tipo': 'entrada', 'cantidad': '+20', 'fecha': '03/07/2026', 'proveedor_cliente': 'Lubricantes Premium'},
        {'item': 'Llantas Pirelli', 'tipo': 'salida', 'cantidad': '-2', 'fecha': '03/07/2026', 'proveedor_cliente': 'Cliente: Juan Pérez'},
        {'item': 'Frenos Brembo', 'tipo': 'entrada', 'cantidad': '+5', 'fecha': '04/07/2026', 'proveedor_cliente': 'Importadora de Llantas'},
        {'item': 'Kit de Transmisión DID', 'tipo': 'salida', 'cantidad': '-1', 'fecha': '05/07/2026', 'proveedor_cliente': 'Cliente: María Gómez'},
        {'item': 'Aceite Motul 20W50', 'tipo': 'nuevo', 'cantidad': '+15', 'fecha': '06/07/2026', 'proveedor_cliente': 'Producto nuevo'},
    ]
    
    return render_template('movimientos.html', movimientos=movimientos)

@app.route('/configuracion')
def configuracion():
    # Datos simulados para las tarjetas de resumen
    resumen_roles = {
        'total': 4,
        'administradores': 1,
        'operadores': 2,
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
    ]

    return render_template('configuracion.html', resumen=resumen_roles, roles=lista_roles)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
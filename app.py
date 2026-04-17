from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///torquestock.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS DE BASE DE DATOS ---

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))
    marca = db.Column(db.String(50))
    stock = db.Column(db.Integer, default=0)
    precio = db.Column(db.String(20))
    estado = db.Column(db.String(20), default='Activo')

class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    correo = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    suministro = db.Column(db.String(100))
    estado = db.Column(db.String(20), default='Activo')

class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20)) # entrada / salida / nuevo
    cantidad = db.Column(db.String(20))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    proveedor_cliente = db.Column(db.String(100))

# Crear la base de datos automáticamente
with app.app_context():
    db.create_all()

# --- RUTAS ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Datos dinámicos para el dashboard
    total_prod = Producto.query.count()
    stock_bajo = Producto.query.filter(Producto.stock < 10).count()
    ultimos_movimientos = Movimiento.query.order_by(Movimiento.fecha.desc()).limit(5).all()
    
    resumen = {
        'total_productos': f"{total_prod:,}",
        'stock_bajo': str(stock_bajo),
        'valor_inventario': "$0.00" # Cálculo pendiente
    }
    
    return render_template('dashboard.html', resumen=resumen, movimientos=ultimos_movimientos)

@app.route('/productos', methods=['GET', 'POST'])
def productos():
    if request.method == 'POST':
        nuevo_p = Producto(
            sku=request.form['sku'],
            nombre=request.form['nombre'],
            categoria=request.form['categoria'],
            marca=request.form['marca'],
            stock=int(request.form['stock']),
            precio=request.form['precio'],
            estado=request.form.get('estado', 'Activo')
        )
        db.session.add(nuevo_p)
        db.session.commit()
        return redirect(url_for('productos'))

    productos_db = Producto.query.all()
    resumen_prod = {
        'total': len(productos_db),
        'stock_bajo': sum(1 for p in productos_db if p.stock < 25),
        'valor_total': '$---',
        'nuevas_adiciones': '0'
    }
    datos_grafica = [50, 80, 250, 190, 300, 230, 480, 250, 350, 350, 500]
    return render_template('productos.html', resumen=resumen_prod, productos=productos_db, ventas=datos_grafica)

@app.route('/categorias', methods=['GET', 'POST'])
def categorias():
    if request.method == 'POST':
        nueva_c = Categoria(
            nombre=request.form['nombre'],
            descripcion=request.form.get('descripcion', '')
        )
        db.session.add(nueva_c)
        db.session.commit()
        return redirect(url_for('categorias'))

    categorias_db = Categoria.query.all()
    resumen_cat = {
        'total_categorias': len(categorias_db),
        'mas_rentable': 'N/A',
        'detalle_rentable': '-',
        'menor_rotacion': 'N/A',
        'detalle_rotacion': '-'
    }
    return render_template('categorias.html', resumen=resumen_cat, lista_categorias=categorias_db)

@app.route('/proveedores', methods=['GET', 'POST'])
def proveedores():
    if request.method == 'POST':
        nuevo_prov = Proveedor(
            nombre=request.form['nombre'],
            contacto=request.form['contacto'],
            correo=request.form['correo'],
            telefono=request.form['telefono'],
            suministro=request.form['suministro'],
            estado=request.form.get('estado', 'Activo')
        )
        db.session.add(nuevo_prov)
        db.session.commit()
        return redirect(url_for('proveedores'))

    proveedores_db = Proveedor.query.all()
    resumen_prov = {
        'total': len(proveedores_db),
        'activos': sum(1 for p in proveedores_db if p.estado == 'Activo'),
    }
    return render_template('proveedores.html', resumen=resumen_prov, proveedores=proveedores_db)

@app.route('/movimientos', methods=['GET', 'POST'])
def movimientos():
    if request.method == 'POST':
        tipo_mov = request.form.get('tipo')

        # --- CASO 1: AÑADIR PRODUCTO NUEVO DESDE EL MODAL ---
        if tipo_mov == 'nuevo':
            # Capturamos los datos del formulario (usando los 'name' que pondremos en el HTML)
            stock_inicial = int(request.form.get('stock', 0))
            nuevo_p = Producto(
                sku=request.form.get('sku'),
                nombre=request.form.get('nombre'),
                categoria=request.form.get('categoria'),
                marca=request.form.get('marca'),
                precio=request.form.get('precio'),
                stock=stock_inicial,
                estado='Activo'
            )
            db.session.add(nuevo_p)
            
            # También registramos el movimiento inicial en el historial
            historial = Movimiento(
                item=nuevo_p.nombre,
                tipo='nuevo',
                cantidad=f"+{stock_inicial}",
                proveedor_cliente="Registro Inicial"
            )
            db.session.add(historial)
            db.session.commit()
            return redirect(url_for('movimientos'))

        # --- CASO 2: ENTRADA O SALIDA DE PRODUCTO EXISTENTE ---
        item_nombre = request.form.get('item')
        producto = Producto.query.filter_by(nombre=item_nombre).first()

        if producto:
            # Determinamos la cantidad según el modal abierto
            if tipo_mov == 'entrada':
                cantidad = int(request.form.get('cantidad_ingreso', 0))
                producto.stock += cantidad
                signo = "+"
            else:
                cantidad = int(request.form.get('cantidad_salida', 0))
                producto.stock -= cantidad
                signo = "-"

            nuevo_mov = Movimiento(
                item=producto.nombre,
                tipo=tipo_mov,
                cantidad=f"{signo}{cantidad}",
                proveedor_cliente=request.form.get('proveedor_cliente')
            )
            db.session.add(nuevo_mov)
            db.session.commit()

        return redirect(url_for('movimientos'))

    # Carga inicial de la página
    movimientos_db = Movimiento.query.order_by(Movimiento.fecha.desc()).all()
    productos_db = Producto.query.all()
    return render_template('movimientos.html', movimientos=movimientos_db, productos=productos_db)

@app.route('/reportes')
def reportes():
    dias_mes = [f"Nov {str(i).zfill(2)}" for i in range(1, 31)]
    datos_ventas = [90, 40, 100, 150, 90, 120, 200, 150, 140, 220, 210, 230, 220, 390, 310, 250, 350, 320, 260, 200, 300, 190, 220, 240, 190, 210, 250, 180, 210, 230]
    return render_template('reportes.html', dias=dias_mes, ventas=datos_ventas)

@app.route('/configuracion')
def configuracion():
    resumen_roles = {'total': 4, 'administradores': 1, 'operadores': 2}
    # Mantener roles simulados por ahora ya que no hay tabla de usuarios/roles definida aún
    lista_roles = [
        {'rol': 'Administrador', 'descripcion': 'Acceso total.', 'permisos': 'Todo', 'miembros': 1, 'estado': 'Activo'},
        {'rol': 'Operador', 'descripcion': 'Gestión de inventario.', 'permisos': 'Productos', 'miembros': 2, 'estado': 'Activo'}
    ]
    return render_template('configuracion.html', resumen=resumen_roles, roles=lista_roles)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
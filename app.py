from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash # Para cifrar contraseñas
from datetime import datetime, timedelta, timezone
from sqlalchemy import extract
from functools import wraps
from werkzeug.utils import secure_filename
import calendar
import base64
import os

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA APLICACIÓN Y BASE DE DATOS ---
app.config['SECRET_KEY'] = 'mi_llave_super_secreta_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///torquestock.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS DE BASE DE DATOS ---

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))
    fecha_creacion = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class Producto(db.Model):
    __tablename__ = 'producto' # Opcional, pero buena práctica
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))
    marca = db.Column(db.String(50))
    stock = db.Column(db.Integer, default=0)
    precio_compra = db.Column(db.String(20), default="0") # ¡NUEVA COLUMNA!
    precio = db.Column(db.String(20)) # Este lo dejamos como Precio de Venta
    estado = db.Column(db.String(20), default='Activo')
    imagen = db.Column(db.String(255), default='default.png')

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    correo = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    suministro = db.Column(db.String(100))
    estado = db.Column(db.String(20), default='Activo')

class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20)) # entrada / salida / nuevo
    cantidad = db.Column(db.String(20))
    fecha = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    proveedor_cliente = db.Column(db.String(100))

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False) # Será el correo
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), default='Operador') # Administrador / Operador

# Crear base de datos y usuario inicial
with app.app_context():
    db.create_all()
    if not Usuario.query.filter_by(username='admin@torquebikers.com').first():
        admin_pass = generate_password_hash('admin123')
        nuevo_admin = Usuario(username='admin@torquebikers.com', password=admin_pass, rol='Administrador')
        db.session.add(nuevo_admin)
        db.session.commit()

# --- BARRERAS DE SEGURIDAD (DECORADORES) ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Si no hay un ID de usuario en la sesión, lo mandamos al login
        if 'user_id' not in session:
            flash('Por favor, inicia sesión para acceder al sistema.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Primero validamos que esté logueado
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        if session.get('user_rol') != 'Administrador':
            flash('Acceso denegado: Se requieren permisos de Administrador.', 'error')
            return redirect(request.referrer or url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form.get('username')
        user_pass = request.form.get('password')
        
        user = Usuario.query.filter_by(username=user_email).first()
        
        # Comparamos la contraseña ingresada con el Hash de la DB
        if user and check_password_hash(user.password, user_pass):
            session['user_id'] = user.id
            session['user_rol'] = user.rol
            session['username'] = user.username  # <-- AÑADE ESTA LÍNEA
            return redirect(url_for('dashboard'))
        else:
            flash('Correo o contraseña incorrectos.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Borra todos los datos de la sesión actual
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # 1. Cálculos para las Tarjetas de Resumen
    total_prod = Producto.query.count()
    stock_bajo = Producto.query.filter(Producto.stock < 10).count()
    
    # Cálculo real del valor total del inventario (Basado en Precio de Compra)
    productos = Producto.query.filter(Producto.stock > 0).all()
    valor_total = 0
    for p in productos:
        try:
            # Extraemos y limpiamos el precio_compra en lugar del precio de venta
            p_compra = float(str(p.precio_compra).replace('$', '').replace(',', ''))
            valor_total += p_compra * p.stock
        except:
            pass
            
    resumen = {
        'total_productos': f"{total_prod:,}",
        'stock_bajo': str(stock_bajo),
        'valor_inventario': f"${valor_total:,.2f}"
    }

    # 2. Últimos Movimientos para la Tabla
    ultimos_movimientos = Movimiento.query.order_by(Movimiento.fecha.desc()).limit(6).all()
    
    # 3. Datos para la Gráfica (Corrección de Zona Horaria Colombia)
    hoy = datetime.now()
    ventas_por_dia = {}
    
    # 3.1 Preparamos el calendario de los últimos 7 días (Hora Local)
    for i in range(6, -1, -1):
        dia_str = (hoy - timedelta(days=i)).strftime('%d/%m')
        ventas_por_dia[dia_str] = 0
        
    # 3.2 Traemos TODOS los movimientos
    todos_movimientos = Movimiento.query.all()
    
    # 3.3 Agrupamos corrigiendo el desfase horario
    for mov in todos_movimientos:
        # Validamos que sea una salida monetaria
        if mov.tipo and str(mov.tipo).strip().lower() in ['salida', 'salida - venta'] and mov.fecha:
            
            # ¡EL TRUCO! Restamos 5 horas a la BD para sincronizar con Colombia (-5 GMT)
            fecha_real = mov.fecha - timedelta(hours=5)
            dia_mov = fecha_real.strftime('%d/%m')
            
            # Si este movimiento ocurrió en los últimos 7 días, lo sumamos
            if dia_mov in ventas_por_dia:
                try:
                    # Limpiamos el texto y lo forzamos a ser un número entero positivo
                    valor_str = str(mov.cantidad).replace('+', '').replace('-', '').strip()
                    valor_limpio = abs(int(float(valor_str)))
                    ventas_por_dia[dia_mov] += valor_limpio
                except:
                    pass

    grafica_dashboard = {
        'labels': list(ventas_por_dia.keys()),
        'data': list(ventas_por_dia.values())
    }
    
    return render_template('dashboard.html', 
                           resumen=resumen, 
                           movimientos=ultimos_movimientos,
                           grafica=grafica_dashboard)

@app.route('/productos', methods=['GET', 'POST'])
@login_required
def productos():
    if request.method == 'POST':
        # --- VALIDACIÓN DE SEGURIDAD ---
        if session.get('user_rol') != 'Administrador':
            flash('No tienes permiso para crear productos.', 'error')
            return redirect(url_for('productos'))
        # -------------------------------

        imagen_file = request.files.get('imagen')
        filename = 'default.png' # Imagen por defecto si no suben nada
        
        if imagen_file and imagen_file.filename != '':
            filename = secure_filename(imagen_file.filename)
            # Creamos la carpeta de productos si no existe
            ruta_carpeta = os.path.join(app.root_path, 'static', 'img', 'productos')
            os.makedirs(ruta_carpeta, exist_ok=True)
            imagen_file.save(os.path.join(ruta_carpeta, filename))
        
        stock_inicial = int(request.form.get('stock', 0))
        
        nuevo_p = Producto(
            sku=request.form.get('sku'),
            nombre=request.form.get('nombre'),
            categoria=request.form.get('categoria'),
            marca=request.form.get('marca'),
            stock=stock_inicial,
            precio_compra=request.form.get('precio_compra', '0'), # Guardamos el de compra
            precio=request.form.get('precio', '0'),               # Guardamos el de venta
            estado=request.form.get('estado', 'Activo'),
            imagen=filename
        )
        db.session.add(nuevo_p)
        
        historial = Movimiento(
            item=nuevo_p.nombre,
            tipo='nuevo',
            cantidad=f"+{stock_inicial}",
            proveedor_cliente="Registro Inicial"
        )
        db.session.add(historial)
        db.session.commit()
        return redirect(url_for('productos'))

    # --- 1. LÓGICA DE BÚSQUEDA Y FILTROS ---
    query = Producto.query
    
    # Capturamos lo que el usuario seleccionó (o valores por defecto)
    filtro_cat = request.args.get('categoria', 'Todas')
    filtro_marca = request.args.get('marca', 'Todas')
    filtro_estado = request.args.get('estado', 'Todos')
    busqueda = request.args.get('busqueda', '')

    # Aplicamos los filtros a la base de datos
    if filtro_cat != 'Todas':
        query = query.filter(Producto.categoria == filtro_cat)
    if filtro_marca != 'Todas':
        query = query.filter(Producto.marca == filtro_marca)
    if filtro_estado != 'Todos':
        query = query.filter(Producto.estado == filtro_estado)
    if busqueda:
        # Busca tanto por nombre como por SKU
        query = query.filter(Producto.nombre.ilike(f'%{busqueda}%') | Producto.sku.ilike(f'%{busqueda}%'))

    productos_filtrados = query.all()
    
    # --- 2. CÁLCULOS MATEMÁTICOS PARA LAS TARJETAS ---
    valor_total = 0
    for p in productos_filtrados:
        try:
            # Ahora calculamos el capital invertido basándonos SOLO en el precio de compra
            p_compra = float(str(p.precio_compra).replace('$', '').replace(',', ''))
            valor_total += p_compra * p.stock
        except:
            pass
            
    hoy = datetime.now(timezone.utc)
    # Buscamos en Movimientos los "nuevos" registrados este mes y año
    movimientos_nuevos = Movimiento.query.filter_by(tipo='nuevo').all()
    adiciones_mes = sum(1 for m in movimientos_nuevos if m.fecha.month == hoy.month and m.fecha.year == hoy.year)

    resumen_prod = {
        'total': len(productos_filtrados),
        'stock_bajo': sum(1 for p in productos_filtrados if p.stock < 10), # Asumimos < 10 como stock bajo
        'valor_total': f"${valor_total:,.2f}",
        'nuevas_adiciones': adiciones_mes
    }

    # --- 3. DATOS PARA LLENAR LOS SELECTS ---
    categorias_db = Categoria.query.all() 
    todas_las_marcas = db.session.query(Producto.marca).distinct().all()
    marcas_db = [m[0] for m in todas_las_marcas if m[0]]
    
    # --- 4. DATOS REALES PARA LA GRÁFICA DE CADA PRODUCTO ---
    hoy = datetime.now()
    dias_labels = [(hoy - timedelta(days=i)).strftime('%d/%m') for i in range(6, -1, -1)]
    
    # Traemos todos los movimientos de salida
    salidas = Movimiento.query.filter(db.func.lower(Movimiento.tipo).in_(['salida', 'salida - venta'])).all()
    
    datos_grafica_productos = {}
    for p in productos_filtrados:
        ventas_prod = {dia: 0 for dia in dias_labels}
        for mov in salidas:
            # Si la salida es de este producto en específico
            if mov.item == p.nombre and mov.fecha:
                fecha_real = mov.fecha - timedelta(hours=5) # Ajuste de Zona Horaria Colombia
                dia_str = fecha_real.strftime('%d/%m')
                
                if dia_str in ventas_prod:
                    try:
                        cant = abs(int(str(mov.cantidad).replace('+', '').replace('-', '').strip()))
                        ventas_prod[dia_str] += cant
                    except:
                        pass
        
        # Guardamos la data usando el ID del producto como llave
        datos_grafica_productos[p.id] = {
            'nombre': p.nombre,
            'labels': list(ventas_prod.keys()),
            'data': list(ventas_prod.values()),
            'imagen': p.imagen or 'default.png'
        }
    
    return render_template('productos.html', 
                           resumen=resumen_prod, 
                           productos=productos_filtrados, 
                           ventas=datos_grafica_productos, 
                           categorias=categorias_db,
                           marcas=marcas_db,
                           # Pasamos los filtros de vuelta al HTML para que el Select no se reinicie
                           filtro_cat=filtro_cat,
                           filtro_marca=filtro_marca,
                           filtro_estado=filtro_estado,
                           busqueda=busqueda)

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
@admin_required
def eliminar_producto(id):
    # Buscamos el producto
    producto = Producto.query.get_or_404(id)
    
    # 1. Registramos el movimiento de eliminación en el historial
    historial = Movimiento(
        item=producto.nombre,
        tipo='eliminado',
        cantidad=f"-{producto.stock}", # Indicamos que se retiró todo el stock restante
        proveedor_cliente="Eliminado del catálogo" # Usamos este campo para la justificación
    )
    db.session.add(historial)
    
    # 2. Ahora sí, borramos el producto de la base de datos
    db.session.delete(producto)
    db.session.commit()
    
    return redirect(url_for('productos'))

@app.route('/editar_producto/<int:id>', methods=['POST'])
@admin_required
def editar_producto(id):
    # Validamos que el usuario esté logueado (si aplicaste el paso anterior)
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Buscamos el producto en la base de datos
    producto = Producto.query.get_or_404(id)
    
    # Actualizamos únicamente los campos permitidos
    producto.sku = request.form.get('sku')
    producto.nombre = request.form.get('nombre')
    producto.categoria = request.form.get('categoria')
    producto.precio_compra = request.form.get('precio_compra')
    producto.precio = request.form.get('precio')
    
    # Guardamos los cambios
    db.session.commit()
    flash('Producto editado correctamente.', 'success')
    return redirect(url_for('productos'))

@app.route('/categorias', methods=['GET', 'POST'])
@login_required
def categorias():
    if request.method == 'POST':
        # --- VALIDACIÓN DE SEGURIDAD ---
        if session.get('user_rol') != 'Administrador':
            flash('No tienes permiso para crear categorías.', 'error')
            return redirect(url_for('categorias'))
        # -------------------------------
        nueva_c = Categoria(
            nombre=request.form['nombre'],
            descripcion=request.form.get('descripcion', '')
        )
        db.session.add(nueva_c)
        db.session.commit()
        return redirect(url_for('categorias'))

    # Traemos todos los datos necesarios
    categorias_db = Categoria.query.all()
    productos_db = Producto.query.all()
    
    # Buscamos los movimientos de "salida" monetaria de los últimos 30 días
    hace_30_dias = datetime.now(timezone.utc) - timedelta(days=30)
    movimientos_salida = Movimiento.query.filter(
        db.func.lower(Movimiento.tipo).in_(['salida', 'salida - venta']), 
        Movimiento.fecha >= hace_30_dias
    ).all()
    
    # Creamos un mapa rápido de productos para acceder a sus precios de compra y venta
    mapa_productos = {p.nombre: p for p in productos_db}
    
    # Preparamos el diccionario base
    stats_cat = {}
    for cat in categorias_db:
        stats_cat[cat.nombre] = {
            'cantidad': 0, 
            'valor_total_compra': 0.0, 
            'ventas_30_dias': 0, 
            'ganancia_30_dias': 0.0
        }
        
    # 1. Calculamos Cantidad de Productos y Valor Total (basado en precio COMPRA)
    for p in productos_db:
        if p.categoria in stats_cat:
            stats_cat[p.categoria]['cantidad'] += 1
            try:
                # Usamos el precio_compra que creamos en el paso anterior
                p_compra = float(str(p.precio_compra).replace('$', '').replace(',', ''))
                stats_cat[p.categoria]['valor_total_compra'] += p_compra * p.stock
            except:
                pass
                
    # 2. Calculamos las rotaciones y GANANCIAS NETAS en los últimos 30 días
    for mov in movimientos_salida:
        prod = mapa_productos.get(mov.item)
        if prod and prod.categoria in stats_cat:
            try:
                cant = abs(int(str(mov.cantidad).replace('+', '').replace('-', '').strip()))
                p_compra = float(str(prod.precio_compra).replace('$', '').replace(',', ''))
                p_venta = float(str(prod.precio).replace('$', '').replace(',', ''))
                
                # Ganancia = Lo que gané por unidad * cantidad vendida
                ganancia_unitaria = p_venta - p_compra
                
                stats_cat[prod.categoria]['ventas_30_dias'] += cant
                stats_cat[prod.categoria]['ganancia_30_dias'] += (ganancia_unitaria * cant)
            except:
                pass

    # 3. Asignamos los cálculos a los objetos que irán al HTML
    for cat in categorias_db:
        cat.cantidad_productos = stats_cat[cat.nombre]['cantidad']
        cat.valor_total = stats_cat[cat.nombre]['valor_total_compra']
        
    # 4. Buscamos a los ganadores (Más Rentable y Menor Rotación)
    mas_rentable = 'N/A'
    detalle_rentable = '-'
    menor_rotacion = 'N/A'
    detalle_rotacion = '-'
    
    cats_con_productos = {k: v for k, v in stats_cat.items() if v['cantidad'] > 0}
    
    if cats_con_productos:
        # Categoría Más Rentable (La que genera MAYOR ganancia neta)
        cat_mas_rentable = max(cats_con_productos.items(), key=lambda x: x[1]['ganancia_30_dias'])
        if cat_mas_rentable[1]['ventas_30_dias'] > 0:
            mas_rentable = cat_mas_rentable[0]
            detalle_rentable = f"${cat_mas_rentable[1]['ganancia_30_dias']:,.2f} de ganancia ({cat_mas_rentable[1]['ventas_30_dias']} ventas)"
        
        # Categoría con Menor Rotación (MENOR cantidad de ventas, y si hay empate, menor ganancia)
        cat_menor_rot = min(cats_con_productos.items(), key=lambda x: (x[1]['ventas_30_dias'], x[1]['ganancia_30_dias']))
        menor_rotacion = cat_menor_rot[0]
        detalle_rotacion = f"{cat_menor_rot[1]['ventas_30_dias']} ventas (${cat_menor_rot[1]['ganancia_30_dias']:,.2f} de ganancia)"

    resumen_cat = {
        'total_categorias': len(categorias_db),
        'mas_rentable': mas_rentable,
        'detalle_rentable': detalle_rentable,
        'menor_rotacion': menor_rotacion,
        'detalle_rotacion': detalle_rotacion
    }
    
    return render_template('categorias.html', resumen=resumen_cat, lista_categorias=categorias_db)

@app.route('/eliminar_categoria/<int:id>', methods=['POST'])
@login_required # Añadido por seguridad
def eliminar_categoria(id):
    # 1. Obtener la categoría a eliminar usando SQLAlchemy
    categoria = Categoria.query.get_or_404(id)
    nombre_categoria = categoria.nombre
    
    # 2. Verificar si existen productos con este nombre de categoría
    cantidad_productos = Producto.query.filter_by(categoria=nombre_categoria).count()
    
    if cantidad_productos > 0:
        # Si hay productos, lanzamos error y NO eliminamos
        flash(f'Error: No se puede eliminar. Hay {cantidad_productos} productos asociados a la categoría "{nombre_categoria}".', 'error')
        return redirect(url_for('categorias'))
    
    # 3. Si no hay productos, procedemos a eliminar
    db.session.delete(categoria)
    db.session.commit()
    flash('Categoría eliminada exitosamente.', 'success')
        
    return redirect(url_for('categorias'))

@app.route('/editar_categoria/<int:id>', methods=['POST'])
@login_required # Añadido por seguridad
def editar_categoria(id):
    nuevo_nombre = request.form['nombre']
    descripcion = request.form.get('descripcion', '')
    
    # 1. Obtener la categoría actual desde la base de datos
    categoria = Categoria.query.get_or_404(id)
    nombre_viejo = categoria.nombre
    
    # 2. Actualizar los datos de la categoría
    categoria.nombre = nuevo_nombre
    categoria.descripcion = descripcion
    
    # 3. ACTUALIZAR LOS PRODUCTOS ASOCIADOS (Si el nombre cambió)
    if nombre_viejo != nuevo_nombre:
        # Buscamos todos los productos que tienen la categoría vieja
        productos_asociados = Producto.query.filter_by(categoria=nombre_viejo).all()
        
        # Iteramos y les asignamos el nuevo nombre
        for prod in productos_asociados:
            prod.categoria = nuevo_nombre
            
    # Hacemos un solo commit para guardar la categoría y los productos editados
    db.session.commit()
    flash('Categoría actualizada correctamente en el inventario.', 'success')
    return redirect(url_for('categorias'))

@app.route('/proveedores', methods=['GET', 'POST'])
@login_required
def proveedores():
    if request.method == 'POST':
        # --- VALIDACIÓN DE SEGURIDAD ---
        if session.get('user_rol') != 'Administrador':
            flash('No tienes permiso para crear proveedores.', 'error')
            return redirect(url_for('proveedores'))
        # -------------------------------
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

    # --- LÓGICA DE BÚSQUEDA Y FILTROS ---
    query = Proveedor.query
    
    filtro_estado = request.args.get('estado', 'Todos')
    filtro_suministro = request.args.get('suministro', 'Todos')
    busqueda = request.args.get('busqueda', '')

    if filtro_estado != 'Todos':
        query = query.filter(Proveedor.estado == filtro_estado)
    if filtro_suministro != 'Todos':
        query = query.filter(Proveedor.suministro == filtro_suministro)
    if busqueda:
        query = query.filter(Proveedor.nombre.ilike(f'%{busqueda}%') | Proveedor.contacto.ilike(f'%{busqueda}%'))

    proveedores_filtrados = query.all()
    
    # --- DATOS PARA EL SELECT DE SUMINISTROS ---
    categorias_db = Categoria.query.all()

    resumen_prov = {
        'total': len(proveedores_filtrados),
        'activos': sum(1 for p in proveedores_filtrados if p.estado == 'Activo'),
    }
    
    return render_template('proveedores.html', 
                           resumen=resumen_prov, 
                           proveedores=proveedores_filtrados,
                           categorias=categorias_db,
                           filtro_estado=filtro_estado,
                           filtro_suministro=filtro_suministro,
                           busqueda=busqueda)

@app.route('/eliminar_proveedor/<int:id>', methods=['POST'])
@admin_required
def eliminar_proveedor(id):
    # Buscamos el proveedor en la base de datos por su ID
    proveedor_a_eliminar = Proveedor.query.get_or_404(id)
    
    # Eliminamos el registro
    db.session.delete(proveedor_a_eliminar)
    db.session.commit()
    
    # Redirigimos de vuelta a la vista de proveedores
    return redirect(url_for('proveedores'))

@app.route('/editar_proveedor/<int:id>', methods=['POST'])
@admin_required
def editar_proveedor(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    proveedor = Proveedor.query.get_or_404(id)
    
    # Actualizar valores
    proveedor.nombre = request.form.get('nombre')
    proveedor.contacto = request.form.get('contacto')
    proveedor.correo = request.form.get('correo')
    proveedor.telefono = request.form.get('telefono')
    proveedor.suministro = request.form.get('suministro')
    proveedor.estado = request.form.get('estado')
    
    db.session.commit()
    flash('Proveedor actualizado correctamente.', 'success')
    
    return redirect(url_for('proveedores'))

@app.route('/movimientos', methods=['GET', 'POST'])
@login_required
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
                nombre_prod = request.form.get('item')
                cant = int(request.form.get('cantidad_ingreso', 0))
                proveedor = request.form.get('proveedor_cliente')

                producto = Producto.query.filter_by(nombre=nombre_prod).first()
                if producto:
                    producto.stock += cant
                    # Al ingresar stock, el producto vuelve a estar Activo
                    if producto.stock > 0:
                        producto.estado = 'Activo'

                    nuevo_mov = Movimiento(
                        item=producto.nombre,
                        tipo='entrada',
                        cantidad=f"+{cant}",
                        proveedor_cliente=proveedor
                    )
                    db.session.add(nuevo_mov)
                    db.session.commit()
                    flash('Ingreso registrado correctamente.', 'success')

            elif tipo_mov == 'salida':
                nombre_prod = request.form.get('item')
                cant = int(request.form.get('cantidad_salida', 0))
                cliente = request.form.get('proveedor_cliente')
                
                # NUEVO: Capturamos el motivo de la salida (por defecto 'venta')
                motivo = request.form.get('motivo_salida', 'venta')

                producto = Producto.query.filter_by(nombre=nombre_prod).first()
                if producto:
                    # VALIDACIÓN CRÍTICA: No permitir vender más del stock disponible
                    if cant > producto.stock:
                        flash(f'Error: Solo hay {producto.stock} existencias de {producto.nombre}.', 'error')
                        return redirect(url_for('movimientos'))

                    producto.stock -= cant
                    # Si el stock llega a 0, se inactiva automáticamente
                    if producto.stock == 0:
                        producto.estado = 'Inactivo'

                    # NUEVO: Guardamos el tipo de salida compuesto (Ej: "salida - venta", "salida - pérdida")
                    nuevo_mov = Movimiento(
                        item=producto.nombre,
                        tipo=f"salida - {motivo.lower()}",
                        cantidad=f"-{cant}",
                        proveedor_cliente=cliente
                    )
                    db.session.add(nuevo_mov)
                    db.session.commit()
                    flash(f'Salida por {motivo.lower()} registrada correctamente.', 'success')

            return redirect(url_for('movimientos'))
    
    # --- 1. LÓGICA DE BÚSQUEDA Y FILTROS ---
    query = Movimiento.query
    
    filtro_tipo = request.args.get('tipo', 'Todos')
    busqueda = request.args.get('busqueda', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')

    # Filtrar por Tipo
    if filtro_tipo != 'Todos':
        # Mapeamos lo que viene del HTML a lo que guardamos en DB
        tipo_db = filtro_tipo.lower()
        if filtro_tipo == 'Ajuste': 
            tipo_db = 'nuevo' # Asumimos que los ajustes entran como "nuevo"
        query = query.filter(Movimiento.tipo == tipo_db)

    # Filtrar por Búsqueda (Producto o Proveedor/Cliente)
    if busqueda:
        query = query.filter(Movimiento.item.ilike(f'%{busqueda}%') | Movimiento.proveedor_cliente.ilike(f'%{busqueda}%'))

    # Filtrar por Rango de Fechas
    if fecha_desde:
        try:
            fd = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(Movimiento.fecha >= fd)
        except: pass
        
    if fecha_hasta:
        try:
            # Añadimos las horas hasta el final del día para incluir movimientos de ese mismo día
            fh = datetime.strptime(fecha_hasta, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(Movimiento.fecha <= fh)
        except: pass

    movimientos_db = query.order_by(Movimiento.fecha.desc()).all()
    
    # --- 2. TRAER DATOS PARA LOS MODALES ---
    categorias_db = Categoria.query.all()
    proveedores_db = Proveedor.query.filter_by(estado='Activo').all() # Traemos solo los activos
    productos_db = Producto.query.all()

    return render_template('movimientos.html', 
                           movimientos=movimientos_db,
                           productos=productos_db,
                           categorias=categorias_db,
                           proveedores=proveedores_db,
                           filtro_tipo=filtro_tipo,
                           busqueda=busqueda,
                           fecha_desde=fecha_desde,
                           fecha_hasta=fecha_hasta)

@app.route('/reportes')
@login_required
def reportes():
    hoy = datetime.now()

    # 1. Opciones de Meses (Generamos los últimos 12 meses fijos, con o sin datos)
    opciones_meses = []
    meses_es = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    for i in range(12): # Genera 12 meses hacia atrás. Puedes poner 24 si necesitas 2 años.
        mes_calculado = hoy.month - i
        anio_calculado = hoy.year
        
        # Ajuste matemático si retrocedemos al año anterior
        if mes_calculado <= 0:
            mes_calculado += 12
            anio_calculado -= 1
            
        nombre_mes = meses_es[mes_calculado]
        opciones_meses.append({
            'valor': f"{anio_calculado}-{mes_calculado:02d}", 
            'label': f"{nombre_mes} {anio_calculado}"
        })

    # Pre-cache de precios para calcular ingresos de ventas rápidamente
    productos_all = Producto.query.all()
    precios_venta = {}
    for p in productos_all:
        try:
            precios_venta[p.nombre] = float(str(p.precio).replace('$', '').replace(',', ''))
        except:
            precios_venta[p.nombre] = 0.0

    # --- DATOS PARA GRÁFICA 1: Ventas (Unidades e Ingresos) ---
    lbl_ventas = []
    
    # Traer todos los movimientos de salida de los últimos 30 días (solo ventas reales)
    hace_30 = hoy - timedelta(days=30)
    movimientos_salida = Movimiento.query.filter(
        db.func.lower(Movimiento.tipo).in_(['salida', 'salida - venta']), 
        Movimiento.fecha >= hace_30
    ).all()

    dict_unidades = {}
    dict_ingresos = {}
    ventas_mes_actual = 0.0
    
    # Preparamos los últimos 30 días
    for i in range(29, -1, -1):
        fecha = hoy - timedelta(days=i)
        lbl = fecha.strftime('%d %b')
        lbl_ventas.append(lbl)
        dict_unidades[lbl] = 0
        dict_ingresos[lbl] = 0.0

    # Llenamos con los datos reales
    for mov in movimientos_salida:
        fecha_real = mov.fecha - timedelta(hours=5) if mov.fecha else hoy
        lbl = fecha_real.strftime('%d %b')
        
        try:
            cant = abs(int(str(mov.cantidad).replace('-', '').replace('+', '').strip()))
        except: cant = 0
        
        precio_v = precios_venta.get(mov.item, 0.0)
        ingreso = cant * precio_v

        if lbl in dict_unidades:
            dict_unidades[lbl] += cant
            dict_ingresos[lbl] += ingreso
            
        # Sumar al recuento del mes actual
        if fecha_real.month == hoy.month and fecha_real.year == hoy.year:
            ventas_mes_actual += ingreso

    dat_ventas = [dict_unidades[lbl] for lbl in lbl_ventas]
    dat_ingresos = [dict_ingresos[lbl] for lbl in lbl_ventas]
    texto_recuento_mes = f"Total recaudado este mes: ${ventas_mes_actual:,.2f}"

    # --- DATOS PARA GRÁFICA 2: Inventario Bajo ---
    bajo_stock = Producto.query.filter(Producto.stock < 10).order_by(Producto.stock.asc()).limit(8).all()
    lbl_stock = [p.nombre[:15]+"..." if len(p.nombre)>15 else p.nombre for p in bajo_stock]
    dat_stock = [p.stock for p in bajo_stock]

    # --- DATOS PARA GRÁFICA 3: Valor por Categoría (AHORA POR PRECIO DE COMPRA) ---
    productos_stock = Producto.query.filter(Producto.stock > 0).all()
    valor_cat = {}
    for p in productos_stock:
        cat = p.categoria or 'Sin categoría'
        try:
            # CAMBIO: Usamos precio_compra en vez de precio
            precio_c = float(str(p.precio_compra).replace('$', '').replace(',', ''))
            valor_cat[cat] = valor_cat.get(cat, 0) + (precio_c * p.stock)
        except: pass
    lbl_valor = list(valor_cat.keys())
    dat_valor = list(valor_cat.values())

    # --- DATOS PARA GRÁFICA 4: Movimientos (Entradas y Salidas) ---
    lbl_mov = []
    dat_mov = []
    for i in range(14, -1, -1):
        fecha = hoy - timedelta(days=i)
        lbl_mov.append(fecha.strftime('%d %b'))
        cant = Movimiento.query.filter(db.func.date(Movimiento.fecha) == fecha.date()).count()
        dat_mov.append(cant)

    # Empaquetamos todo para enviarlo al HTML
    graficas = {
        'ventas': {
            'labels': lbl_ventas, 
            'data': dat_ventas, 
            'label': 'Unidades', 
            'data2': dat_ingresos,      # <- ¡Nuevo dataset de dinero!
            'label2': 'Ingresos ($)',
            'defType': 'line',
            'subtitulo': f'Tendencia de ventas de los últimos 30 días. {texto_recuento_mes}'
        },
        'bajo_stock': {'labels': lbl_stock, 'data': dat_stock, 'label': 'Unidades Restantes', 'defType': 'bar'},
        'valor_total': {'labels': lbl_valor, 'data': dat_valor, 'label': 'Capital Invertido ($)', 'defType': 'bar'},
        'movimientos': {'labels': lbl_mov, 'data': dat_mov, 'label': 'Transacciones Diarias', 'defType': 'line'}
    }

    return render_template('reportes.html', 
                           opciones_meses=opciones_meses,
                           graficas=graficas)

@app.route('/generar_reporte', methods=['POST'])
@login_required
def generar_reporte():
    tipo_reporte = request.form.get('tipo_reporte')
    periodo = request.form.get('periodo')
    
    datos = []
    titulo = "Reporte"
    columnas = []
    extra_data = {} # Nuevo diccionario para pasar totales generales al PDF
    
    # --- Convertir Logo a Base64 ---
    logo_base64 = ""
    tipo_img = "png" 
    ruta_png = os.path.join(app.root_path, 'static', 'img', 'Logo.png')
    ruta_jpg = os.path.join(app.root_path, 'static', 'img', 'Logo.jpg')
    ruta_logo = ruta_png if os.path.exists(ruta_png) else ruta_jpg
    
    try:
        if os.path.exists(ruta_logo):
            if ruta_logo.endswith('.jpg'):
                tipo_img = "jpeg"
            with open(ruta_logo, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    except:
        pass

    # Extraer el mes y año
    if periodo:
        anio, mes = int(periodo.split('-')[0]), int(periodo.split('-')[1])
    else:
        anio, mes = datetime.now().year, datetime.now().month

    # --- LÓGICA DE REPORTES ---
    if tipo_reporte == 'ventas':
        titulo = f"Reporte Financiero de Ventas - {mes:02d}/{anio}"
        movimientos = Movimiento.query.filter(
            extract('year', Movimiento.fecha) == anio,
            extract('month', Movimiento.fecha) == mes,
            db.func.lower(Movimiento.tipo).in_(['salida', 'salida - venta']) # Solo suma ingresos reales
        ).all()
        
        # Diccionario rápido de precios de venta y compra
        productos_all = Producto.query.all()
        precios_venta = {}
        precios_compra = {}
        for p in productos_all:
            try: precios_venta[p.nombre] = float(str(p.precio).replace('$', '').replace(',', ''))
            except: precios_venta[p.nombre] = 0.0
            
            try: precios_compra[p.nombre] = float(str(p.precio_compra).replace('$', '').replace(',', ''))
            except: precios_compra[p.nombre] = 0.0

        total_mensual = 0.0
        ganancia_mensual = 0.0
        datos_enriquecidos = []
        
        for mov in movimientos:
            try: cant = abs(int(str(mov.cantidad).replace('-', '').replace('+', '').strip()))
            except: cant = 0
            
            precio_v = precios_venta.get(mov.item, 0.0)
            precio_c = precios_compra.get(mov.item, 0.0)
            
            ingreso_total = cant * precio_v
            costo_total = cant * precio_c
            ganancia_total = ingreso_total - costo_total
            
            total_mensual += ingreso_total
            ganancia_mensual += ganancia_total
            
            # Guardamos los datos calculados para la tabla
            datos_enriquecidos.append({
                'fecha': mov.fecha,
                'item': mov.item,
                'cantidad': cant,
                'precio_compra': precio_c,
                'precio_unitario': precio_v,
                'ingreso_total': ingreso_total,
                'ganancia_total': ganancia_total,
                'proveedor_cliente': mov.proveedor_cliente
            })
            
        datos = datos_enriquecidos
        # AÑADIDAS LAS NUEVAS COLUMNAS AL ENCABEZADO
        columnas = ['Fecha', 'Producto', 'Cant.', 'P. Compra', 'P. Venta', 'Ingreso', 'Ganancia', 'Cliente']
        extra_data['total_mensual'] = total_mensual 
        extra_data['ganancia_mensual'] = ganancia_mensual # Pasamos la ganancia al HTML
        
    elif tipo_reporte == 'movimientos':
        titulo = f"Historial de Movimientos - {mes:02d}/{anio}"
        datos = Movimiento.query.filter(
            extract('year', Movimiento.fecha) == anio,
            extract('month', Movimiento.fecha) == mes
        ).order_by(Movimiento.fecha.desc()).all()
        columnas = ['Fecha', 'Tipo', 'Producto', 'Cant.', 'Detalle']

    elif tipo_reporte == 'valor_total':
        titulo = "Valorización de Inventario"
        datos = Producto.query.filter(Producto.stock > 0).all()
        columnas = ['SKU', 'Producto', 'Stock', 'Precio Compra', 'Subtotal']
        
    elif tipo_reporte == 'bajo_stock':
        titulo = "Alerta de Bajo Stock Actual"
        datos = Producto.query.filter(Producto.stock < 10).all()
        columnas = ['SKU', 'Producto', 'Categoría', 'Stock Actual']

    return render_template('reporte_imprimir.html', 
                           titulo=titulo, 
                           tipo=tipo_reporte, 
                           datos=datos, 
                           columnas=columnas,
                           extra_data=extra_data, # Pasamos los totales
                           logo_b64=logo_base64,
                           tipo_img=tipo_img)

@app.route('/configuracion', methods=['GET', 'POST'])
@admin_required
def configuracion():
    if request.method == 'POST':
        # Lógica para añadir nuevo usuario desde el panel
        nuevo_user = request.form.get('nuevo_usuario')
        nueva_pass = request.form.get('nueva_password')
        rol = request.form.get('rol')
        
        if nuevo_user and nueva_pass:
            hashed_pass = generate_password_hash(nueva_pass)
            u = Usuario(username=nuevo_user, password=hashed_pass, rol=rol)
            db.session.add(u)
            db.session.commit()
            flash('Usuario creado con éxito.', 'success')
            return redirect(url_for('configuracion'))

    usuarios_db = Usuario.query.all()
    resumen_roles = {
        'total': len(usuarios_db),
        'administradores': Usuario.query.filter_by(rol='Administrador').count(),
        'operadores': Usuario.query.filter_by(rol='Operador').count()
    }
    return render_template('configuracion.html', resumen=resumen_roles, roles=usuarios_db)

@app.route('/eliminar_usuario/<int:id>', methods=['POST'])
@admin_required
def eliminar_usuario(id):
    # Prevenir que el usuario actual se elimine a sí mismo
    if session.get('user_id') == id:
        flash('No puedes eliminar tu propio usuario activo.', 'error')
        return redirect(url_for('configuracion'))

    user = Usuario.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado exitosamente.', 'success')
    
    return redirect(url_for('configuracion'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
import csv
from datetime import datetime
from app import app, db, Movimiento, Producto

def importar_datos_completos(archivo_csv):
    with app.app_context():
        try:
            # 1. Usamos 'utf-8-sig' para eliminar cualquier carácter invisible (BOM) que meta Excel
            with open(archivo_csv, mode='r', encoding='utf-8-sig') as file:
                
                # 2. Leemos la primera línea para adivinar si Excel usó comas o puntos y comas
                primera_linea = file.readline()
                file.seek(0) # Regresamos el cursor al inicio del archivo
                
                delimitador_detectado = ';' if ';' in primera_linea else ','
                
                # 3. Iniciamos el lector con el delimitador correcto
                lector = csv.DictReader(file, delimiter=delimitador_detectado)
                
                contador_movimientos = 0
                productos_creados = 0
                
                for fila in lector:
                    # 1. Parsear la fecha del CSV
                    fecha_real = datetime.strptime(fila['fecha'], '%Y-%m-%d')
                    cantidad_str = str(fila['cantidad']).replace('+', '').replace('-', '').strip()
                    cantidad_numerica = int(cantidad_str)
                    nombre_item = fila['item']
                    tipo_movimiento = fila['tipo'].lower().strip()

                    # 2. Verificar si el producto ya existe. Si no existe Y es un ingreso 'nuevo', lo creamos.
                    producto_existente = Producto.query.filter_by(nombre=nombre_item).first()
                    
                    if not producto_existente and tipo_movimiento == 'nuevo':
                        # Lógica para inferir la categoría basándonos en tu lista de proveedores
                        categoria_inferida = "Sin categoría"
                        if "Motul" in fila['proveedor_cliente'] or "Ipone" in fila['proveedor_cliente']:
                            categoria_inferida = "Lubricantes"
                        elif "Frenos" in fila['proveedor_cliente']:
                            categoria_inferida = "Frenos"
                        elif "Pirelli" in fila['proveedor_cliente']:
                            categoria_inferida = "Llantas"
                        elif "Light" in fila['proveedor_cliente']:
                            categoria_inferida = "Iluminación"
                        elif "Lujos" in fila['proveedor_cliente']:
                            categoria_inferida = "Protecciones"
                        elif "Cadenas" in fila['proveedor_cliente']:
                            categoria_inferida = "Kit de Arrastre"
                        elif "Surtimotores" in fila['proveedor_cliente']:
                            categoria_inferida = "Motor"
                        elif "Shaft" in fila['proveedor_cliente']:
                            categoria_inferida = "Suspensión"
                        elif "Pro" in fila['proveedor_cliente']:
                            categoria_inferida = "Herramientas"

                        # Generar un SKU básico basado en el nombre y un contador
                        nuevo_sku = f"SKU-{nombre_item[:3].upper()}-00{productos_creados + 1}"

                        nuevo_producto = Producto(
                            sku=nuevo_sku,
                            nombre=nombre_item,
                            categoria=categoria_inferida,
                            marca="Genérica", # Valor por defecto
                            stock=cantidad_numerica, # El stock inicial es la cantidad que ingresa
                            precio_compra="50000", # Valor por defecto a editar luego en la UI
                            precio="80000",        # Valor por defecto a editar luego en la UI
                            estado='Activo',
                            imagen='default.png'
                        )
                        db.session.add(nuevo_producto)
                        db.session.flush() # Guardamos temporalmente para asegurar que se cree
                        productos_creados += 1
                    
                    elif producto_existente:
                        # Si el producto YA existe, actualizamos su stock según el tipo de movimiento
                         if tipo_movimiento == 'entrada':
                             producto_existente.stock += cantidad_numerica
                             producto_existente.estado = 'Activo' # Reactivar si estaba en 0
                         elif 'salida' in tipo_movimiento:
                             producto_existente.stock -= cantidad_numerica
                             if producto_existente.stock <= 0:
                                 producto_existente.estado = 'Inactivo'

                    # 3. Registrar el movimiento histórico
                    nuevo_mov = Movimiento(
                        item=nombre_item,
                        tipo=tipo_movimiento,
                        cantidad=fila['cantidad'], # Guardamos el formato original con +/-
                        fecha=fecha_real,
                        proveedor_cliente=fila['proveedor_cliente']
                    )
                    db.session.add(nuevo_mov)
                    contador_movimientos += 1
                
                # 4. Hacer commit de todo (Productos y Movimientos)
                db.session.commit()
                print(f"✅ ¡Éxito! Se crearon {productos_creados} productos nuevos.")
                print(f"✅ Se importaron {contador_movimientos} movimientos históricos correctamente.")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al importar: {e}")

if __name__ == '__main__':
    # Asegúrate de que el nombre del archivo CSV coincida
    importar_datos_completos('historico.csv')
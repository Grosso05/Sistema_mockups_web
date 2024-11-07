#uod
import datetime
import os
from sqlite3 import IntegrityError
import uuid
from dateutil import parser
from flask import Blueprint, flash, json, jsonify, render_template, request, redirect, session, url_for,send_file
from flask_login import login_required, login_user, current_user
from matplotlib import cm
from models import Categoria, Cotizacion, ItemCotizado, ItemTemporal, Items, ItemsPorProducto, Lineas, PorcentajesProducto, ProductoCotizado, Productos, ResumenDeCostos, Users, ItemProveedores,db, PrecioEscalonado
from utils import roles_required
import locale
from datetime import datetime, timezone
from io import BytesIO
from flask import send_file
from reportlab.lib.pagesizes import legal, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image
from flask_login import current_user
from werkzeug.utils import secure_filename
from reportlab.platypus import XBox
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from flask import jsonify, request
from sqlalchemy import func

import locale
locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8') 
    
routes_blueprint = Blueprint('routes', __name__)

#ruta principal (index), ruta para generar catalogo del lado del cliente
@routes_blueprint.route('/')
def index():
    mensaje = request.args.get('mensaje', '')  # Obtener el mensaje de la URL
    return render_template('index.html', mensaje=mensaje)


#ruta para el dashboard de administrador
@routes_blueprint.route('/routes.admin')
@login_required
@roles_required(1)
def admin():
    if current_user.user_rol != 1:  # Verifica si el rol del usuario es igual a 1 (ID del rol de administrador)
        return redirect(url_for('users.login'))  # Redirige a la página de inicio de sesión u otra página 
    return render_template('/dashboard_admin.html',user_rol=current_user.user_rol)



@routes_blueprint.route('/routes.user')
@login_required
def user():
    if current_user.user_rol not in [2, 3]:
        return render_template(url_for('users.login'))
    return render_template('dashboard_user.html', user_rol=current_user.user_rol)

#Ruta para generar catalogo del lado del administrador
@routes_blueprint.route('/routes.generar_catalogo')
@login_required
@roles_required(1, 2, 3)  # Permitir acceso a roles 1, 2 y 3
def generar_catalogo():
    # Obtener el rol del usuario actual
    user_rol = current_user.user_rol
    return render_template('generar_catalogoregistrado.html', user_rol=current_user.user_rol)


#ruta para generar catalogo del lado del usuario
@routes_blueprint.route('/routes.generar_catalogouser')
@login_required
@roles_required(2)
def generar_catalogouser():
    return render_template('generarcatalogouserregistrado.html')

# <------------------------------------------------------------------ SISTEMA COTIZADOR --------------------------------------------------------------------------------->


@routes_blueprint.route('/generar_cotizacion')
@login_required
def generar_cotizacion():
    lineas = Lineas.query.all()
    productos = Productos.query.all()
    
    # Obtener todos los vendedores
    vendedores = Users.query.all()
    
    user_rol = current_user.user_rol if current_user.is_authenticated else None
    return render_template('generar_cotizacion.html', lineas=lineas, productos=productos, vendedores=vendedores, user_rol=user_rol, logged_user=current_user)


@routes_blueprint.route('/productos_por_linea/<int:linea_id>')
def productos_por_linea(linea_id):
    productos = Productos.query.filter_by(linea_idFK=linea_id).all()
    productos_json = []
    for producto in productos:
        items = Items.query.join(ItemsPorProducto, ItemsPorProducto.item_idFK == Items.item_id)\
                            .filter(ItemsPorProducto.producto_idFK == producto.producto_id)\
                            .all()
        items_json = [{'id': item.item_id, 'descripcion': item.nombre, 'tipo': item.tipo} for item in items]
        productos_json.append({
            'id': producto.producto_id,
            'nombre': producto.nombre,
            'items': items_json
        })
    return jsonify(productos_json)

@routes_blueprint.route('/todos_los_productos')
def todos_los_productos():
    productos = Productos.query.all()
    productos_json = []
    for producto in productos:
        items = Items.query.join(ItemsPorProducto, ItemsPorProducto.item_idFK == Items.item_id)\
                            .filter(ItemsPorProducto.producto_idFK == producto.producto_id)\
                            .all()
        items_json = [{'id': item.item_id, 'descripcion': item.nombre, 'tipo': item.tipo} for item in items]
        productos_json.append({
            'id': producto.producto_id,
            'nombre': producto.nombre,
            'linea_id': producto.linea_idFK,  # Asegúrate de devolver también la línea asociada al producto
            'items': items_json
        })
    return jsonify(productos_json)

@routes_blueprint.route('/porcentajes/<int:producto_id>')
def get_porcentajes(producto_id):
    porcentaje = PorcentajesProducto.query.filter_by(id_producto=producto_id).first()
    if porcentaje:
        return jsonify({
            'administracion': porcentaje.administracion,
            'imprevistos': porcentaje.imprevistos,
            'utilidad': porcentaje.utilidad
        })
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404

# Ruta para traer items por producto
@routes_blueprint.route('/items_por_producto/<int:producto_id>')
def items_por_producto(producto_id):
    pagina = request.args.get('pagina', 1, type=int)
    items_por_pagina = 20  # Cambia esto a 10 según lo mencionado

    query = Items.query \
        .join(ItemsPorProducto, ItemsPorProducto.item_idFK == Items.item_id) \
        .outerjoin(ItemProveedores, (ItemProveedores.item_id == Items.item_id) & (ItemProveedores.tipo_proveedor == 1)) \
        .filter(ItemsPorProducto.producto_idFK == producto_id)

    # Contar el total de ítems y calcular el total de páginas
    total_items = query.count()
    total_paginas = (total_items // items_por_pagina) + (1 if total_items % items_por_pagina > 0 else 0)

    # Paginación
    items = query.paginate(page=pagina, per_page=items_por_pagina).items

    # Crear la respuesta JSON con los ítems encontrados
    items_json = [{
        'id': item.item_id,
        'descripcion': item.nombre,
        'categoria': item.categoria.CATEGORIA_NOMBRE,
        'unidad': item.unidad,
        'tipo': item.tipo,
        'precio': locale.format_string("%.2f", next((item_prov.precio for item_prov in item.itemproveedores if item_prov.tipo_proveedor == 1), 0), grouping=True)
    } for item in items]

    return jsonify({
        'items': items_json,
        'totalPaginas': total_paginas
    })

@routes_blueprint.route('/todos_los_items')
def todos_los_items():
    pagina = request.args.get('pagina', 1, type=int)  # Obtener la página actual
    busqueda = request.args.get('busqueda', '', type=str)  # Obtener el término de búsqueda
    items_por_pagina = 20  # Número de ítems por página

    # Crear la consulta base para la tabla Items
    query = Items.query

    # Filtrar por búsqueda si se proporciona
    if busqueda:
        query = query.filter(Items.nombre.ilike(f'%{busqueda}%'))  # Usar LIKE para búsqueda

    # Contar el total de ítems y calcular el total de páginas
    total_items = query.count()
    total_paginas = (total_items // items_por_pagina) + (1 if total_items % items_por_pagina > 0 else 0)

    # Paginación
    items = query.paginate(page=pagina, per_page=items_por_pagina).items

    # Crear la respuesta JSON con los ítems encontrados
    items_json = []
    for item in items:
        # Buscar el proveedor con tipo_proveedor = 1 para obtener el precio
        proveedor = next((prov for prov in item.itemproveedores if prov.tipo_proveedor == 1), None)
        item_precio = None
        
        if proveedor:
            item_precio = proveedor.precio  # Obtener el precio del proveedor

        # Agregar el ítem al JSON
        items_json.append({
            'id': item.item_id,
            'descripcion': item.nombre,
            'categoria': item.categoria.CATEGORIA_NOMBRE if item.categoria else None,  # Manejar relación
            'unidad': item.unidad,
            'tipo': item.tipo,
            'precio': locale.format_string("%.2f", item_precio, grouping=True) if item_precio else 'SIN PRECIO',
        })

    return jsonify({
        'items': items_json,
        'totalPaginas': total_paginas
    })

@routes_blueprint.route('/agregar_item_temporal', methods=['POST'])
def agregar_item_temporal():
    descripcion = request.json.get('descripcion')
    precio = request.json.get('precio')
    aprobado = request.json.get('aprobado')
    producto_id = request.json.get('producto_id')

    # Obtener el ID del usuario logueado de la sesión
    creado_por = session.get('user_id')

    if not creado_por:
        return jsonify({'error': 'Usuario no autenticado'}), 401

    nuevo_item = ItemTemporal(
        descripcion=descripcion,
        precio=precio,
        creado_por=creado_por,
        aprobado=aprobado
    )

    try:
        db.session.add(nuevo_item)
        db.session.commit()
        return jsonify({'success': True, 'item_id': nuevo_item.id}), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': 'Error al agregar el ítem temporal'}), 500
    
#Crud Cotizaciones

#ruta del formulario para crear cotizacion
@routes_blueprint.route('/crear_cotizacion', methods=['POST'])
def crear_cotizacion():
    data = request.json
    descripcion = data.get('descripcion')

    if not descripcion:
        return jsonify({'success': False, 'message': 'Descripción es requerida.'}), 400

    nueva_cotizacion = Cotizacion(descripcion=descripcion)
    db.session.add(nueva_cotizacion)
    db.session.commit()

    for producto_data in data['productos']:
        nuevo_producto = ProductoCotizado(
            ID_COTIZACION=nueva_cotizacion.ID_COTIZACION,
            descripcion=producto_data['descripcion'],
            alto=producto_data['alto'],
            ancho=producto_data['ancho'],
            fondo=producto_data['fondo']
        )
        db.session.add(nuevo_producto)
        db.session.commit()

        for item_data in producto_data['items']:
            nuevo_item = Items(
                producto_id=nuevo_producto.id,
                grupo=item_data['grupo'],
                descripcion=item_data['descripcion'],
                unidad=item_data['unidad'],
                precio=item_data['precio'],
                cantidad=item_data['cantidad'],
                total=item_data['total']
            )
            db.session.add(nuevo_item)

    db.session.commit()

    return jsonify({'success': True, 'message': 'Cotización creada exitosamente.'})



UPLOAD_FOLDER = './product_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def incrementar_version(ultima_version):
    if ultima_version:
        nueva_version = chr(ord(ultima_version.upper()) + 1)
        return nueva_version if nueva_version <= 'Z' else 'A'
    return 'A'

@routes_blueprint.route('/guardar-cotizacion', methods=['POST'])
def guardar_cotizacion():
    data = request.form
    negociacion = data.get('negociacion') or ''
    
    # Convertir la cadena de fecha y hora a un objeto datetime
    fecha_cotizacion = parser.parse(data['fechaCotizacion']).astimezone(timezone.utc)


    # Buscar cotizaciones existentes con el mismo número de negociación
    cotizaciones_existentes = Cotizacion.query.filter_by(negociacion=negociacion).order_by(Cotizacion.version.desc()).all()

    # Determinar la nueva versión
    if cotizaciones_existentes:
        ultima_version = cotizaciones_existentes[0].version
        nueva_version = incrementar_version(ultima_version)
    else:
        nueva_version = 'A'

    # Crear la nueva cotización
    nueva_cotizacion = Cotizacion(
        fecha_cotizacion=fecha_cotizacion,
        cliente_cotizacion=data['clienteCotizacion'],
        contacto_cotizacion=data['contactoCotizacion'],
        proyecto_cotizacion=data['proyectoCotizacion'],
        vendedor_cotizacion=data['vendedorCotizacion'],
        negociacion=negociacion,
        forma_de_pago_cotizacion=data['formaPago'],
        validez_cotizacion=data['validezCotizacion'],
        descuento_cotizacion=float(data.get('descuentoCotizacion', 0) or 0),
        iva_seleccionado=data['ivaSeleccionado'],
        version=nueva_version
    )
    db.session.add(nueva_cotizacion)
    db.session.flush()  # Para obtener el ID de la cotización

    # Convertir la cadena JSON de productos en una lista de diccionarios
    productos = json.loads(data.get('productos', '[]'))

    # Procesar los productos
    for producto_data in productos:
        print("Procesando producto:", producto_data)

        # Obtener las cantidades seleccionadas
        cantidades_seleccionadas = producto_data.get('cantidadesSeleccionadas', [])
        cantidades_str = ','.join(map(str, cantidades_seleccionadas))

        # Crear una nueva instancia para cada producto
        nuevo_producto_cotizado = ProductoCotizado(
            descripcion=producto_data['descripcion'],
            alto=producto_data['alto'],
            ancho=producto_data['ancho'],
            fondo=producto_data['fondo'],
            cantidades=cantidades_str,
            cotizacion_id=nueva_cotizacion.id_cotizacion,
            producto_id=producto_data['productoId'],
            producto_seleccionado_id=producto_data.get('productoSeleccionadoId')
        )
        
        db.session.add(nuevo_producto_cotizado)
        db.session.flush()  # Para obtener el ID del producto cotizado

        # Guardar las imágenes si existen
        image_key = f'imagenProducto-{producto_data["productoId"]}'
        if image_key in request.files:
            file = request.files[image_key]
            if file and allowed_file(file.filename):
                original_filename = secure_filename(file.filename)
                unique_filename = f"{producto_data['productoId']}_{uuid.uuid4().hex}_{original_filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)

                if os.path.exists(filepath):
                    print(f"Imagen guardada en: {filepath}")
                    nuevo_producto_cotizado.imagen_ruta = filepath  # Guarda la ruta completa
                else:
                    print("Error: el archivo no se guardó correctamente.")
            else:
                print(f"No se pudo cargar la imagen para el producto {producto_data['productoId']} o no es un formato permitido.")

        # Manejo de resúmenes de costos
        for resumen in producto_data.get('resúmenesCostos', []):
            resumen_de_costos = ResumenDeCostos(
                costo_directo=resumen['costoDirecto'],
                administracion=resumen['administracion'],
                imprevistos=resumen['imprevistos'],
                utilidad=resumen['utilidad'],
                oferta_antes_iva=resumen['ofertaAntesIva'],
                iva=resumen['iva'],
                valor_oferta=resumen['valorOferta'],
                producto_id=nuevo_producto_cotizado.id
            )
            db.session.add(resumen_de_costos)

        # Manejo de items cotizados
        items_data = producto_data.get('items', [])
        for item_data in items_data:
            if item_data['itemId'] < 1000000000000:  # Condición para asegurarse de que solo los items no temporales se procesen
                nuevo_item_cotizado = ItemCotizado(
                    producto_cotizado_id=nuevo_producto_cotizado.id,
                    item_id=item_data['itemId'],
                    cantidad=item_data['itemCantidad'],
                    total_item=item_data['itemTotal']
                )
                db.session.add(nuevo_item_cotizado)

        # Procesar items temporales si existen para este producto
        items_temporales = json.loads(data.get('itemsTemporales', '[]'))
        for item_temporal in items_temporales:
            # Asociar los items temporales solo con el producto actual
            if item_temporal.get('productoId') == producto_data['productoId']:  # Asegúrate de que pertenezca al producto correcto
                nuevo_item_temporal = ItemTemporal(
                    descripcion=item_temporal['descripcion'],
                    precio=item_temporal['total'],  # Cambia esto si necesitas almacenar el precio unitario
                    creado_por=data.get('vendedorCotizacion'),
                    producto_id=nuevo_producto_cotizado.id,  # Asociado al producto correcto
                    cantidad=item_temporal['cantidad'],
                    unidad=item_temporal['unidad'],
                    proveedor=item_temporal['proveedor']  # Agregar el proveedor aquí
                )
                db.session.add(nuevo_item_temporal)


    # Intentar guardar en la base de datos
    try:
        db.session.commit()
        print("Cotización guardada con éxito.")
    except Exception as e:
        db.session.rollback()
        print("Error al guardar la cotización:", e)

    return jsonify({'success': True})





@routes_blueprint.route('/guardar-cotizacion-editada', methods=['POST'])
def guardar_cotizacion_editada():
    data = request.json
    print(data)  # Para depuración

    negociacion = data.get('negociacion') or ''  # Obtener el número de negociación

    # Buscar la última cotización con la misma negociación y versión más alta
    ultima_cotizacion = Cotizacion.query.filter_by(negociacion=negociacion).order_by(Cotizacion.version.desc()).first()

    if ultima_cotizacion:
        # Incrementar la versión si existe una cotización previa
        nueva_version = incrementar_version(ultima_cotizacion.version)
    else:
        # Si no existe, comenzar con la versión 'a'
        nueva_version = 'A'

    # Crear la nueva cotización con la nueva versión
    nueva_cotizacion = Cotizacion(
        fecha_cotizacion=datetime.fromisoformat(data['fechaCotizacion']).astimezone(timezone.utc),
        cliente_cotizacion=data['clienteCotizacion'],
        contacto_cotizacion=data['contactoCotizacion'],
        proyecto_cotizacion=data['proyectoCotizacion'],
        vendedor_cotizacion=data['vendedorCotizacion'],
        negociacion=negociacion,
        forma_de_pago_cotizacion=data['formaPago'],
        validez_cotizacion=data['validezCotizacion'],
        descuento_cotizacion=data.get('descuentoCotizacion', 0),
        iva_seleccionado=data['ivaSeleccionado'],
        version=nueva_version
    )
    db.session.add(nueva_cotizacion)
    db.session.flush()  # Obtener el ID de la nueva cotización

    # Guardar productos cotizados
    for producto_data in data['productos']:
        cantidades_str = ','.join(map(str, producto_data['cantidadesSeleccionadas']))

        nuevo_producto_cotizado = ProductoCotizado(
            descripcion=producto_data['descripcion'],
            alto=producto_data['alto'],
            ancho=producto_data['ancho'],
            fondo=producto_data['fondo'],
            cantidades=cantidades_str,  # Guardar las cantidades como una cadena
            cotizacion_id=nueva_cotizacion.id_cotizacion,
            producto_id=producto_data['productoId'],
            producto_seleccionado_id=producto_data.get('productoSeleccionadoId')
        )
        db.session.add(nuevo_producto_cotizado)
        db.session.flush()  # Obtener el ID del producto cotizado

        # Guardar los resúmenes de costos asociados a cada producto
        for resumen in producto_data.get('resúmenesCostos', []):
            resumen_de_costos = ResumenDeCostos(
                costo_directo=resumen['costoDirecto'],
                administracion=resumen['administracion'],
                imprevistos=resumen['imprevistos'],
                utilidad=resumen['utilidad'],
                oferta_antes_iva=resumen['ofertaAntesIva'],
                iva=resumen['iva'],
                valor_oferta=resumen['valorOferta'],
                producto_id=nuevo_producto_cotizado.id
            )
            db.session.add(resumen_de_costos)

        # Guardar los items cotizados
        for item_data in producto_data['items']:
            nuevo_item_cotizado = ItemCotizado(
                producto_cotizado_id=nuevo_producto_cotizado.id,
                item_id=item_data['itemId'],
                cantidad=item_data['itemCantidad'],
                total_item=item_data['itemTotal']
            )
            db.session.add(nuevo_item_cotizado)

    # Confirmar los cambios en la base de datos
    db.session.commit()

    return jsonify({'success': True})



#Ruta para listar cotizaciones

@routes_blueprint.route('/listar_cotizaciones', methods=['GET', 'POST'])
@login_required
def listar_cotizaciones():
    search = request.args.get('search')
    
    if current_user.user_rol in [1, 3]:
        # Rol 1 o 3: Puede ver todas las cotizaciones
        if search:
            cotizaciones = Cotizacion.query.filter(
                Cotizacion.negociacion.ilike(f'%{search}%')
            ).order_by(Cotizacion.fecha_cotizacion.desc()).all()
        else:
            cotizaciones = Cotizacion.query.order_by(
                Cotizacion.fecha_cotizacion.desc()
            ).all()
    
    elif current_user.user_rol == 2:
        # Rol 2: Solo puede ver las cotizaciones asociadas a su propio usuario
        if search:
            cotizaciones = Cotizacion.query.filter(
                Cotizacion.negociacion.ilike(f'%{search}%'),
                Cotizacion.vendedor_cotizacion == current_user.user_id
            ).order_by(Cotizacion.fecha_cotizacion.desc()).all()
        else:
            cotizaciones = Cotizacion.query.filter(
                Cotizacion.vendedor_cotizacion == current_user.user_id
            ).order_by(Cotizacion.fecha_cotizacion.desc()).all()
    
    else:
        # Manejar otros roles o casos de error si es necesario
        cotizaciones = []

    return render_template('listar_cotizaciones.html', cotizaciones=cotizaciones, user_rol=current_user.user_rol)



#ruta para editar la cotizacion

@routes_blueprint.route('/editar_cotizacion/<int:cotizacion_id>', methods=['GET'])
def editar_cotizacion(cotizacion_id):
    user_rol = current_user.user_rol if current_user.is_authenticated else None
    
    # Consulta la cotización por ID
    cotizacion = Cotizacion.query.filter_by(id_cotizacion=cotizacion_id).first()
    
    if not cotizacion:
        return "Cotización no encontrada", 404

    # Formatea la fecha en el formato correcto
    cotizacion_fecha = cotizacion.fecha_cotizacion.strftime('%Y-%m-%d') if cotizacion.fecha_cotizacion else None

    # Consulta los productos cotizados asociados a la cotización
    productos_cotizados = ProductoCotizado.query.filter_by(cotizacion_id=cotizacion_id).all()
    
    productos_data = []
    for producto_cotizado in productos_cotizados:
        producto_data = producto_cotizado.to_dict()
        
        # Consulta el nombre del producto usando producto_seleccionado_id
        producto = Productos.query.get(producto_cotizado.producto_seleccionado_id)
        producto_data['producto_nombre'] = producto.nombre if producto else 'Nombre no disponible'
        
        productos_data.append(producto_data)

    # Consulta todas las líneas
    lineas = Lineas.query.all()  # Carga todas las líneas

    # Consulta los ítems cotizados asociados a cada producto cotizado y completa la información desde la tabla Items
    items_cotizados = []
    for item_cotizado in ItemCotizado.query.join(ProductoCotizado).filter(ProductoCotizado.cotizacion_id == cotizacion_id).all():
        item = item_cotizado.to_dict()

        # Consultar la relación con la tabla Items
        related_item = Items.query.get(item_cotizado.item_id)

        if related_item:
            item['grupo'] = related_item.categoria.CATEGORIA_NOMBRE if related_item.categoria else 'N/A'
            item['descripcion'] = related_item.nombre
            item['unidad'] = related_item.unidad  # Agregamos el campo 'unidad'
            item['tipo'] = related_item.tipo  # Asegurarnos de enviar el campo 'tipo' desde el backend

            # Consultar el precio desde la tabla ItemProveedores
            precio_proveedor = ItemProveedores.query.filter_by(item_id=item_cotizado.item_id, tipo_proveedor=1).first()
            if precio_proveedor:
                item['precio_unitario'] = format(float(precio_proveedor.precio), ',.0f')
            else:
                item['precio_unitario'] = '0.00'
        else:
            item['grupo'] = 'N/A'
            item['descripcion'] = 'N/A'
            item['unidad'] = 'N/A'  # Agregamos 'N/A' para los casos sin unidad
            item['tipo'] = 'N/A'  # Si no hay tipo disponible, asignamos 'N/A'
            item['precio_unitario'] = '0.00'

        # Formatear el total del ítem
        item['total_item'] = format(float(item['total_item']), ',.0f')
        
        # Agregamos este ítem a la lista de ítems cotizados
        items_cotizados.append(item)
    
    # Consulta los resúmenes de costos asociados a los productos cotizados
    resumen_costos = []
    for producto in productos_cotizados:
        resumen = ResumenDeCostos.query.filter_by(producto_id=producto.id).first()
        if resumen:
            resumen_dict = resumen.to_dict()
            # Formatear los valores del resumen de costos
            resumen_dict['costo_directo'] = format(resumen.costo_directo, ',.0f')
            resumen_dict['administracion'] = format(resumen.administracion, ',.0f')
            resumen_dict['imprevistos'] = format(resumen.imprevistos, ',.0f')
            resumen_dict['utilidad'] = format(resumen.utilidad, ',.0f')
            resumen_dict['oferta_antes_iva'] = format(resumen.oferta_antes_iva, ',.0f')
            resumen_dict['iva'] = format(resumen.iva, ',.0f')
            resumen_dict['valor_oferta'] = format(resumen.valor_oferta, ',.0f')
            resumen_costos.append(resumen_dict)

    # Consulta la lista de vendedores con user_rol 1 o 2
    vendedores = Users.query.filter(Users.user_rol.in_([1, 2])).all()

    return render_template(
        'editar_cotizacion.html',
        cotizacion=cotizacion.to_dict(),
        fecha_cotizacion=cotizacion_fecha,
        productos_cotizados=productos_data,
        items_cotizados=items_cotizados,  # Ahora los ítems tienen el campo 'tipo'
        resumen_costos=resumen_costos,
        vendedores=vendedores,
        user_rol=user_rol,
        lineas=lineas
    )



# Definir las dimensiones de las imágenes
encabezado_width = 612.07 #21,59
encabezado_height = 121.90 #4,3
footer_width = 612.07 
footer_height = 195.615 #6.9
footer_margin = 0
DEFAULT_IMAGE_PATH = "product_images/logo.png"



def format_precio(precio):
    if precio is None:
        return "$ 0.00"
    try:
        # Asegurarse de que el locale esté configurado correctamente
        locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
        
        # Formatear el precio utilizando el locale
        precio = float(precio)
        formatted = locale.currency(precio, grouping=True)
        
        return formatted  # Esto ya te devuelve el formato correcto "$ 1.234,56"
    
    except (ValueError, TypeError):
        return "$ 0.00"  # Retornar "$ 0.00" si hay un error

@routes_blueprint.route('/generar-reporte/<int:cotizacion_id>', methods=['GET'])
def generar_reporte(cotizacion_id):
    locale.setlocale(locale.LC_ALL, '')

    cotizacion = Cotizacion.query.get(cotizacion_id)
    if not cotizacion:
        return "Cotización no encontrada", 404

    buffer = BytesIO()
    ancho = 21.59 * cm
    alto = 33 * cm
    doc = SimpleDocTemplate(buffer, pagesize=(ancho, alto))
    width, height = legal

    elements = []

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    heading_style = ParagraphStyle(
        'SmallHeading',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor("#ffffff")
    )

    # Definir estilo del contenido en negro
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.black  # El contenido será negro
    )

    # Color de fondo para los títulos
    title_background = colors.HexColor("#0C086D")

    # Ajustar márgenes con Spacer para mover la tabla a la derecha
    elements.append(Spacer(1 * inch, 4))  # 1 pulgada de espaciado a la derecha

    # Estilos para títulos y contenido
    heading_style = ParagraphStyle(
        'Heading',
        fontSize=8,  # Tamaño de fuente para títulos
        alignment=TA_CENTER,  # Alineación centrada para los títulos
        textColor=colors.white
    )

    content_style = ParagraphStyle(
        'Content',
        fontSize=6,  # Tamaño pequeño para el contenido
        wordWrap='CJK',  # Ajuste de texto a la celda
        alignment=TA_LEFT  # Alineación izquierda
    )

    # Datos de la tabla
    data = [
        [
            Paragraph("Cliente", heading_style),
            Paragraph(cotizacion.cliente_cotizacion, content_style),
            Paragraph("Proyecto", heading_style),
            Paragraph(cotizacion.proyecto_cotizacion, content_style), 
            Paragraph("Contacto", heading_style),
            Paragraph(cotizacion.contacto_cotizacion, content_style)
        ]
    ]

    # Ajuste de ancho de columnas
    col_widths = [1 * inch, 1.6 * inch, 1 * inch, 1.4 * inch, 1 * inch, 1.4 * inch]

    # Crear la tabla
    table = Table(data, colWidths=col_widths)

    # Estilos de la tabla
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación centrada para todo el contenido
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 0), (0, 0), title_background),
        ('BACKGROUND', (2, 0), (2, 0), title_background),
        ('BACKGROUND', (4, 0), (4, 0), title_background),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('TEXTCOLOR', (2, 0), (2, 0), colors.white),
        ('TEXTCOLOR', (4, 0), (4, 0), colors.white),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.black),
        ('TEXTCOLOR', (3, 0), (3, 0), colors.black),
        ('TEXTCOLOR', (5, 0), (5, 0), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    # Agregar tabla a la lista de elementos
    elements.append(table)

    # Agregar un espacio entre la tabla de información del cliente y la tabla de productos
    elements.append(Spacer(1 * inch, 0.2 * inch))  # 0.5 pulgadas de espacio vertical

    # Ajuste de las tablas de productos en vertical
    header_data = [
        ["ITEM", "Imagen", "Producto", "Materiales / Servicios", "Cantidad", "Valor Unidad", "Valor Total"]
    ]

    # Anchos de las columnas ajustados
    header_table = Table(header_data, colWidths=[0.3*inch, 1.3*inch, 1.3*inch, 2.3*inch, 0.6*inch, 0.9*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0C086D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    item_counter = 1
    subtotal = 0
    multiple_quantities = False

    descuento_porcentaje = cotizacion.descuento_cotizacion / 100 if cotizacion.descuento_cotizacion else 0

    # Agregar un print para mostrar cuántos productos se encontraron
    num_productos = len(cotizacion.productos_cotizados)
    print(f"Número de productos encontrados asociados a la cotización: {num_productos}")

    summary_data = []

    for producto_cotizado in cotizacion.productos_cotizados:
        producto = Productos.query.get(producto_cotizado.producto_seleccionado_id)
        cantidades = producto_cotizado.cantidades.split(',')
        resúmenes_costos = ResumenDeCostos.query.filter_by(producto_id=producto_cotizado.id).all()

        if len(cantidades) > 1:
            multiple_quantities = True

        valores_totales = []
        valores_unitarios = []

        # Reemplazar el formateo original
        for i, cantidad in enumerate(cantidades):
            if i < len(resúmenes_costos):
                valor_total_inicial = resúmenes_costos[i].oferta_antes_iva

                if descuento_porcentaje > 0:
                    valor_total_incrementado = valor_total_inicial / (1 - descuento_porcentaje)
                else:
                    valor_total_incrementado = valor_total_inicial

                subtotal += valor_total_incrementado
                valor_unitario = valor_total_incrementado / float(cantidad) if float(cantidad) > 0 else 0

                # Usar la nueva función format_precio para formatear los valores
                valores_totales.append(format_precio(valor_total_incrementado))
                valores_unitarios.append(format_precio(valor_unitario))
            else:
                valores_totales.append("$ 0.00")
                valores_unitarios.append("$ 0.00")

            # Definir un estilo de párrafo más pequeño para la tabla interna
            small_style = ParagraphStyle(
                'SmallStyle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=7.5,  # Ajusta el tamaño de fuente aquí
                textColor=colors.black
            )

            # Creamos una lista de filas para las cantidades, valores unitarios y valores totales
            cantidades_data = [[Paragraph(cantidades[i], small_style), Paragraph(valores_unitarios[i], small_style), Paragraph(valores_totales[i], small_style)] for i in range(len(cantidades))]

            # Creamos una tabla interna solo para esas columnas
            internal_table = Table(cantidades_data, colWidths=[0.6*inch, 0.9*inch, 0.9*inch])
            internal_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 7.5),  # Ajusta el tamaño de la fuente aquí
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            # Obtener items_cotizados

            items_cotizados = producto_cotizado.items

            # Filtrar los items_cotizados excluyendo aquellos con item_id entre 1845 y 1854
            items_filtrados = [item_cotizado for item_cotizado in items_cotizados if not (1845 <= item_cotizado.item_id <= 1854)]

            # Obtener items_temporales si existen
            items_temporales = ItemTemporal.query.filter_by(producto_id=producto_cotizado.id).all()

            # Combinar descripciones para los items filtrados
            item_names = [Items.query.get(item_cotizado.item_id).nombre for item_cotizado in items_filtrados if Items.query.get(item_cotizado.item_id)]
            items_description = "//".join(item_names) if item_names else "No se especifican items."

            # Agregar items_temporales a la descripción
            if items_temporales:
                temporal_descriptions = [item.descripcion for item in items_temporales]
                items_description += "//" + "//".join(temporal_descriptions)

            # Cambiar el tamaño de la fuente para la descripción de los materiales
            materials_style = ParagraphStyle(
                'MaterialsStyle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=7,  # Ajusta el tamaño de fuente aquí
                textColor=colors.black
            )

            items_paragraph = Paragraph(items_description, materials_style) 

            producto_descripcion = Paragraph(producto_cotizado.descripcion)

            product_name_paragraph = Paragraph(producto.nombre)

            # Definir la ruta de la imagen desde la base de datos
            imagen_ruta = producto_cotizado.imagen_ruta  # Asegúrate que este campo está correctamente asignado

            # Crear un objeto Image
            if imagen_ruta and os.path.exists(imagen_ruta):  # Verificar que la imagen existe
                image = Image(imagen_ruta, width=1.1*inch, height=1.2*inch)  # Ajustar el tamaño según sea necesario
            else:
                image = Image(DEFAULT_IMAGE_PATH, width=1.1*inch, height=0.5*inch)

            # Modificamos la data de la tabla principal
            # Definir estilos para los encabezados y el contenido
            heading_style = ParagraphStyle(
                'HeadingStyle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=8,
                textColor=colors.HexColor("#0C086D")  # Puedes cambiar el color si lo deseas
            )

            # Crear un párrafo que combina los elementos con títulos
            product_info = Paragraph(
                f"<b>Descripción:</b> {producto_cotizado.descripcion}<br/><br/>"  # Título para la descripción
                f"<b>Medidas:</b> {producto_cotizado.alto} x {producto_cotizado.ancho} x {producto_cotizado.fondo}",  # Título para las medidas
                normal_style
            )

            # Crear una tabla que actúe como un contenedor con espacio vacío a la izquierda
            wrapped_internal_table = Table(
                [[Spacer(width=10, height=0), internal_table]],  # La tabla interna movida hacia la derecha
                colWidths=[0*inch, None]  # El primer ancho es el "margen", ajústalo a lo que necesites
            )

            # Modificamos la data de la tabla principal
            data = [
                str(item_counter),
                image,  # Imagen del producto
                product_info,  # Descripción y medidas del producto (sin el nombre)
                items_paragraph,
                "",  # Columna vacía para la columna de materiales
                "",  # Columna vacía para los valores unitarios
                internal_table   # Columna para los valores totales
            ]

            product_table = Table([data], colWidths=[0.3*inch, 1.3*inch, 1.3*inch, 2.3*inch, 0.6*inch, 0.9*inch])
            product_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (6, 0), (-1, 0), 'RIGHT'),
                ('RIGHTPADDING', (7, 0), (10, 0), 0),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 6),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # Aplicar padding solo a la columna de la tabla interna
                ('LEFTPADDING', (6, 0), (6, 0), 2),  # Ajusta este valor para mover la tabla un poco a la derecha
                ('RIGHTPADDING', (6, 0), (6, 0), 0),  # Asegurarnos que no haya relleno a la derecha
            ]))

            elements.append(product_table)
            elements.append(Spacer(1, 1))#

            item_counter += 1

    # Calcular IVA y Total
    if multiple_quantities:
        elements.append(Paragraph("Estos valores no incluyen IVA", normal_style))
    else:
        if cotizacion.iva_seleccionado.lower() == "no":
            iva = 0
            total = subtotal
            elements.append(Paragraph("Estos valores no incluyen IVA", normal_style))
            summary_data = [
                ["Subtotal", locale.format_string("$ %d", subtotal, grouping=True)],
                ["Total", locale.format_string("$ %d", total, grouping=True)]
            ]
            col_widths = [0.9*inch, 0.9*inch]  # Anchos normales sin descuento
        else:
            if descuento_porcentaje > 0:
                valor_descuento = subtotal * descuento_porcentaje
                subtotal_con_descuento = subtotal - valor_descuento
                iva = subtotal_con_descuento * 0.19
                total = subtotal_con_descuento + iva

                valor_descuento_formateado = locale.format_string("$ %d", valor_descuento, grouping=True)
                subtotal_con_descuento_formateado = locale.format_string("$ %d", subtotal_con_descuento, grouping=True)
                iva_formateado = locale.format_string("$ %d", iva, grouping=True)
                total_formateado = locale.format_string("$ %d", total, grouping=True)

                summary_data = [
                    ["Subtotal antes de descuento", locale.format_string("$ %d", subtotal, grouping=True)],
                    [f"Descuento ({cotizacion.descuento_cotizacion}%)", f"-{valor_descuento_formateado}"],
                    ["Subtotal con descuento", subtotal_con_descuento_formateado],
                    ["IVA (19%)", iva_formateado],
                    ["Total", total_formateado]
                ]

                # Aumentar el ancho de las columnas para acomodar el texto del descuento
                col_widths = [1.6*inch, 0.9*inch]  # Anchos más grandes cuando hay descuento
            else:
                iva = subtotal * 0.19
                total = subtotal + iva

                iva_formateado = locale.format_string("$ %d", iva, grouping=True)
                total_formateado = locale.format_string("$ %d", total, grouping=True)
                subtotal_formateado = locale.format_string("$ %d", subtotal, grouping=True)

                summary_data = [
                    ["Subtotal", subtotal_formateado],
                    ["IVA (19%)", iva_formateado],
                    ["Total", total_formateado]
                ]

                col_widths = [0.9*inch, 0.9*inch]  # Anchos normales sin descuento

    # Asegúrate de que summary_data tenga datos
    if not summary_data:
        summary_data = None 

    condiciones_comerciales = Paragraph(
        f"<b>Condiciones Comerciales:</b><br/><br/>"
        f"<b>Forma de Pago:</b> {cotizacion.forma_de_pago_cotizacion}<br/><br/>"
        f"<b>Validez de la Cotización:</b> {cotizacion.validez_cotizacion} días",
        normal_style
    )

    # Solo crea la tabla si summary_data tiene datos
    if summary_data:
        # Usa los colWidths definidos dinámicamente
        summary_table = Table(summary_data, colWidths=col_widths)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 10), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))

        # Crea la tabla con condiciones comerciales y resumen
        summary_and_conditions = Table([[condiciones_comerciales, summary_table]], colWidths=[4.2*inch, 2.6*inch])
    else:
        # Solo muestra condiciones comerciales si no hay datos de resumen
        summary_and_conditions = Table([[condiciones_comerciales]], colWidths=[4.2*inch])

    # Añadir un Spacer para mover la tabla hacia la derecha
    wrapped_summary_table = Table([[Spacer(5, 0), summary_and_conditions]], colWidths=[None, None])

    wrapped_summary_table.hAlign = 'RIGHT'  # Esta propiedad mueve toda la tabla hacia la derecha

    elements.append(wrapped_summary_table)

    separator_line = HRFlowable(width="110%", thickness=1, lineCap='round', color=colors.black, spaceBefore=10, spaceAfter=10)

    agradecimiento = Paragraph(
        "Gracias por la confianza depositada en nuestra empresa, quedamos a la espera de sus comentarios. Cordialmente",
        normal_style
    )

    # Mapeo de los vendedores con sus respectivas imágenes de firma
    firmas = {
        130: "FIRMA_FELDMAN_RODRIGUEZ.jpg",
        131: "FIRMA_PEDRO_ALVAREZ.jpg",
        132: "FIRMA_ADRIANA_HUESO.jpg",
        133: "FIRMA_LUIS_CORREA.jpg",
        134: "FIRMA_ARMANDO_CISNEROS.jpg"
    }

    # Obtener el ID del vendedor de la cotización
    vendedor_id = cotizacion.vendedor_cotizacion

    if vendedor_id in firmas:
        firma_path = f"static/images/{firmas[vendedor_id]}"
        firma_vendedor = Image(firma_path, width=6*inch, height=1*inch)
    else:
        firma_texto = Paragraph("Firma inexistente", normal_style)
        firma_vendedor = firma_texto

    elements.append(separator_line)
    elements.append(Spacer(1, 12))
    elements.append(agradecimiento)
    elements.append(Spacer(1, 12))
    elements.append(firma_vendedor)

    def add_header_footer(canvas, doc):
        canvas.saveState()

        # Insertar el encabezado y pie de página
        canvas.drawImage("static/images/encabezado_cotizacion.png",0, 815, height=encabezado_height, width=width,  mask='auto')
        canvas.drawImage("static/images/footer_cotizacion.png", 0, 0, width=footer_width, height=footer_height, mask='auto')

        # Posicionar la negociación en coordenadas específicas
        textobject = canvas.beginText(502, 905)  # 
        textobject.setFont("Helvetica", 10)
        textobject.textLine(cotizacion.negociacion)  # Colocar el texto de la negociación
        canvas.drawText(textobject)

        # Posicionar la fecha en coordenadas específicas
        fecha_cotizacion = cotizacion.fecha_cotizacion.strftime("%d/%m/%Y")  # Convertir a formato dd/mm/yyyy
        canvas.drawString(505, 864, f"{fecha_cotizacion}")  # Cambia las coordenadas (400, 750) por las deseadas


        canvas.restoreState()

    # Crear el documento con los elementos y agregar encabezado/pie de página
    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)

    # Devolver el archivo PDF
    return send_file(buffer, as_attachment=True, download_name=f"Cotizacion - N {cotizacion.negociacion}.{cotizacion.proyecto_cotizacion}-{cotizacion.cliente_cotizacion}.pdf", mimetype='application/pdf')
# < ----------------------------------------------------------  Ruta para generar OP ---------------------------------------------------------------------------------------->

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from flask import send_file
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

@routes_blueprint.route('/generar-op/<int:cotizacion_id>', methods=['GET'])
def generar_op(cotizacion_id):
    # Buscar la cotización por ID
    cotizacion = Cotizacion.query.get(cotizacion_id)

    if not cotizacion:
        return "Cotización no encontrada", 404

    # Buscar el vendedor
    vendedor = Users.query.get(cotizacion.vendedor_cotizacion)
    if vendedor:
        vendedor_nombre = f"{vendedor.user_name} {vendedor.user_last_name}"
    else:
        vendedor_nombre = "Desconocido"    

    buffer = BytesIO()
    ancho = 21.59 * cm
    alto = 33 * cm
    doc = SimpleDocTemplate(buffer, pagesize=(ancho, alto))
    width, height = legal

    # Crear el contenido del documento
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    normal_style.fontSize = 9  # Cambiar a 7 para el texto normal

    heading_style = styles['Heading1']
    heading_style.fontSize = 8  # Cambiar a 8 para el título

        # Definir estilo del contenido en negro
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.black  # El contenido será negro
    )

    title_background = colors.HexColor("#00A859")

    elements.append(Spacer(1 * inch, 7))  # 1 pulgada de espaciado a la derecha



    # Datos de la OP en una tabla horizontal
    data = [
        [
            Paragraph("Cliente", heading_style),
            Paragraph(cotizacion.cliente_cotizacion, content_style),
            Paragraph("Proyecto", heading_style),
            Paragraph(cotizacion.proyecto_cotizacion, content_style), 
            Paragraph("Vendedor", heading_style),
            Paragraph(vendedor_nombre, content_style)
        ]
    ]

    # Ajustar las alturas de las filas
    row_heights = [0.3 * inch]  # Aumentar la altura de la fila

    # Crear la tabla y establecer las alturas de las filas
    table = Table(data, colWidths=[1 * inch, 1.6 * inch, 1 * inch, 1.4 * inch, 1 * inch, 1.2 * inch], rowHeights=row_heights)

    # Ajuste de estilo de la tabla
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Centrar horizontalmente todos los encabezados
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),  # Centrar verticalmente todos los encabezados
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 5),  # Tamaño de fuente más pequeño para mayor compresión

        # Colores de fondo y texto
        ('BACKGROUND', (0, 0), (0, 0), title_background),
        ('BACKGROUND', (2, 0), (2, 0), title_background),
        ('BACKGROUND', (4, 0), (4, 0), title_background),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),  # Cliente
        ('TEXTCOLOR', (2, 0), (2, 0), colors.white),  # Proyecto
        ('TEXTCOLOR', (4, 0), (4, 0), colors.white),  # Vendedor
        ('TEXTCOLOR', (1, 0), (1, 0), colors.black),  # Contenido Cliente
        ('TEXTCOLOR', (3, 0), (3, 0), colors.black),  # Contenido Proyecto
        ('TEXTCOLOR', (5, 0), (5, 0), colors.black),  # Contenido Vendedor

        # Ajustar padding específico para los encabezados y contenido
        ('PADDING', (0, 0), (-1, -1), 30),        # Sin padding en general
        ('TOPPADDING', (0, 0), (0, 0), 10),      # Aumentar padding superior para "Cliente"
        ('BOTTOMPADDING', (0, 0), (0, 0), 0),    # Reducir padding inferior para "Cliente"

        ('TOPPADDING', (2, 0), (2, 0), 10),      # Aumentar padding superior para "Proyecto"
        ('BOTTOMPADDING', (2, 0), (2, 0), 0),    # Reducir padding inferior para "Proyecto"
        
        ('TOPPADDING', (4, 0), (4, 0), 10),      # Aumentar padding superior para "Contacto"
        ('BOTTOMPADDING', (4, 0), (4, 0), 0),    # Reducir padding inferior para "Contacto"

        # Mantener el padding original para el contenido
        ('TOPPADDING', (1, 0), (1, 0), 5),        # Espacio superior para contenido (Cliente)
        ('BOTTOMPADDING', (1, 0), (1, 0), 5),     # Espacio inferior para contenido (Cliente)

        ('TOPPADDING', (3, 0), (3, 0), 5),        # Espacio superior para contenido (Proyecto)
        ('BOTTOMPADDING', (3, 0), (3, 0), 5),     # Espacio inferior para contenido (Proyecto)

        ('TOPPADDING', (5, 0), (5, 0), 5),        # Espacio superior para contenido (Contacto)
        ('BOTTOMPADDING', (5, 0), (5, 0), 5),     # Espacio inferior para contenido (Contacto)

        # Añadir borde delgado (opcional, para visualizar mejor)
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    # Agregar tabla a la lista de elementos
    elements.append(table)


    elements.append(Spacer(1, 12))

    # Cabecera de la tabla de productos
    header_data = [
        ["ITEM", "Descripción", "Medidas", "Cantidad"]
    ]

    header_table = Table(header_data, colWidths=[0.5*inch, 4*inch, 2.5*inch, 1*inch])  # 8inch
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#00A859'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, '#000000'),
        ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),
    ]))
    elements.append(header_table)

    # Detalle de Productos
    item_counter = 1
    for producto_cotizado in cotizacion.productos_cotizados:
        producto = Productos.query.get(producto_cotizado.producto_id)

        # Información del Producto
        producto_descripcion = Paragraph(producto_cotizado.descripcion, normal_style)
        medidas = f"{producto_cotizado.alto} x {producto_cotizado.ancho} x {producto_cotizado.fondo}"

        # Crear la fila del producto
        data = [
            str(item_counter),  # ITEM
            producto_descripcion,  # Descripción
            medidas,  # Medidas
            producto_cotizado.cantidades
        ]

        product_table = Table([data], colWidths=[0.5*inch, 4*inch, 2.5*inch, 1*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#e0e0e0'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOX', (0, 0), (-1, -1), 0.5, '#000000'),
            ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(product_table)
        elements.append(Spacer(1, 6))  # Espacio para separar productos

        # Crear tabla de materiales
        items_data = [
            ["Material", "Unidad", "Cantidad"]
        ]



        items = producto_cotizado.items
        for item_cotizado in items:
            item_info = Items.query.get(item_cotizado.item_id)
            if item_info:

                items_data.append([item_info.nombre, item_info.unidad, item_cotizado.cantidad])

        # Obtener items_temporales y verificarlos
        items_temporales = ItemTemporal.query.filter_by(producto_id=producto_cotizado.id).all()
        for item_temporal in items_temporales:

            items_data.append([item_temporal.descripcion, item_temporal.unidad, item_temporal.cantidad])



        # Crear la tabla de items solo si hay datos
        if len(items_data) > 1:  # Si hay más de una fila (la primera fila es el encabezado)
            items_table = Table(items_data, colWidths=[4*inch, 3*inch, 1*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), '#00A859'),
                ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOX', (0, 0), (-1, -1), 0.5, '#000000'),
                ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(items_table)
            elements.append(Spacer(1, 12))  # Espacio después de la tabla de materiales

        item_counter += 1

    # Añadir imagen de encabezado y pie de página
    def add_header_footer(canvas, doc):
        canvas.saveState()

        # Insertar el encabezado y pie de página
        canvas.drawImage("static/images/encabezado_op.png",0, 815, height=encabezado_height, width=width,  mask='auto')
        canvas.drawImage("static/images/footer_cotizacion.png", 0, 0, width=footer_width, height=footer_height, mask='auto')

        # Posicionar la negociación en coordenadas específicas
        textobject = canvas.beginText(500, 905)  # 
        textobject.setFont("Helvetica", 12)
        textobject.textLine(cotizacion.negociacion)  # Colocar el texto de la negociación
        canvas.drawText(textobject)

        # Posicionar la fecha en coordenadas específicas
        fecha_cotizacion = cotizacion.fecha_cotizacion.strftime("%d/%m/%Y")  # Convertir a formato dd/mm/yyyy
        canvas.drawString(503, 863, f"{fecha_cotizacion}")  # Cambia las coordenadas (400, 750) por las deseadas


        canvas.restoreState()

    # Crear el documento con los elementos y agregar encabezado/pie de página
    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"OP - N {cotizacion.negociacion}.{cotizacion.proyecto_cotizacion}-{cotizacion.cliente_cotizacion}.pdf", mimetype='application/pdf')



# <-------------------------------------------------------- Ruta para generar Requisición ------------------------------------------------------------------------------------------------->

# Función para formatear números
def formatear_numero(numero):
    """Función para formatear números con punto como separador de miles y coma como separador decimal."""
    return "{:,.2f}".format(numero).replace(',', 'X').replace('.', ',').replace('X', '.')

@routes_blueprint.route('/generar-requisicion/<int:cotizacion_id>', methods=['GET'])
def generar_requisicion(cotizacion_id):
    # Buscar la cotización por ID
    cotizacion = Cotizacion.query.get(cotizacion_id)

    if not cotizacion:
        return "Cotización no encontrada", 404

    # Buscar el vendedor
    vendedor = Users.query.get(cotizacion.vendedor_cotizacion)
    if vendedor:
        vendedor_nombre = f"{vendedor.user_name} {vendedor.user_last_name}"
    else:
        vendedor_nombre = "Desconocido"

    buffer = BytesIO()
    ancho = 21.59 * cm
    alto = 33 * cm
    doc = SimpleDocTemplate(buffer, pagesize=(ancho, alto))
    width, height = legal

    # Crear el contenido del documento
    elements = []

    # Estilos

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    heading_style = styles['Heading1']

    # Crear estilo para los encabezados de la tabla (Cliente, Proyecto, Vendedor)
    heading_white_style = ParagraphStyle(
        'HeadingWhiteStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=10,  # Tamaño de fuente más pequeño
        textColor=colors.white,  # Texto en color blanco
        alignment=1  # Centrar el texto
    )

    # Definir estilo del contenido en negro
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        textColor=colors.black  # El contenido será negro
    )

    # Color de fondo de los títulos
    title_background = colors.HexColor("#E09834")
    elements.append(Spacer(1, 12))

    # Datos de la OP en una tabla horizontal
    data = [
        [
            Paragraph("Cliente", heading_white_style),  # Aplicar estilo blanco
            Paragraph(cotizacion.cliente_cotizacion, content_style),
            Paragraph("Proyecto", heading_white_style),  # Aplicar estilo blanco
            Paragraph(cotizacion.proyecto_cotizacion, content_style),
            Paragraph("Vendedor", heading_white_style),  # Aplicar estilo blanco
            Paragraph(vendedor_nombre, content_style)
        ]
    ]

    # Ajustar las alturas de las filas
    row_heights = [0.3 * inch]  # Aumentar la altura de la fila

    # Crear la tabla y establecer las alturas de las filas
    table = Table(data, colWidths=[1 * inch, 1.6 * inch, 1 * inch, 1.4 * inch, 1 * inch, 1.2 * inch], rowHeights=row_heights)

    # Ajuste de estilo de la tabla
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Centrar horizontalmente todos los encabezados
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),  # Centrar verticalmente todos los encabezados
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 5),  # Tamaño de fuente más pequeño para mayor compresión

        # Colores de fondo y texto
        ('BACKGROUND', (0, 0), (0, 0), title_background),
        ('BACKGROUND', (2, 0), (2, 0), title_background),
        ('BACKGROUND', (4, 0), (4, 0), title_background),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),  # Cliente
        ('TEXTCOLOR', (2, 0), (2, 0), colors.white),  # Proyecto
        ('TEXTCOLOR', (4, 0), (4, 0), colors.white),  # Vendedor
        ('TEXTCOLOR', (1, 0), (1, 0), colors.black),  # Contenido Cliente
        ('TEXTCOLOR', (3, 0), (3, 0), colors.black),  # Contenido Proyecto
        ('TEXTCOLOR', (5, 0), (5, 0), colors.black),  # Contenido Vendedor

        # Ajustar padding específico para los encabezados y contenido
        ('PADDING', (0, 0), (-1, -1), 30),        # Sin padding en general
        ('TOPPADDING', (0, 0), (0, 0), 10),      # Aumentar padding superior para "Cliente"
        ('BOTTOMPADDING', (0, 0), (0, 0), 0),    # Reducir padding inferior para "Cliente"

        ('TOPPADDING', (2, 0), (2, 0), 10),      # Aumentar padding superior para "Proyecto"
        ('BOTTOMPADDING', (2, 0), (2, 0), 0),    # Reducir padding inferior para "Proyecto"
        
        ('TOPPADDING', (4, 0), (4, 0), 10),      # Aumentar padding superior para "Contacto"
        ('BOTTOMPADDING', (4, 0), (4, 0), 0),    # Reducir padding inferior para "Contacto"

        # Mantener el padding original para el contenido
        ('TOPPADDING', (1, 0), (1, 0), 5),        # Espacio superior para contenido (Cliente)
        ('BOTTOMPADDING', (1, 0), (1, 0), 5),     # Espacio inferior para contenido (Cliente)

        ('TOPPADDING', (3, 0), (3, 0), 5),        # Espacio superior para contenido (Proyecto)
        ('BOTTOMPADDING', (3, 0), (3, 0), 5),     # Espacio inferior para contenido (Proyecto)

        ('TOPPADDING', (5, 0), (5, 0), 5),        # Espacio superior para contenido (Contacto)
        ('BOTTOMPADDING', (5, 0), (5, 0), 5),     # Espacio inferior para contenido (Contacto)

        # Añadir borde delgado (opcional, para visualizar mejor)
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    # Agregar tabla a la lista de elementos
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Cabecera de la tabla de productos
    header_data = [
        ["ITEM", "Descripción", "Cantidad"]
    ]

    header_table = Table(header_data, colWidths=[0.5*inch, 3.5*inch, 1*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#E09834'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOX', (0, 0), (-1, -1), 1, '#000000'),
        ('GRID', (0, 0), (-1, -1), 1, '#000000'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    # Detalle de Productos
    item_counter = 1
    total_precio_total = 0  # Variable para acumular el total

    for producto_cotizado in cotizacion.productos_cotizados:
        producto = Productos.query.get(producto_cotizado.producto_id)

        # Información del Producto
        producto_descripcion = Paragraph(producto_cotizado.descripcion, normal_style)

        # Crear la fila del producto
        data = [
            str(item_counter),  # ITEM
            producto_descripcion,  # Descripción
            producto_cotizado.cantidades  # Cantidad del producto
        ]

        product_table = Table([data], colWidths=[0.5*inch, 3.5*inch, 1*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#c0c0c0'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, '#000000'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(product_table)
        elements.append(Spacer(1, 6))

        # Crear tabla de materiales
        items_data = [
            ["Material", "Unidad", "Cantidad", "Valor Unit", "Precio Total"]
        ]

        # Inicializar total_precio_total para cada producto
        total_precio_total = 0

        # Obtener items_cotizados y depurarlos
        print(f"Producto Cotizado ID: {producto_cotizado.id}")
        for item_cotizado in producto_cotizado.items:
            item_info = Items.query.get(item_cotizado.item_id)
            if item_info:
                item_nombre = item_info.nombre
                item_unidad = item_info.unidad
                cantidad = item_cotizado.cantidad
                precio_total = item_cotizado.total_item

                # Calcular valor_unit y formatear precio_total
                valor_unit = precio_total / cantidad if cantidad != 0 else 0
                precio_total_formateado = formatear_numero(precio_total)
                valor_unit_formateado = formatear_numero(valor_unit)

                print(f"Item: {item_nombre}, Cantidad: {cantidad}, Valor Unit: {valor_unit_formateado}, Precio Total: {precio_total_formateado}")
                items_data.append([item_nombre, item_unidad, cantidad, valor_unit_formateado, precio_total_formateado])
                total_precio_total += precio_total  # Acumular el total

        # Obtener items_temporales y depurarlos
        items_temporales = ItemTemporal.query.filter_by(producto_id=producto_cotizado.id).all()
        for item_temporal in items_temporales:
            precio_unitario = item_temporal.precio / item_temporal.cantidad if item_temporal.cantidad > 0 else 0
            print(f"Item Temporal: {item_temporal.descripcion}, Unidad: {item_temporal.unidad}, Cantidad: {item_temporal.cantidad}, Precio Unitario: {precio_unitario}")

            # Agregar a la tabla los valores de descripción, unidad, cantidad, precio unitario y precio total
            items_data.append([
                item_temporal.descripcion,            # Descripción
                item_temporal.unidad,                 # Unidad
                item_temporal.cantidad,               # Cantidad
                formatear_numero(precio_unitario),    # Precio unitario
                formatear_numero(item_temporal.precio) # Precio total
            ])

            # Acumular el precio total de los items temporales
            total_precio_total += item_temporal.precio

        # Añadir fila de total a la tabla de ítems
        items_data.append(["", "", "", "Total", formatear_numero(total_precio_total)])

        # Crear la tabla de items solo si hay datos
        if len(items_data) > 1:  # Si hay más de una fila (la primera fila es el encabezado)
            items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), '#E09834'),
                ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOX', (0, 0), (-1, -1), 1, '#000000'),
                ('GRID', (0, 0), (-1, -1), 1, '#000000'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(items_table)
            elements.append(Spacer(1, 12))

        item_counter += 1

    # Añadir imagen de encabezado y pie de página
    def add_header_footer(canvas, doc):
        canvas.saveState()

        # Insertar el encabezado y pie de página
        canvas.drawImage("static/images/encabezado_requisicion.png",0, 815, height=encabezado_height, width=width,  mask='auto')
        canvas.drawImage("static/images/footer_cotizacion.png", 0, 0, width=footer_width, height=footer_height, mask='auto')

        # Posicionar la negociación en coordenadas específicas
        textobject = canvas.beginText(502, 905)  # 
        textobject.setFont("Helvetica", 10)
        textobject.textLine(cotizacion.negociacion)  # Colocar el texto de la negociación
        canvas.drawText(textobject)

        # Posicionar la fecha en coordenadas específicas
        fecha_cotizacion = cotizacion.fecha_cotizacion.strftime("%d/%m/%Y")  # Convertir a formato dd/mm/yyyy
        canvas.drawString(505, 864, f"{fecha_cotizacion}")  # Cambia las coordenadas (400, 750) por las deseadas


        canvas.restoreState()

    # Crear el documento con los elementos y agregar encabezado/pie de página
    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Requisicion - N {cotizacion.negociacion}.{cotizacion.proyecto_cotizacion}-{cotizacion.cliente_cotizacion}.pdf", mimetype='application/pdf')

@routes_blueprint.route('/verificar-negociacion')
def verificar_negociacion():
    negociacion = request.args.get('negociacion')
    
    # Busca si existe una cotización con esa negociación
    cotizacion = Cotizacion.query.filter_by(negociacion=negociacion).first()
    
    if cotizacion:
        return jsonify({"exists": True, "negociacion": cotizacion.negociacion})
    else:
        return jsonify({"exists": False})

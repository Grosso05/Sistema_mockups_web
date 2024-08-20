import datetime
from sqlite3 import IntegrityError
from flask import Blueprint, flash, jsonify, render_template, request, redirect, session, url_for,send_file
from flask_login import login_required, login_user, current_user
from models import Categoria, Cotizacion, ItemCotizado, ItemTemporal, Items, ItemsPorProducto, Lineas, PorcentajesProducto, ProductoCotizado, Productos, ResumenDeCostos, Users, ItemProveedores,db
from utils import roles_required
import locale

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO



    
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
    return render_template('/dashboard_admin.html')


#ruta para el dashboard de usuario
@routes_blueprint.route('/routes.user')
@login_required
@roles_required(2)
def user():
    if current_user.user_rol !=2:
        return render_template(url_for('users.login'))
    return render_template('dashboard_user.html')

#Ruta para generar catalogo del lado del administrador
@routes_blueprint.route('/routes.generar_catalogo')
@login_required
@roles_required(1)
def generar_catalogo():
    return render_template('generar_catalogoregistrado.html')

#ruta para generar catalogo del lado del usuario
@routes_blueprint.route('/routes.generar_catalogouser')
@login_required
@roles_required(2)
def generar_catalogouser():
    return render_template('generarcatalogouserregistrado.html')

# <------------------------------------------------------------------ SISTEMA COTIZADOR --------------------------------------------------------------------------------->

# Configurar locale
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')  # Ajusta según tu configuración regional

@routes_blueprint.route('/generar_cotizacion')
def generar_cotizacion():
    lineas = Lineas.query.all()
    productos = Productos.query.all()
    vendedores = Users.query.all() 
    return render_template('generar_cotizacion.html', lineas=lineas, productos=productos, vendedores=vendedores)

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
    busqueda = request.args.get('busqueda', '', type=str)
    items_por_pagina = 20

    query = Items.query \
        .join(ItemsPorProducto, ItemsPorProducto.item_idFK == Items.item_id) \
        .outerjoin(ItemProveedores, (ItemProveedores.item_id == Items.item_id) & (ItemProveedores.tipo_proveedor == 1)) \
        .filter(ItemsPorProducto.producto_idFK == producto_id)
    
    if busqueda:
        query = query.filter(Items.nombre.ilike(f'%{busqueda}%'))
    
    total_items = query.count()
    total_paginas = (total_items // items_por_pagina) + (1 if total_items % items_por_pagina > 0 else 0)
    
    items = query.paginate(page=pagina, per_page=items_por_pagina).items

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
    pagina = request.args.get('pagina', 1, type=int)
    busqueda = request.args.get('busqueda', '', type=str)
    items_por_pagina = 20

    query = Items.query \
        .outerjoin(ItemProveedores, (ItemProveedores.item_id == Items.item_id) & (ItemProveedores.tipo_proveedor == 1))
    
    if busqueda:
        query = query.filter(Items.nombre.ilike(f'%{busqueda}%'))

    total_items = query.count()
    total_paginas = (total_items // items_por_pagina) + (1 if total_items % items_por_pagina > 0 else 0)

    items = query.paginate(page=pagina, per_page=items_por_pagina).items

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



#Ruta para 


@routes_blueprint.route('/guardar-cotizacion', methods=['POST'])
def guardar_cotizacion():
    data = request.json
    print(data)  # Para depuración
    
    negociacion = data.get('negociacion') or ''  # Reemplaza None con una cadena vacía o un valor por defecto

    # Crear la nueva cotización
    nueva_cotizacion = Cotizacion(
        fecha_cotizacion=data['fechaCotizacion'],
        cliente_cotizacion=data['clienteCotizacion'],
        contacto_cotizacion=data['contactoCotizacion'],
        proyecto_cotizacion=data['proyectoCotizacion'],
        vendedor_cotizacion=data['vendedorCotizacion'],
        negociacion=negociacion,
        forma_de_pago_cotizacion=data['formaPago'],
        validez_cotizacion=data['validezCotizacion'],
        descuento_cotizacion=data['descuentoCotizacion'] or 0,  # Asegurarse de que no sea None
        recibe_cotizacion=data['recibeCotizacion'],
        numero_contacto_cotizacion=data['numeroContacto'],
        direccion_cotizacion=data['direccionCotizacion']
    )
    db.session.add(nueva_cotizacion)
    db.session.flush()  # Para obtener el ID de la cotización

    for producto_data in data['productos']:
        nuevo_producto_cotizado = ProductoCotizado(
            descripcion=producto_data['descripcion'],
            alto=producto_data['alto'],
            ancho=producto_data['ancho'],
            fondo=producto_data['fondo'],
            cotizacion_id=nueva_cotizacion.id_cotizacion,
            producto_id=producto_data['productoId']
        )
        db.session.add(nuevo_producto_cotizado)
        db.session.flush()  # Para obtener el ID del producto cotizado

        # Guardar los resúmenes de costos
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

        for item_data in producto_data['items']:
            nuevo_item_cotizado = ItemCotizado(
                producto_cotizado_id=nuevo_producto_cotizado.id,
                item_id=item_data['itemId'],
                cantidad=item_data['itemCantidad'],
                total_item=item_data['itemTotal']
            )
            db.session.add(nuevo_item_cotizado)

    db.session.commit()

    return jsonify({'success': True})






@routes_blueprint.route('/guardar_items', methods=['POST'])
def guardar_items():
    data = request.json
    cotizacion_id = data['cotizacion_id']
    items = data['items']
    
    for item_data in items:
        item_cotizado = ItemCotizado(
            producto_cotizado_id=item_data['producto_cotizado_id'],
            item_id=item_data['item_id'],
            cantidad=item_data['cantidad'],
            precio_unitario=item_data['precio_unitario'],
            temporal=item_data['temporal']
        )
        db.session.add(item_cotizado)
    
    db.session.commit()
    
    return jsonify({'message': 'Ítems guardados correctamente'})

@routes_blueprint.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    data = request.get_json()
    try:
        # Obtén el producto y la cotización de la base de datos
        cotizacion = Cotizacion.query.get(data.get('cotizacion_id'))
        if not cotizacion:
            return jsonify({'error': 'Cotización no encontrada'}), 404
        
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad')
        precio_unitario = data.get('precio_unitario')

        # Guarda el producto en la cotización
        item = ItemCotizado(
            cotizacion_id=cotizacion.id_cotizacion,
            producto_id=producto_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'Producto guardado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

#Ruta para listar cotizaciones

@routes_blueprint.route('/listar_cotizaciones', methods=['GET', 'POST'])
def listar_cotizaciones():
    search = request.args.get('search')
    if search:
        # Filtrar las cotizaciones según el término de búsqueda
        cotizaciones = Cotizacion.query.filter(Cotizacion.negociacion.ilike(f'%{search}%')).all()
    else:
        # Obtener todas las cotizaciones si no se ha ingresado un término de búsqueda
        cotizaciones = Cotizacion.query.all()
    
    return render_template('listar_cotizaciones.html', cotizaciones=cotizaciones)



# Definir las dimensiones de las imágenes
encabezado_width = 500  # Ancho reducido
encabezado_height = 65  # Altura reducida
footer_width = 500      # Ancho reducido
footer_height = 60      # Altura reducida
footer_margin = 20      # Margen inferior



@routes_blueprint.route('/generar-reporte/<int:cotizacion_id>', methods=['GET'])
def generar_reporte(cotizacion_id):
    # Buscar la cotización por ID
    cotizacion = Cotizacion.query.get(cotizacion_id)

    if not cotizacion:
        return "Cotización no encontrada", 404

    # Crear un buffer para almacenar el PDF
    buffer = BytesIO()

    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    width, height = letter  # Obtener el ancho y alto de la página

    # Crear el contenido del documento
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    heading_style = styles['Heading1']

    # Añadir título con estilo
    title = Paragraph(f"Cotización - Negociación: {cotizacion.negociacion}", heading_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Datos de la cotización
    data = [
        ["Fecha", cotizacion.fecha_cotizacion],
        ["Cliente", cotizacion.cliente_cotizacion],
        ["Proyecto", cotizacion.proyecto_cotizacion],
        ["Contacto", cotizacion.contacto_cotizacion],
        ["Número de Negociación", cotizacion.negociacion]
    ]

    table = Table(data, colWidths=[1.5*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#d0d0d0'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOX', (0, 0), (-1, -1), 1, '#000000'),
        ('GRID', (0, 0), (-1, -1), 1, '#000000'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Detalle de Productos
    for producto_cotizado in cotizacion.productos_cotizados:
        producto = Productos.query.get(producto_cotizado.producto_id)
        resumen_costos = ResumenDeCostos.query.filter_by(producto_id=producto_cotizado.id).first()

        # Información del Producto
        data = [
            ["Producto", producto.nombre],
            ["Medidas (Alto x Ancho x Fondo)", f"{producto_cotizado.alto} x {producto_cotizado.ancho} x {producto_cotizado.fondo}"],
            ["Descripción", Paragraph(producto_cotizado.descripcion, normal_style)]
        ]

        table = Table(data, colWidths=[1.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#d0d0d0'),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOX', (0, 0), (-1, -1), 1, '#000000'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Información General de los Items
        item_names = [Items.query.get(item_cotizado.item_id).nombre for item_cotizado in producto_cotizado.items if Items.query.get(item_cotizado.item_id)]
        items_description = "<br/>".join(item_names) if item_names else "No se especifican items."
        
        # Crear un párrafo para los ítems
        items_paragraph = Paragraph(items_description, normal_style)
        
        # Cuadro de Materiales
        materials_data = [
            ["Materiales", items_paragraph]
        ]

        materials_table = Table(materials_data, colWidths=[1.5*inch, 4*inch])
        materials_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#d0d0d0'),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOX', (0, 0), (-1, -1), 1, '#000000'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000'),
        ]))
        elements.append(materials_table)
        elements.append(Spacer(1, 12))

        # Valor Total del Producto
        if resumen_costos:
            data = [
                ["Valor Total del Producto", resumen_costos.valor_oferta]
            ]
            table = Table(data, colWidths=[1.5*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), '#d0d0d0'),
                ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOX', (0, 0), (-1, -1), 1, '#000000'),
                ('GRID', (0, 0), (-1, -1), 1, '#000000'),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

    # Añadir imagen de encabezado y pie de página
    def add_header_footer(canvas, doc):
        canvas.saveState()
        # Ajustar la imagen del encabezado
        canvas.drawImage("static/images/encabezado_cotizacion.png", 60, height - encabezado_height - 20, width=encabezado_width, height=encabezado_height, mask='auto')
        # Ajustar la imagen del pie de página
        canvas.drawImage("static/images/footer_cotizacion.png", 60, footer_margin, width=footer_width, height=footer_height, mask='auto')
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    # Enviar el PDF como respuesta
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Cotizacion_{cotizacion.negociacion}.pdf", mimetype='application/pdf')
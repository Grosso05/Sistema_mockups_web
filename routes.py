import datetime
from sqlite3 import IntegrityError
from flask import Blueprint, flash, jsonify, render_template, request, redirect, session, url_for,send_file
from flask_login import login_required, login_user, current_user
from models import Categoria, Cotizacion, ItemCotizado, ItemTemporal, Items, ItemsPorProducto, Lineas, PorcentajesProducto, ProductoCotizado, Productos, ResumenDeCostos, Users, ItemProveedores,db
from utils import roles_required
import locale
from datetime import datetime, timezone
from io import BytesIO
from flask import send_file
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from flask_login import current_user

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




@routes_blueprint.route('/generar_cotizacion')
def generar_cotizacion():
    lineas = Lineas.query.all()
    productos = Productos.query.all()
    vendedores = Users.query.all()
    user_rol = current_user.user_rol if current_user.is_authenticated else None
    return render_template('generar_cotizacion.html', lineas=lineas, productos=productos, vendedores=vendedores, user_rol=user_rol)

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



#Ruta para guardar en bd la cotizacion


@routes_blueprint.route('/guardar-cotizacion', methods=['POST'])
def guardar_cotizacion():
    data = request.json
    print(data)  # Para depuración

    negociacion = data.get('negociacion') or ''  # Reemplaza None con una cadena vacía o un valor por defecto

    # Convertir la cadena de fecha y hora a un objeto datetime
    fecha_cotizacion = datetime.fromisoformat(data['fechaCotizacion']).astimezone(timezone.utc)

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
        descuento_cotizacion=data.get('descuentoCotizacion', 0),  # Asegurarse de que no sea None
        recibe_cotizacion=data['recibeCotizacion'],
        numero_contacto_cotizacion=data['numeroContacto'],
        direccion_cotizacion=data['direccionCotizacion'],
        iva_seleccionado=data['ivaSeleccionado']
    )
    db.session.add(nueva_cotizacion)
    db.session.flush()  # Para obtener el ID de la cotización

    for producto_data in data['productos']:
        # Convertir la lista de cantidades a una cadena separada por comas
        cantidades_str = ','.join(map(str, producto_data['cantidadesSeleccionadas']))
        
        nuevo_producto_cotizado = ProductoCotizado(
            descripcion=producto_data['descripcion'],
            alto=producto_data['alto'],
            ancho=producto_data['ancho'],
            fondo=producto_data['fondo'],
            cantidades=cantidades_str,  # Usar la cadena de cantidades
            cotizacion_id=nueva_cotizacion.id_cotizacion,
            producto_id=producto_data['productoId'],
            producto_seleccionado_id=producto_data.get('productoSeleccionadoId')  # Guardar el nuevo campo
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





#Ruta para listar cotizaciones

@routes_blueprint.route('/listar_cotizaciones', methods=['GET', 'POST'])
def listar_cotizaciones():
    search = request.args.get('search')
    if search:
        # Filtrar y ordenar las cotizaciones según el término de búsqueda
        cotizaciones = Cotizacion.query.filter(Cotizacion.negociacion.ilike(f'%{search}%')).order_by(Cotizacion.fecha_cotizacion.desc()).all()
    else:
        # Obtener todas las cotizaciones y ordenarlas si no se ha ingresado un término de búsqueda
        cotizaciones = Cotizacion.query.order_by(Cotizacion.fecha_cotizacion.desc()).all()
    
    return render_template('listar_cotizaciones.html', cotizaciones=cotizaciones)


#ruta para editar la cotizacion

@routes_blueprint.route('/editar_cotizacion/<int:cotizacion_id>', methods=['GET'])
def editar_cotizacion(cotizacion_id):
    # Consulta la cotización por ID
    cotizacion = Cotizacion.query.filter_by(id_cotizacion=cotizacion_id).first()

    if not cotizacion:
        return "Cotización no encontrada", 404

    # Consulta los productos cotizados asociados a la cotización
    productos_cotizados = ProductoCotizado.query.filter_by(cotizacion_id=cotizacion_id).all()

    # Consulta los ítems cotizados asociados a cada producto cotizado y completa la información desde la tabla Items
    items_cotizados = []
    for item_cotizado in ItemCotizado.query.join(ProductoCotizado).filter(ProductoCotizado.cotizacion_id == cotizacion_id).all():
        item = item_cotizado.to_dict()

        # Consultar la relación con la tabla Items
        related_item = Items.query.get(item_cotizado.item_id)

        if related_item:
            item['grupo'] = related_item.categoria.CATEGORIA_NOMBRE if related_item.categoria else 'N/A'
            item['descripcion'] = related_item.nombre
            item['unidad'] = related_item.unidad
            item['tipo'] = related_item.tipo

            # Consultar el precio desde la tabla ItemProveedores
            precio_proveedor = ItemProveedores.query.filter_by(item_id=item_cotizado.item_id, tipo_proveedor=1).first()
            if precio_proveedor:
                item['precio_unitario'] = format(float(precio_proveedor.precio), ',.0f')
            else:
                item['precio_unitario'] = '0.00'
        else:
            item['grupo'] = 'N/A'
            item['descripcion'] = 'N/A'
            item['unidad'] = 'N/A'
            item['tipo'] = 'N/A'
            item['precio_unitario'] = '0.00'

        # Formatear el total del ítem
        item['total_item'] = format(float(item['total_item']), ',.0f')
        
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

    # Generar cabeceras para cantidad y total, basado en valores reales
    valoresCantidad = ['Cantidad1']  # Aquí debes poner tus valores reales, ajustado a la cantidad que deseas mostrar

    cantidadHeader = ''.join([f'<th>Cantidad ({valor})</th>' for valor in valoresCantidad])
    totalHeader = ''.join([f'<th>Total ({valor})</th>' for valor in valoresCantidad])

    return render_template(
        'editar_cotizacion.html',
        cotizacion=cotizacion.to_dict(),
        productos_cotizados=[p.to_dict() for p in productos_cotizados],
        items_cotizados=items_cotizados,
        resumen_costos=resumen_costos,
        cantidadHeader=cantidadHeader,
        totalHeader=totalHeader
    )




# Definir las dimensiones de las imágenes
encabezado_width = 768
encabezado_height = 30
footer_width = 750
footer_height = 30
footer_margin = 3

import locale
locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')

@routes_blueprint.route('/generar-reporte/<int:cotizacion_id>', methods=['GET'])
def generar_reporte(cotizacion_id):
    # Configuración regional para el formato de moneda
    locale.setlocale(locale.LC_ALL, '')

    # Buscar la cotización por ID
    cotizacion = Cotizacion.query.get(cotizacion_id)
    if not cotizacion:
        return "Cotización no encontrada", 404

    # Si fecha_cotizacion es un datetime, formatear directamente
    if isinstance(cotizacion.fecha_cotizacion, datetime):
        fecha_cotizacion = cotizacion.fecha_cotizacion.strftime('%Y-%m-%d')
    else:
        # Si es un string, tratar de convertirlo primero
        try:
            fecha_cotizacion = datetime.strptime(cotizacion.fecha_cotizacion, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        except ValueError:
            fecha_cotizacion = cotizacion.fecha_cotizacion  # Usar la fecha original si el formato no es el esperado

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    elements = []

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    heading_style = styles['Heading1']

    product_style = ParagraphStyle(
        'ProductStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        alignment=1,
        wordWrap='CJK'
    )

    title = Paragraph(f"Negociación: {cotizacion.negociacion}", heading_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    data = [
        ["Fecha", fecha_cotizacion, "Cliente", Paragraph(cotizacion.cliente_cotizacion, normal_style)],
        ["Proyecto", Paragraph(cotizacion.proyecto_cotizacion, normal_style), "Contacto", Paragraph(cotizacion.contacto_cotizacion, normal_style)]
    ]

    table = Table(data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 2.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d0d0d0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    header_data = [
        ["ITEM", "Imagen", "Producto", "Medidas", "Descripción", "Materiales", "Cantidad", "Valor Unidad", "Valor Total"]
    ]

    header_table = Table(header_data, colWidths=[0.3*inch, 1*inch, 1.5*inch, 1*inch, 2*inch, 2.3*inch, 0.7*inch, 0.9*inch, 0.9*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 6),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    item_counter = 1
    subtotal = 0
    multiple_quantities = False

    descuento_porcentaje = cotizacion.descuento_cotizacion / 100 if cotizacion.descuento_cotizacion else 0

    for producto_cotizado in cotizacion.productos_cotizados:
        producto = Productos.query.get(producto_cotizado.producto_seleccionado_id)

        cantidades = producto_cotizado.cantidades.split(',')
        resúmenes_costos = ResumenDeCostos.query.filter_by(producto_id=producto_cotizado.id).all()

        if len(cantidades) > 1:
            multiple_quantities = True

        cantidades_paragraph = Paragraph("<br/>".join(cantidades), normal_style)
        valores_totales = []
        valores_unitarios = []

        for i, cantidad in enumerate(cantidades):
            if i < len(resúmenes_costos):
                valor_total_inicial = resúmenes_costos[i].oferta_antes_iva

                # Si hay un descuento, inflamos el precio
                if descuento_porcentaje > 0:
                    valor_total_incrementado = valor_total_inicial / (1 - descuento_porcentaje)
                else:
                    valor_total_incrementado = valor_total_inicial

                subtotal += valor_total_incrementado
                valor_unitario = valor_total_incrementado / float(cantidad) if float(cantidad) > 0 else 0

                valores_totales.append(locale.format_string("$ %d", valor_total_incrementado, grouping=True))
                valores_unitarios.append(locale.format_string("$ %.2f", valor_unitario, grouping=True))
            else:
                valores_totales.append("$ 0")
                valores_unitarios.append("$ 0.00")

        valores_totales_paragraph = Paragraph("<br/>".join(valores_totales), normal_style)
        valores_unitarios_paragraph = Paragraph("<br/>".join(valores_unitarios), normal_style)

        item_names = [Items.query.get(item_cotizado.item_id).nombre for item_cotizado in producto_cotizado.items if Items.query.get(item_cotizado.item_id)]
        items_description = "//".join(item_names) if item_names else "No se especifican items."
        items_paragraph = Paragraph(items_description, product_style)
        producto_descripcion = Paragraph(producto_cotizado.descripcion, product_style)

        product_name_paragraph = Paragraph(producto.nombre, product_style)

        data = [
            str(item_counter),
            "",
            product_name_paragraph,
            f"{producto_cotizado.alto} x {producto_cotizado.ancho} x {producto_cotizado.fondo}",
            producto_descripcion,
            items_paragraph,
            cantidades_paragraph,
            valores_unitarios_paragraph,
            valores_totales_paragraph
        ]

        product_table = Table([data], colWidths=[0.3*inch, 1*inch, 1.5*inch, 1*inch, 2*inch, 2.3*inch, 0.7*inch, 0.9*inch, 0.9*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 6),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(product_table)
        elements.append(Spacer(1, 1))

        item_counter += 1

            # Definir un estilo de tabla común
        table_style = ParagraphStyle(
            'TableStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,  # Ajustar el tamaño de la fuente si es necesario
            alignment=1,
            wordWrap='CJK'
        )


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

        # Ajusta el ancho de las columnas para mover la tabla a la derecha
        col_widths = [2.5*inch, 1.5*inch]  # Ajusta el ancho de las columnas según sea necesario
        summary_table = Table(summary_data, colWidths=col_widths)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Agregar un espacio para mover la tabla hacia la derecha
        right_space = Spacer(10, 2)  # Ajusta el tamaño del espacio según sea necesario
        elements.append(right_space)
        elements.append(summary_table)

    # Construir PDF
        # Añadir imagen de encabezado y pie de página
    def add_header_footer(canvas, doc):
        canvas.saveState()
        # Ajustar la imagen del encabezado
        canvas.drawImage("static/images/encabezado_cotizacion.png", 10, height - encabezado_height - 10, width=encabezado_width, height=encabezado_height, mask='auto')
        # Ajustar la imagen del pie de página
        canvas.drawImage("static/images/footer_cotizacion.png", 20, footer_margin, width=footer_width, height=footer_height, mask='auto')
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'Cotizacion_{cotizacion.negociacion}.pdf', mimetype='application/pdf')

# < ----------------------------------------------------------  Ruta para generar OP ---------------------------------------------------------------------------------------->

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

    # Crear un buffer para almacenar el PDF
    buffer = BytesIO()

    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)  # Obtener el ancho y alto de la página

    # Crear el contenido del documento
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    heading_style = styles['Heading1']

    # Añadir título con estilo
    title = Paragraph(f"Orden de Producción - OP: {cotizacion.negociacion}", heading_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Datos de la OP en una tabla horizontal
    data = [
        ["Fecha", cotizacion.fecha_cotizacion, "Cliente", cotizacion.cliente_cotizacion],
        ["Proyecto", cotizacion.proyecto_cotizacion, "Vendedor", vendedor_nombre]
    ]

    table = Table(data, colWidths=[1*inch, 3.5*inch, 1*inch, 3.5*inch]) #8inch
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#d0d0d0'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, '#000000'),
        ('GRID', (0, 0), (-1, -1), 1, '#000000'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Cabecera de la tabla de productos
    header_data = [
        ["ITEM", "Descripción", "Medidas", "Cantidad"]
    ]

    header_table = Table(header_data, colWidths=[0.5*inch, 5*inch, 3*inch, 0.5*inch]) #8inch
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#4CAF50'),
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

        product_table = Table([data], colWidths=[0.5*inch, 5*inch, 3*inch, 0.5*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#e0e0e0'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, '#000000'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(product_table)
        elements.append(Spacer(1, 6))  # Espacio para separar productos

        # Crear tabla de materiales
        items_data = [
            ["Material", "Unidad", "Cantidad"]
        ]

        item_names = [Items.query.get(item_cotizado.item_id).nombre for item_cotizado in producto_cotizado.items if Items.query.get(item_cotizado.item_id)]
        item_units = [Items.query.get(item_cotizado.item_id).unidad for item_cotizado in producto_cotizado.items if Items.query.get(item_cotizado.item_id)]
        item_quantities = [item_cotizado.cantidad for item_cotizado in producto_cotizado.items]

        for name, unit, quantity in zip(item_names, item_units, item_quantities):
            items_data.append([name, unit, quantity])

        items_table = Table(items_data, colWidths=[5*inch, 3*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#c0c0c0'),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, '#000000'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 12))  # Espacio después de la tabla de materiales

        item_counter += 1

    # Añadir imagen de encabezado y pie de página
    def add_header_footer(canvas, doc):
        canvas.saveState()
        # Ajustar la imagen del encabezado
        canvas.drawImage("static/images/encabezado_cotizacion.png", 10, height - encabezado_height - 20, width=encabezado_width, height=encabezado_height, mask='auto')
        # Ajustar la imagen del pie de página
        canvas.drawImage("static/images/footer_cotizacion.png", 20, footer_margin, width=footer_width, height=footer_height, mask='auto')
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    # Enviar el PDF como respuesta
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"OP_{cotizacion.negociacion}.pdf", mimetype='application/pdf')


# <-------------------------------------------------------- Ruta para generar Requisición ------------------------------------------------------------------------------------------------->

# Función para formatear números
def formatear_numero(valor):
    # Formatear con puntos como separadores de miles
    return "{:,.0f}".format(valor).replace(",", ".")

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

    # Crear un buffer para almacenar el PDF
    buffer = BytesIO()

    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Crear el contenido del documento
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    heading_style = styles['Heading1']

    # Añadir título con estilo
    title = Paragraph(f"Requisición - {cotizacion.negociacion}", heading_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Datos de la OP en una tabla horizontal
    data = [
        ["Fecha", cotizacion.fecha_cotizacion, "Cliente", cotizacion.cliente_cotizacion],
        ["Proyecto", cotizacion.proyecto_cotizacion, "Vendedor", vendedor_nombre]
    ]

    table = Table(data, colWidths=[1*inch, 3.5*inch, 1*inch, 3.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#d0d0d0'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, '#000000'),
        ('GRID', (0, 0), (-1, -1), 1, '#000000'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Cabecera de la tabla de productos
    header_data = [
        ["ITEM", "Descripción", "Cantidad"]
    ]

    header_table = Table(header_data, colWidths=[0.5*inch, 3.5*inch, 1*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#4CAF50'),
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
            ('BACKGROUND', (0, 0), (-1, 0), '#e0e0e0'),
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

        for item_cotizado in producto_cotizado.items:
            item_nombre = Items.query.get(item_cotizado.item_id).nombre
            item_unidad = Items.query.get(item_cotizado.item_id).unidad
            cantidad = item_cotizado.cantidad
            precio_total = item_cotizado.total_item

            # Calcular valor_unit y formatear precio_total
            valor_unit = precio_total / cantidad if cantidad != 0 else 0
            precio_total_formateado = formatear_numero(precio_total)
            valor_unit_formateado = formatear_numero(valor_unit)

            items_data.append([item_nombre, item_unidad, cantidad, valor_unit_formateado, precio_total_formateado])
            total_precio_total += precio_total  # Acumular el total

        # Añadir fila de total a la tabla de ítems
        items_data.append(["", "", "", "             Total", formatear_numero(total_precio_total)])

        items_table = Table(items_data, colWidths=[3.5*inch, 2*inch, 1*inch, 1.5*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#c0c0c0'),
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
        # Ajustar la imagen del encabezado
        canvas.drawImage("static/images/encabezado_cotizacion.png", 10, height - encabezado_height - 10, width=encabezado_width, height=encabezado_height, mask='auto')
        # Ajustar la imagen del pie de página
        canvas.drawImage("static/images/footer_cotizacion.png", 20, footer_margin, width=footer_width, height=footer_height, mask='auto')
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    # Enviar el PDF como respuesta
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Requisicion_{cotizacion.negociacion}.pdf", mimetype='application/pdf')

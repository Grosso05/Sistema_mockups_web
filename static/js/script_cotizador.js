document.addEventListener('DOMContentLoaded', () => {
    // Recuperar datos desde las etiquetas <script> en el HTML
    const lineasElement = document.getElementById('lineas-data');
    const productosElement = document.getElementById('productos-data');

    // Parsear los datos JSON
    const lineas = lineasElement ? JSON.parse(lineasElement.textContent) : [];
    const productos = productosElement ? JSON.parse(productosElement.textContent) : [];


    document.addEventListener('DOMContentLoaded', () => {
        // Implementación del debounce
        let debounceTimeout;
        const debounceBuscar = (callback, delay = 300) => {
            return (...args) => {
                clearTimeout(debounceTimeout);
                debounceTimeout = setTimeout(() => callback(...args), delay);
            };
        };
    
        // Función para manejar la búsqueda
        const manejarBusqueda = (productoId) => (evento) => {
            const termino = evento.target.value;
            console.log(`Buscando en producto ${productoId}:`, termino);
            cargarTodosLosItems(productoId, 1, termino);
        };
    
        // Seleccionar todos los inputs de búsqueda dinámicamente
        document.querySelectorAll('[id^="busquedaInput-"]').forEach((input) => {
            const productoId = input.id.split('-')[1]; // Obtener el ID dinámico
            input.addEventListener('input', debounceBuscar(manejarBusqueda(productoId), 300));
        });
    });


        // Barra lateral
        function toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const content = document.querySelector('main');

        if (sidebar.classList.contains('collapsed')) {
            sidebar.classList.remove('collapsed');
            content.style.marginLeft = '250px';
            content.style.width = 'calc(100% - 250px)';
        } else {
            sidebar.classList.add('collapsed');
            content.style.marginLeft = '0';
            content.style.width = '100%';
        }
        }

        function closeSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const content = document.querySelector('main');
        sidebar.classList.add('collapsed');
        content.style.marginLeft = '0';
        content.style.width = '100%';
        }

        // Dropdowns
        function toggleDropdown(id) {
        const dropdown = document.getElementById(id);
        const icon = event.currentTarget.querySelector('i.fas');

        if (dropdown.style.display === "block") {
            dropdown.style.display = "none";
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
        } else {
            dropdown.style.display = "block";
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
        }
        }


        // Toggle para formulario de cotización
        document.getElementById('toggleDatosBtn').addEventListener('click', function() {
        const formularioCotizacion = document.getElementById('formulario-cotizacion');
        formularioCotizacion.style.display = formularioCotizacion.style.display === 'none' ? 'flex' : 'none';
        this.textContent = formularioCotizacion.style.display === 'none' ? '>' : 'v';
        this.classList.toggle('expandido');
        });

        // Mostrar formulario al cargar
        document.addEventListener('DOMContentLoaded', function() {
        const formularioCotizacion = document.getElementById('formulario-cotizacion');
        formularioCotizacion.style.display = 'flex';
        });

        // Variables de productos
        let itemNumber = 0; // Número global de productos
        let productosDinamicos = []; // Cambiado el nombre a productosDinamicos para evitar conflicto
        let productosEliminados = []; // Lista para almacenar los productos eliminados
        const productosContainer = document.getElementById('productos-container');
        let temporalItemID = 1;
        let valoresCantidad = [];

        // Función para cargar productos por línea
        function cargarProductosPorLinea(lineaId, productoSelect) {
        if (lineaId) {
            fetch(`/productos_por_linea/${lineaId}`)
                .then(response => response.json())
                .then(productos => {
                    productoSelect.innerHTML = '<option value="">Seleccionar</option>';
                    productos.forEach(producto => {
                        const option = document.createElement('option');
                        option.value = producto.id;
                        option.textContent = producto.nombre;
                        option.dataset.lineaId = producto.linea_id;
                        productoSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error(`Error al cargar productos para la línea ${lineaId}:`, error);
                });
        } else {
            cargarTodosLosProductos(productoSelect);
        }
        }

        // Función para cargar todos los productos
        function cargarTodosLosProductos(productoSelect) {
        fetch('/todos_los_productos')
            .then(response => response.json())
            .then(productos => {
                productos.sort((a, b) => a.nombre.localeCompare(b.nombre));
                productoSelect.innerHTML = '<option value="">Seleccionar</option>';
                productos.forEach(producto => {
                    const option = document.createElement('option');
                    option.value = producto.id;
                    option.textContent = producto.nombre;
                    productoSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error al cargar todos los productos:', error);
            });
        }

        // Función para cargar porcentajes de un producto
        function cargarPorcentajesProducto() {
        const productoId = document.getElementById('seleccionarProducto').value;

        if (productoId) {
            fetch(`/porcentajes/${productoId}`)
                .then(response => response.json())
                .then(porcentajes => {
                    if (!porcentajes.error) {
                        const productoElement = document.querySelector(`#producto-${productoId}`);
                        if (productoElement) {
                            productoElement.dataset.administracion = porcentajes.administracion;
                            productoElement.dataset.imprevistos = porcentajes.imprevistos;
                            productoElement.dataset.utilidad = porcentajes.utilidad;

                            const inputUtilidad = document.getElementById('utilidadSeleccionada');
                            inputUtilidad.placeholder = `El porcentaje mínimo es: ${porcentajes.utilidad}`;
                            inputUtilidad.min = porcentajes.utilidad;
                        }
                    }
                })
                .catch(error => {
                    console.error('Error al cargar los porcentajes:', error);
                });
        }
        }



        document.getElementById('productos-container').addEventListener('click', function (event) {
        // Delegación de evento para el botón de agregar cantidad
        if (event.target.classList.contains('btnAgregarCantidad')) {
            const cantidadContainer = event.target.closest('.cantidad-container');
            agregarCantidad(cantidadContainer);
        }
        // Delegación de evento para el botón de eliminar cantidad
        else if (event.target.classList.contains('btnEliminarCantidad')) {
            const cantidadContainer = event.target.closest('.cantidad-container');
            eliminarCantidad(cantidadContainer);
        }
        });

        document.getElementById('btnCrearVacio').addEventListener('click', function () {
            if (lineas.length === 0) {
                console.error('Las líneas aún no han sido cargadas');
                return;
            }
        
            // Usamos el primer número disponible de los eliminados, si no hay ninguno, incrementamos itemNumber
            let nuevoItemNumber = productosEliminados.length > 0 ? productosEliminados.shift() : ++itemNumber;
        
            const nuevoProducto = document.createElement('div');
            nuevoProducto.className = 'producto';
            nuevoProducto.id = `producto-${nuevoItemNumber}`;
            nuevoProducto.style.marginBottom = '15px';
            nuevoProducto.style.border = '1px solid #ccc';
            nuevoProducto.style.padding = '10px';
            nuevoProducto.style.borderRadius = '5px';
        
            // Crear el contenido dinámico del producto (producto vacío)
            nuevoProducto.innerHTML = `
        <!-- Título del producto -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #ccc; padding-bottom: 10px;">
            <h3 contenteditable="true" style="margin: 0;">Producto ${nuevoItemNumber}</h3>
        </div>

        <!-- Información básica del producto -->
        <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between; width: 100%; border-bottom: 1px solid #ccc; padding-bottom: 10px;">
            <!-- Descripción -->
            <textarea contenteditable="true" style="flex: 1; width: 18%; resize: none; height: 50px; margin: 0;" placeholder="Descripción"></textarea>
            
            <!-- Medidas -->
            <div style="display: flex; gap: 5px; align-items: center; flex: 1; width: 18%; justify-content: space-evenly;">
                <div>
                    <label>Alto:</label>
                    <input type="number" placeholder="0" style="width: 60px;">
                </div>
                <div>
                    <label>Ancho:</label>
                    <input type="number" placeholder="0" style="width: 60px;">
                </div>
                <div>
                    <label>Fondo:</label>
                    <input type="number" placeholder="0" style="width: 60px;">
                </div>
            </div>

            <!-- Cantidades -->
            <div class="cantidad-container" style="display: flex; align-items: center; gap: 5px; flex: 1; width: 18%;">
                <label>Cantidad:</label>
                <input type="number" class="cantidad-input" name="cantidadUnidades" min="1" value="1" style="width: 60px;">
                <button class="btnAgregarCantidad" type="button" style="padding: 5px;">+</button>
                <button class="btnEliminarCantidad" type="button" style="padding: 5px;">-</button>
            </div>

            <!-- Selects -->
            <div style="display: flex; flex-direction: column; gap: 5px; align-items: center; flex: 1; width: 18%;">
                <select class="linea-select" style="width: 90%;">
                    <option value="">Seleccionar Línea</option>
                    ${lineas.map(linea => `<option value="${linea.linea_id}">${linea.nombre}</option>`).join('')}
                </select>
                <select class="producto-select" style="width: 90%;">
                    <option value="">Seleccionar Producto</option>
                </select>
            </div>

            <!-- Botones -->
            <div class="acciones" style="display: flex; flex-direction: column; gap: 5px; align-items: center; flex: 1; width: 18%;">
                <button class="editar-producto-btn" data-producto-id="${nuevoItemNumber}" style="background-color: orange; color: white; border: none; padding: 5px 10px; border-radius: 4px;">Editar</button>
                <button class="confirmar-producto-btn" data-producto-id="${nuevoItemNumber}" style="background-color: green; color: white; border: none; padding: 5px 10px; border-radius: 4px;">Confirmar</button>
                <button class="eliminar-producto-btn" data-producto-id="${nuevoItemNumber}" style="background-color: red; color: white; border: none; padding: 5px 10px; border-radius: 4px;">Eliminar</button>
                <button class="duplicar-producto-btn" data-producto-id="${nuevoItemNumber}" style="background-color: blue; color: white; border: none; padding: 5px 10px; border-radius: 4px;">Duplicar</button>
            </div>
        </div>

        <!-- Contenido expandible -->
        <div class="contenido-expandible" id="contenido-expandible-${nuevoItemNumber}" style="display: none; margin-top: 10px; border-top: 1px solid #ccc; padding-top: 10px;">

<!-- Tabla de ítems seleccionados -->
<div class="items-seleccionados" id="itemsSeleccionados-${nuevoItemNumber}">
    <h4>Ítems Seleccionados</h4>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Descripción</th>
                <th>Unidad</th>
                <th>Precio</th>
                <th>Cantidad</th>
                <th>Total</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody id="itemsseleccionados-${nuevoItemNumber}">
            <!-- Aquí se cargarán los ítems seleccionados -->
        </tbody>
    </table>
</div>

        <!-- Resumen de Costos -->
    <!-- Resumen de Costos -->
    <div class="resumen-costos" id="resumenCostos-${nuevoItemNumber}">
        <h4>Resumen de Costos</h4>
        <table>
            <tbody>
                <tr>
                    <td>Costo Directo:</td>
                    <td id="costoDirecto-${nuevoItemNumber}">0</td>
                </tr>
                <tr>
                    <td>Costo Directo Unitario:</td>
                    <td id="costoDirectoUnitario-${nuevoItemNumber}">0</td>
                </tr>
                <tr>
                    <td>Administración:</td>
                    <td id="administracion-${nuevoItemNumber}">0</td>
                    <td id="porcentajeAdministracion-${nuevoItemNumber}">%</td> <!-- Aquí va el porcentaje -->
                </tr>
                <tr>
                    <td>Imprevistos:</td>
                    <td id="imprevistos-${nuevoItemNumber}">0</td>
                    <td id="porcentajeImprevistos-${nuevoItemNumber}">%</td> <!-- Aquí va el porcentaje -->
                </tr>
                <tr>
                    <td>Utilidad:</td>
                    <td id="utilidad-${nuevoItemNumber}">0</td>
                    <td id="porcentajeUtilidad-${nuevoItemNumber}">%</td> <!-- Aquí va el porcentaje -->
                </tr>

                <tr>
                    <td>Oferta Antes de IVA:</td>
                    <td id="ofertaAntesIVA-${nuevoItemNumber}">0</td>
                </tr>
                <tr>
                    <td>Precio Unitario de Venta:</td>
                    <td id="precioUnitarioVenta-${nuevoItemNumber}">0</td>
                </tr>
                <tr>
                    <td>IVA:</td>
                    <td id="iva-${nuevoItemNumber}">0</td>
                </tr>
                <tr>
                    <td>Valor Oferta Impuestos Incluidos:</td>
                    <td id="valorOfertaImpuestos-${nuevoItemNumber}">0</td>
                </tr>
            </tbody>
        </table>
    </div>

        <!-- Tabla de ítems sugeridos -->
        <div>


        <!-- Contenedor de tablas -->
        <div class="tab-content" id="sugeridos-${nuevoItemNumber}" style="display: block;">
            <h4>Ítems Sugeridos</h4>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Descripción</th>
                        <th>Unidad</th>
                        <th>Precio</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody id="itemssugeridos-${nuevoItemNumber}">
                    <!-- Aquí se cargarán los ítems sugeridos -->
                </tbody>
            </table>
        </div>

        <div class="tab-content" id="todos-${nuevoItemNumber}" style="display: none;">
            <h4>Todos los Ítems</h4>
<input 
    type="text" 
    id="busquedaInput-${nuevoItemNumber}" 
    placeholder="Buscar ítems..." 
    style="margin-bottom: 10px;"
>

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Descripción</th>
                        <th>Categoría</th>
                        <th>Unidad</th>
                        <th>Tipo</th>
                        <th>Precio</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody id="todositems-${nuevoItemNumber}">
                    <!-- Aquí se cargarán todos los ítems -->
                </tbody>
            </table>
                <div id="todositems-pagination-1" class="pagination-container" style="text-align: center; margin-top: 10px;">
            <!-- Aquí se generarán los botones de paginación -->
        </div>
        </div>
        </div>

        <!-- Selector para alternar entre tablas -->
        <div style="margin-bottom: 10px;">
            <button class="tab-btn" data-tab="sugeridos-${nuevoItemNumber}">Ítems Sugeridos</button>
            <button class="tab-btn" data-tab="todos-${nuevoItemNumber}">Todos los Ítems</button>
        </div>

        `;

        document.addEventListener('change', function (event) {
            if (event.target.matches('.producto-select')) {
                const selectProducto = event.target;
                const productoCotizacionId = selectProducto.closest('.producto').id.split('-')[1]; // Obtener el nuevoItemNumber (ID de la cotización)
                const productoId = selectProducto.value; // Obtener el productoId real seleccionado
        
                if (productoId) {
                    console.log(`Producto seleccionado con ID: ${productoId}`);
                    obtenerYMostrarPorcentajes(productoCotizacionId, productoId);  // Pasamos el nuevoItemNumber y el productoId
                } else {
                    console.log("No se ha seleccionado un producto.");
                }
            }
        });
        
    // Seleccionar el campo de cantidad
    const cantidadInput = nuevoProducto.querySelector('.cantidad-input');

    // Añadir evento input para recalcular el Costo Directo Unitario
    cantidadInput.addEventListener('input', function () {
        let cantidad = parseFloat(cantidadInput.value);
        if (isNaN(cantidad) || cantidad < 1) {
            cantidad = 1; // Restablecer a 1 si el valor no es válido
            cantidadInput.value = cantidad;
        }

        // Recalcular los costos asociados al producto
        actualizarResumenCostos(nuevoItemNumber);
    });

        document.addEventListener('click', function (event) {   
        console.log('Evento detectado:', event.target); // Para depuración

        const target = event.target;

        // Verificar si el botón "Confirmar" fue clickeado
        if (target.matches('.confirmar-producto-btn')) {
            const productoId = target.dataset.productoId;
            const producto = document.getElementById(`producto-${productoId}`);
            const textarea = producto.querySelector('textarea');

            console.log('Confirmar Producto:', productoId); // Depuración
            textarea.setAttribute('readonly', true);
            alert(`Producto ${productoId} confirmado.`);
        } 
        // Verificar si el botón "Editar" fue clickeado
        else if (target.matches('.editar-producto-btn')) {
            const productoId = target.dataset.productoId;
            const producto = target.closest('.producto'); // Buscar el contenedor más cercano que tenga la clase .producto
            const textarea = producto.querySelector('textarea');
            const contenidoExpandible = producto.querySelector('.contenido-expandible'); // Buscar el contenido expandible correspondiente
            const selectProducto = producto.querySelector('.producto-select'); // Buscar el select de producto

            const selectedProductoId = selectProducto.value;

            // Verificar si no se ha seleccionado un producto
            if (!selectedProductoId) {
                alert('Por favor, selecciona un producto antes de editar.');
                return; // No permitir la edición si no hay producto seleccionado
            }

            console.log('Editar Producto:', productoId); // Depuración
            // Hacer el textarea editable
            textarea.removeAttribute('readonly');
            alert(`Producto ${productoId} editable.`);

            // Alternar la visibilidad del contenido expandible
            if (contenidoExpandible) {
                if (contenidoExpandible.style.display === "none" || contenidoExpandible.style.display === "") {
                    contenidoExpandible.style.display = "block"; // Mostrar el contenido expandible
                    console.log(`Contenido expandible para Producto ${productoId} mostrado.`); // Depuración
                } else {
                    contenidoExpandible.style.display = "none"; // Ocultar el contenido expandible
                    console.log(`Contenido expandible para Producto ${productoId} oculto.`); // Depuración
                }
            }
        } 
        // Verificar si el botón "Eliminar" fue clickeado
        else if (target.matches('.eliminar-producto-btn')) {
            const productoId = target.dataset.productoId;
            const confirmacion = confirm(`¿Estás seguro de eliminar el producto ${productoId}?`);
            if (confirmacion) {
                const producto = document.getElementById(`producto-${productoId}`);
                producto.remove(); // Eliminar el producto del DOM
                alert(`Producto ${productoId} eliminado.`);
            }
        }
        // Nuevo bloque: Verificar si el botón "Agregar" en la tabla de ítems fue clickeado
        else if (target.matches('.btnAgregar')) {
            const itemRow = target.closest('tr'); // Fila del ítem
            const productoId = target.closest('.producto').id.split('-')[1]; // ID del producto
            
            const itemId = parseInt(itemRow.querySelector('td:nth-child(1)').textContent.trim(), 10); // ID del ítem
            const item = {
                id: itemId,  // Asegurarse de que este es un número
                descripcion: itemRow.querySelector('td:nth-child(2)').textContent.trim(),
                unidad: itemRow.querySelector('td:nth-child(3)').textContent.trim(),
                precio: parseFloat(itemRow.querySelector('td:nth-child(4)').textContent.trim()).toFixed(2),
            };
        
            console.log('Item ID antes de mover:', item.id); // Verificación de item.id
            console.log('Objeto item:', item);  // Verificación del objeto item
            
            // Ahora pasa solo item.id (no todo el objeto) a moverItemASeleccionados
            moverItemASeleccionados(item.id, productoId);
        
            // Ocultar el ítem de las tablas de sugeridos y todos los ítems
            ocultarItemDeSugeridos(item.id, productoId);
            actualizarCostoDirecto(productoId);
        }
        

        // Verificar si el botón "Eliminar" en los ítems seleccionados fue clickeado
        else if (target.matches('.btnEliminarItem')) {
            const itemRow = target.closest('tr'); // Fila del ítem
            const productoId = target.closest('.producto').id.split('-')[1]; // ID del producto
            const itemId = itemRow.querySelector('td:nth-child(1)').textContent.trim(); // ID del ítem

            // Eliminar el ítem de la tabla de seleccionados
            itemRow.remove();
            
            // Volver a mostrar el ítem en la tabla de sugeridos
            mostrarItemEnSugeridos(itemId, productoId);
            actualizarResumenCostos();
        }
        });
        
        

        document.addEventListener('click', function (event) {
        if (event.target.classList.contains('tab-btn')) {
            const tabId = event.target.getAttribute('data-tab');

            // Ocultar todas las tablas
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
            });

            // Mostrar la tabla seleccionada
            const selectedTab = document.getElementById(tabId);
            selectedTab.style.display = 'block';

            // Si es la tabla "Todos los Ítems", cargar los datos
            if (tabId.startsWith('todos-')) {
                const productoId = tabId.split('-')[1]; // Extraer el ID del producto
                cargarTodosLosItems(productoId); // Llamar a la función para cargar los ítems
            }
        }
        });

        document.addEventListener('change', function (event) {
            if (event.target.matches('.producto-select')) {
                const selectProducto = event.target;
                const productoId = selectProducto.value; // Obtener el productoId directamente desde el select
        
                console.log(`Producto seleccionado con ID: ${productoId}`); // Verificamos el id seleccionado
        
                if (productoId) {
                    // Si se selecciona un producto, cargar los ítems sugeridos
                    const productoDiv = selectProducto.closest('.producto');
                    const nuevoItemNumber = productoDiv.id.split('-')[1]; // Extraemos el nuevoItemNumber asociado al div
                    cargarItemsSugeridos(nuevoItemNumber, productoId);
        
                    // Llamamos a obtener los porcentajes del producto seleccionado
                    obtenerYMostrarPorcentajes(productoId);
                } else {
                    // Si no hay producto seleccionado, limpiar los ítems
                    const productoDiv = selectProducto.closest('.producto');
                    const productoId = productoDiv.id.split('-')[1]; // Obtener el productoId del div
                    const tbody = document.querySelector(`#itemsseleccionados-${productoId}`);
                    tbody.innerHTML = ''; // Limpiar la tabla de ítems
                }
            }
        });
        

        function formatearPesosColombianos(numero) {
            // Asegurarse de que el precio sea un número
            let precio = parseFloat(numero);
        
            // Verificar si el precio es un número válido
            if (isNaN(precio)) {
                return 'SIN PRECIO'; // En caso de que no sea un precio válido
            }
        
            // Formatear el precio con puntos como separadores de miles
            let precioFormateado = precio.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        
            return precioFormateado;
        }
        
        


        // Función para cargar ítems sugeridos dinámicamente desde el backend
        function cargarItemsSugeridos(productoId, selectedProductoId) {
        const tbody = document.querySelector(`#itemssugeridos-${productoId}`);
        if (tbody.children.length > 0) return; // Si ya hay ítems, no recargar.

        // Hacer la solicitud al backend
        fetch(`/items_por_producto/${selectedProductoId}`)
            .then(response => {
                if (!response.ok) throw new Error(`Error al cargar ítems para el producto ${selectedProductoId}`);
                return response.json();
            })
            .then(data => {
                const { items } = data;

                // Renderizar los ítems en la tabla
                items.forEach(item => {
                    const fila = document.createElement('tr');
                    fila.setAttribute('data-item-id', item.id); // Añadir el atributo data-item-id
                    fila.innerHTML = `
                        <td>${item.id}</td>
                        <td>${item.descripcion}</td>
                        <td>${item.unidad}</td>
                        <td>${formatearPesosColombianos(item.precio)}</td>
                        <td>
                            <button class="btnAgregar" data-item-id="${item.id}">Agregar</button>
                        </td>
                    `;
                    tbody.appendChild(fila);
                });

                console.log(`Cargados ${items.length} ítems para el producto ${selectedProductoId}`);
            })
            .catch(error => {
                console.error(`Error cargando ítems: ${error.message}`);
            });
        }


        document.addEventListener('DOMContentLoaded', () => {
            const inputs = document.querySelectorAll('[id^="busquedaInput-"]');
            console.log(`Inputs encontrados: ${inputs.length}`); // ¿Cuántos inputs detecta?
            inputs.forEach(input => console.log(`ID de input detectado: ${input.id}`));
        });
         

        document.addEventListener('DOMContentLoaded', () => {
            // Asociar el evento 'input' a los campos de búsqueda
            document.querySelectorAll('[id^="busquedaInput-"]').forEach(input => {
                const productoId = input.id.split('-')[1]; // Extraer el ID dinámico
                console.log(`Input detectado: ${input.id}, Producto ID: ${productoId}`); // Depuración
        
                input.addEventListener('input', () => {
                    const busqueda = input.value.trim(); // Texto ingresado por el usuario
                    console.log(`Buscando: ${busqueda} para producto ${productoId}`); // Depuración
                    cargarTodosLosItems(productoId, 1, busqueda); // Reiniciar a la página 1
                });
            });
        });
        
        

        

        function cargarTodosLosItems(productoId, pagina = 1, busqueda = '') {
            const tbody = document.querySelector(`#todositems-${productoId}`);
            const paginationContainer = document.querySelector(`#todositems-pagination-${productoId}`);
        
            if (!tbody || !paginationContainer) {
                console.error("No se encontró el contenedor adecuado.");
                return;
            }
        
            // Mostrar mensaje de carga
            tbody.innerHTML = '<tr><td colspan="7">Cargando...</td></tr>';
        
            console.log(`Realizando petición a: /todos_los_items?pagina=${pagina}&busqueda=${encodeURIComponent(busqueda)}`);
            fetch(`/todos_los_items?pagina=${pagina}&busqueda=${encodeURIComponent(busqueda)}`)
                .then(response => {
                    if (!response.ok) throw new Error('Error al cargar los ítems');
                    return response.json();
                })
                .then(data => {
                    const { items, totalPaginas } = data;
        
                    // Limpiar el tbody antes de renderizar
                    tbody.innerHTML = '';
        
                    if (items.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="7">No se encontraron ítems.</td></tr>';
                        return;
                    }
        
                    // Renderizar la tabla
                    items.forEach(item => {
                        const fila = document.createElement('tr');
                        fila.setAttribute('data-item-id', item.id);  // Aquí agregamos el atributo data-item-id
                        fila.innerHTML = `
                            <td>${item.id}</td>
                            <td>${item.descripcion}</td>
                            <td>${item.categoria || 'Sin Categoría'}</td>
                            <td>${item.unidad}</td>
                            <td>${item.tipo}</td>
                            <td>${formatearPesosColombianos(item.precio)}</td>
                            <td><button class="btnAgregar" data-item-id="${item.id}">Agregar</button></td>
                        `;
                        tbody.appendChild(fila);
                    });
                    
        
                    // Configurar el evento en los inputs dinámicos
                    console.log("Configurando eventos para inputs dinámicos...");
                    document.querySelectorAll('[id^="busquedaInput-"]').forEach(input => {
                        const productoId = input.id.split('-')[1]; // Extraer ID del producto
                        input.removeEventListener('input', handleBusqueda); // Asegurar no duplicar eventos
                        input.addEventListener('input', handleBusqueda);
                    });
        
                  
                    // Actualizar paginación
                    paginationContainer.innerHTML = '';
                    const maxVisibleButtons = 9; // Máximo de botones visibles
                    const half = Math.floor(maxVisibleButtons / 2);
                    let startPage = Math.max(1, pagina - half);
                    let endPage = Math.min(totalPaginas, pagina + half);

                    if (endPage - startPage + 1 < maxVisibleButtons) {
                        if (startPage === 1) {
                            endPage = Math.min(totalPaginas, startPage + maxVisibleButtons - 1);
                        } else if (endPage === totalPaginas) {
                            startPage = Math.max(1, endPage - maxVisibleButtons + 1);
                        }
                    }

                    // Botón "Anterior"
                    if (pagina > 1) {
                        const prevButton = document.createElement('button');
                        prevButton.textContent = '«';
                        prevButton.addEventListener('click', () => cargarTodosLosItems(productoId, pagina - 1, busqueda));
                        paginationContainer.appendChild(prevButton);
                    }

                    // Botones de las páginas
                    for (let i = startPage; i <= endPage; i++) {
                        const button = document.createElement('button');
                        button.textContent = i;
                        if (i === pagina) button.classList.add('active');
                        button.addEventListener('click', () => cargarTodosLosItems(productoId, i, busqueda));
                        paginationContainer.appendChild(button);
                    }

                    // Botón "Siguiente"
                    if (pagina < totalPaginas) {
                        const nextButton = document.createElement('button');
                        nextButton.textContent = '»';
                        nextButton.addEventListener('click', () => cargarTodosLosItems(productoId, pagina + 1, busqueda));
                        paginationContainer.appendChild(nextButton);
                    }
                })
                .catch(error => {
                    console.error('Error al cargar los ítems:', error);
                    tbody.innerHTML = '<tr><td colspan="7">Error al cargar los ítems.</td></tr>';
                });
        }
        
        let debounceTimer; // Variable global para el temporizador

        // Manejo del evento input con debounce
        function handleBusqueda(event) {
            const input = event.target;
            const productoId = input.id.split('-')[1];
            const busqueda = input.value.trim();
        
            // Limpiar cualquier temporizador anterior
            clearTimeout(debounceTimer);
        
            // Configurar un nuevo temporizador
            debounceTimer = setTimeout(() => {
                console.log(`Input detectado en producto ${productoId}: Buscando "${busqueda}"`);
                cargarTodosLosItems(productoId, 1, busqueda); // Llamar la función después del retraso
            }, 1200); // 
        }
        
        
        // Evento para cargar productos según la línea seleccionada
        const lineaSelect = nuevoProducto.querySelector('.linea-select');
        const productoSelect = nuevoProducto.querySelector('.producto-select');

        lineaSelect.addEventListener('change', function () {
            const selectedLineaId = this.value;
            cargarProductosPorLinea(selectedLineaId, productoSelect);
        });

        productoSelect.addEventListener('change', function () {
            const selectedProductoId = this.value;
            if (!selectedProductoId) {
                lineaSelect.value = ''; // Si no se selecciona un producto, limpiar el select de líneas
                return;
            }

            const producto = productosDinamicos.find(producto => producto.id == selectedProductoId);
            if (producto) {
                lineaSelect.value = producto.linea_id; // Seleccionar automáticamente la línea correspondiente
            }
        });

        // Cargar todos los productos inicialmente
        cargarTodosLosProductos(productoSelect);

        // Agregar el producto al contenedor
        productosContainer.appendChild(nuevoProducto);

        // Mover el botón "Agregar Producto Vacío" al final de todos los productos
        actualizarBotonCrearProducto();

        // Agregar el producto a la lista de productos
        productosDinamicos.push({ id: nuevoItemNumber, producto: nuevoProducto });
        });

        // Función para eliminar el producto del array
        function eliminarProducto(productoId) {
        productosDinamicos = productosDinamicos.filter(producto => producto.id !== productoId);
        productosEliminados.push(productoId);  // Agregar el ID a la lista de eliminados
        productosEliminados.sort((a, b) => a - b);  // Asegurarnos de que estén ordenados
        }

        // Función para actualizar el botón "Agregar Producto"
        function actualizarBotonCrearProducto() {
        const productosContainer = document.getElementById('productos-container');
        const btnCrearVacio = document.getElementById('btnCrearVacio');
        productosContainer.after(btnCrearVacio); // Mover el botón justo después del contenedor de productos
        btnCrearVacio.style.display = 'block';
        }

        actualizarBotonCrearProducto();

        // Función para actualizar los valores de cantidad
        function actualizarValoresCantidad(container) {
        const cantidadInputs = container.querySelectorAll('.cantidad-input');
        const valoresCantidad = Array.from(cantidadInputs).map(input => parseInt(input.value, 10) || 1);
        console.log('Valores de cantidad:', valoresCantidad); // Puedes manejar estos valores según sea necesario
        }

        // Función para manejar el clic en el botón de agregar cantidad
        function agregarCantidad(cantidadContainer) {
        const cantidadInputs = cantidadContainer.querySelectorAll('.cantidad-input');

        // Verificar que no haya más de 5 inputs
        if (cantidadInputs.length < 5) {
            const newInput = document.createElement('input');
            newInput.type = 'number';
            newInput.className = 'cantidad-input';
            newInput.name = 'cantidadUnidades';
            newInput.min = '1';
            newInput.value = '1';
            cantidadContainer.insertBefore(newInput, cantidadContainer.querySelector('.btnAgregarCantidad'));
            actualizarValoresCantidad(cantidadContainer);
        } else {
            alert('No puedes agregar más de 5 cantidades.');
        }
        }

        // Función para manejar el clic en el botón de eliminar cantidad
        function eliminarCantidad(cantidadContainer) {
        const cantidadInputs = cantidadContainer.querySelectorAll('.cantidad-input');
        if (cantidadInputs.length > 1) {
            cantidadContainer.removeChild(cantidadInputs[cantidadInputs.length - 1]);
            actualizarValoresCantidad(cantidadContainer);
        }
        }


        function ocultarItemDeSugeridos(itemId, productoId) {
            // Ocultar en la tabla de sugeridos
            const itemRowSugeridos = document.querySelector(`#itemssugeridos-${productoId} tr[data-item-id="${itemId}"]`);
            
            if (itemRowSugeridos) {
                itemRowSugeridos.style.display = 'none'; // Ocultar la fila
                console.log(`Ítem ${itemId} oculto de sugeridos para el producto ${productoId}`);
            } else {
                console.error(`No se encontró el ítem con ID ${itemId} en la tabla de sugeridos para el producto ${productoId}`);
            }
        
            // Ocultar en la tabla de todos los ítems
            const itemRowTodos = document.querySelector(`#todositems-${productoId} tr[data-item-id="${itemId}"]`);
            
            if (itemRowTodos) {
                itemRowTodos.style.display = 'none'; // Ocultar la fila
                console.log(`Ítem ${itemId} oculto de todos los ítems para el producto ${productoId}`);
            } else {
                console.error(`No se encontró el ítem con ID ${itemId} en la tabla de todos los ítems para el producto ${productoId}`);
            }
        }
        
        

        // Función para mostrar un ítem en la tabla de sugeridos
        function mostrarItemEnSugeridos(item, productoId) {
        // Buscar el tbody de "Sugeridos" para este producto
        const tbodySugeridos = document.querySelector(`#itemssugeridos-${productoId}`);
        if (!tbodySugeridos) {
            console.error(`No se encontró la tabla de ítems sugeridos para el producto ${productoId}`);
            return;
        }

        // Verificar si el ítem ya está en la tabla de sugeridos
        const itemExistente = tbodySugeridos.querySelector(`tr[data-item-id="${item.id}"]`);
        if (itemExistente) {
            // Si ya existe, solo cambiar su estilo para hacerlo visible
            if (itemExistente.style.display === 'none') {
                itemExistente.style.display = '';  // Volver a mostrar el ítem
                console.log(`Ítem ${item.id} vuelto a mostrar en sugeridos`);
            } else {
                console.log(`El ítem ${item.id} ya está visible en la lista de sugeridos`);
            }
            return; // No lo agregamos nuevamente
        }

        // Si no existe, crear y agregar el ítem a sugeridos
        const filaSugerido = document.createElement('tr');
        filaSugerido.setAttribute('data-item-id', item.id); // Agregar el ID al atributo
        filaSugerido.innerHTML = `
            <td>${item.id}</td>
            <td>${item.descripcion}</td>
            <td>${item.unidad}</td>
            <td>${item.precio}</td>
            <td>
                <button class="btnAgregar" data-item-id="${item.id}">Agregar</button>
            </td>
        `;

        // Agregar la fila al tbody de sugeridos
        tbodySugeridos.appendChild(filaSugerido);

        console.log(`Ítem ${item.id} agregado a sugeridos`);
        }

        function formatearPesosColombianos(numero) {
            // Asegurarse de que el precio sea un número
            let precio = parseFloat(numero);
        
            // Verificar si el precio es un número válido
            if (isNaN(precio)) {
                return 'SIN PRECIO'; // En caso de que no sea un precio válido
            }
        
            // Convertir el número a una cadena con dos decimales
            const precioConDecimales = precio.toFixed(2);
        
            // Formatear el precio con puntos como separadores de miles
            const precioFormateado = precioConDecimales.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        
            return precioFormateado;
        }
        
    // Función para mover el item a la tabla de seleccionados
    function moverItemASeleccionados(itemId, productoId) {
        const tbodySeleccionados = document.getElementById(`itemsseleccionados-${productoId}`);
        if (!tbodySeleccionados) {
            console.error(`No se encontró la tabla de ítems seleccionados para el producto ${productoId}`);
            return;
        }

        fetch(`/item_detalle/${itemId}`)
            .then(response => {
                if (!response.ok) throw new Error(`Error al cargar detalles del ítem ${itemId}`);
                return response.json();
            })
            .then(item => {
                const precioUnitario = parseFloat(item.precio);
                const precioFormateado = formatearPesosColombianos(precioUnitario);
                const nuevaFilaSeleccionada = document.createElement('tr');

                nuevaFilaSeleccionada.innerHTML = `
                    <td>${item.id}</td>
                    <td>${item.descripcion}</td>
                    <td>${item.unidad}</td>
                    <td>${precioFormateado}</td>
                    <td><input type="number" class="cantidadInput" step="any" min="0.1" value="1"></td>
                    <td>${precioFormateado}</td>
                    <td><button class="btnEliminarItem" type="button">Eliminar</button></td>
                `;

                tbodySeleccionados.appendChild(nuevaFilaSeleccionada);

                // Obtener referencias a los elementos dinámicos
                const inputCantidad = nuevaFilaSeleccionada.querySelector('.cantidadInput');
                const celdaTotal = nuevaFilaSeleccionada.querySelector('td:nth-child(6)');
                const btnEliminar = nuevaFilaSeleccionada.querySelector('.btnEliminarItem');

                // Evento para actualizar el total al cambiar la cantidad
                inputCantidad.addEventListener('input', function () {
                    let cantidad = parseFloat(inputCantidad.value);
                    if (isNaN(cantidad) || cantidad < 0.1) {
                        cantidad = 0.1; // Restablecer a 0.1 si el valor no es válido
                        inputCantidad.value = cantidad;
                    }
                    const nuevoTotal = (precioUnitario * cantidad).toFixed(2);
                    celdaTotal.textContent = formatearPesosColombianos(nuevoTotal);

                    // Recalcular el costo directo cada vez que se cambia la cantidad
                    actualizarResumenCostos(productoId);
                });

                // Evento para eliminar el ítem
                btnEliminar.addEventListener('click', function () {
                    nuevaFilaSeleccionada.remove();
                    mostrarItemEnSugeridos(item, productoId);

                    // Recalcular el costo directo después de eliminar un ítem
                    actualizarResumenCostos(productoId);
                });

                console.log(`Ítem ${item.id} movido a seleccionados del producto ${productoId}`);
                
                // Actualizar el costo directo inmediatamente después de agregar el ítem
                actualizarResumenCostos(productoId);
            })
            .catch(error => {
                console.error(`Error cargando detalles del ítem: ${error.message}`);
            });
    }

    function formatearPesosColombianos(numero) {
        // Asegurarse de que el precio sea un número
        let precio = parseFloat(numero);
    
        // Verificar si el precio es un número válido
        if (isNaN(precio)) {
            return 'SIN PRECIO'; // En caso de que no sea un precio válido
        }
    
        // Redondear a la unidad más cercana
        precio = Math.round(precio); // Redondeo normal a la unidad más cercana
    
        // Formatear el precio con puntos como separadores de miles
        let precioFormateado = precio.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    
        return precioFormateado;
    }
    

    // Función para actualizar el costo directo
    function actualizarCostoDirecto(productoId) {
        const tbodySeleccionados = document.getElementById(`itemsseleccionados-${productoId}`);
        let costoDirectoTotal = 0;
    
        tbodySeleccionados.querySelectorAll('tr').forEach(fila => {
            // Extraer y limpiar el precio unitario
            const precioUnitarioTexto = fila.querySelector('td:nth-child(4)').textContent.replace(/\./g, '').replace(/[^0-9.-]+/g, '');
            const precioUnitario = parseFloat(precioUnitarioTexto);
    
            // Obtener cantidad
            const cantidadInput = fila.querySelector('.cantidadInput');
            const cantidad = parseFloat(cantidadInput.value);
    
            // Validar y sumar si los valores son válidos
            if (!isNaN(precioUnitario) && !isNaN(cantidad)) {
                costoDirectoTotal += precioUnitario * cantidad;
            }
        });
    
        // Actualizar el valor formateado en el DOM
        const costoDirectoElement = document.querySelector(`#costoDirecto-${productoId}`);
        costoDirectoElement.textContent = formatearPesosColombianos(costoDirectoTotal.toFixed(2));
    }

    // Función para actualizar el costo directo unitario
    function actualizarCostoDirectoUnitario(productoId) {
        // Obtener el costo directo
        const costoDirectoElement = document.getElementById(`costoDirecto-${productoId}`);
        const costoDirectoTexto = costoDirectoElement.textContent.replace(/\./g, '').replace(',', '.');
        const costoDirecto = parseFloat(costoDirectoTexto);
    
        // Obtener la cantidad desde el input correspondiente
        const cantidadInput = document.querySelector(`#producto-${productoId} .cantidad-input`);
        const cantidad = parseFloat(cantidadInput?.value);
    
        // Elemento donde se mostrará el costo directo unitario
        const costoDirectoUnitarioElement = document.getElementById(`costoDirectoUnitario-${productoId}`);
    
        // Validar los valores y realizar el cálculo
        if (!isNaN(costoDirecto) && !isNaN(cantidad) && cantidad > 0) {
            const costoDirectoUnitario = costoDirecto / cantidad;
            costoDirectoUnitarioElement.textContent = formatearPesosColombianos(costoDirectoUnitario.toFixed(2));
        } else {
            costoDirectoUnitarioElement.textContent = '0'; // Fallback si los datos son inválidos
        }
    }
    

    // Escuchar cambios en el input de cantidad
    document.querySelectorAll('.cantidad-input').forEach(input => {
        input.addEventListener('input', function () {
            let nuevaCantidad = parseFloat(input.value);
            if (isNaN(nuevaCantidad) || nuevaCantidad < 1) {
                nuevaCantidad = 1; // Evitar valores no válidos o menores que 1
                input.value = nuevaCantidad;
            }
            const productoId = input.closest('.resumen-costos').id.split('-')[1];
            actualizarCostoDirectoUnitario(productoId);
        });
    });

    // Actualizar el costo directo unitario cada vez que se actualice el costo directo
    function actualizarResumenCostos(productoId) {
        // Primero actualizamos los costos directos y unitarios
        actualizarCostoDirecto(productoId); // Calcula y actualiza el costo directo
        actualizarCostoDirectoUnitario(productoId); // Calcula y actualiza el costo directo unitario
        
        // Recalcular AIU usando los porcentajes cargados en el DOM
        const porcentajeAdministracion = parseFloat(document.getElementById(`porcentajeAdministracion-${productoId}`).textContent.replace('%', ''));
        const porcentajeImprevistos = parseFloat(document.getElementById(`porcentajeImprevistos-${productoId}`).textContent.replace('%', ''));
        const porcentajeUtilidad = parseFloat(document.getElementById(`porcentajeUtilidad-${productoId}`).textContent.replace('%', ''));
        
        if (!isNaN(porcentajeAdministracion) && !isNaN(porcentajeImprevistos) && !isNaN(porcentajeUtilidad)) {
            actualizarAIU(productoId, porcentajeAdministracion, porcentajeImprevistos, porcentajeUtilidad);
        } else {
            console.error(`Porcentajes inválidos para el producto ${productoId}`);
        }
        
        // Obtener valores base del DOM
        const costoDirectoElement = document.getElementById(`costoDirecto-${productoId}`);
        const administracionElement = document.getElementById(`administracion-${productoId}`);
        const imprevistosElement = document.getElementById(`imprevistos-${productoId}`);
        const utilidadElement = document.getElementById(`utilidad-${productoId}`);
        
        const costoDirecto = parseFloat(costoDirectoElement.textContent.replace(/\./g, '').replace(',', '.')) || 0;
        const administracion = parseFloat(administracionElement.textContent.replace(/\./g, '').replace(',', '.')) || 0;
        const imprevistos = parseFloat(imprevistosElement.textContent.replace(/\./g, '').replace(',', '.')) || 0;
        const utilidad = parseFloat(utilidadElement.textContent.replace(/\./g, '').replace(',', '.')) || 0;
    
        // Cálculo: Oferta Antes de IVA
        const ofertaAntesIVA = costoDirecto + administracion + imprevistos + utilidad;
        document.getElementById(`ofertaAntesIVA-${productoId}`).textContent = formatearPesosColombianos(ofertaAntesIVA.toFixed(2));
    
        // Obtener la cantidad desde el input correspondiente
        const cantidadInput = document.querySelector(`#producto-${productoId} .cantidad-input`);
        const cantidad = parseFloat(cantidadInput?.value) || 1; // Fallback a 1 si no es válido
    
        // Cálculo: Precio Unitario de Venta
        const precioUnitarioVenta = ofertaAntesIVA / cantidad;
        document.getElementById(`precioUnitarioVenta-${productoId}`).textContent = formatearPesosColombianos(precioUnitarioVenta.toFixed(2));
    
        // Cálculo: IVA (19%)
        const iva = ofertaAntesIVA * 0.19;
        document.getElementById(`iva-${productoId}`).textContent = formatearPesosColombianos(iva.toFixed(2));
    
        // Cálculo: Valor Oferta Impuestos Incluidos
        const valorOfertaImpuestos = ofertaAntesIVA + iva;
        document.getElementById(`valorOfertaImpuestos-${productoId}`).textContent = formatearPesosColombianos(valorOfertaImpuestos.toFixed(2));
    }
    // Escuchar cambios en los inputs relevantes para recalcular todo
    document.querySelectorAll('.cantidad-input').forEach(input => {
        input.addEventListener('input', function () {
            let nuevaCantidad = parseFloat(input.value);
            if (isNaN(nuevaCantidad) || nuevaCantidad < 1) {
                nuevaCantidad = 1; // Evitar valores no válidos o menores que 1
                input.value = nuevaCantidad;
            }
            const productoId = input.closest('.resumen-costos').id.split('-')[1];
            actualizarResumenCostos(productoId);
        });
    });
    
    

    function obtenerYMostrarPorcentajes(productoCotizacionId, productoId) {
        console.log(`Obteniendo porcentajes para el producto real con ID: ${productoId}`);
        
        fetch(`/porcentajes/${productoId}`)
            .then(response => response.json())
            .then(data => {
                if (data.administracion && data.imprevistos && data.utilidad) {
                    // Actualizamos los porcentajes en el DOM del producto de la cotización
                    document.getElementById(`porcentajeAdministracion-${productoCotizacionId}`).textContent = `${data.administracion}%`;
                    document.getElementById(`porcentajeImprevistos-${productoCotizacionId}`).textContent = `${data.imprevistos}%`;
                    document.getElementById(`porcentajeUtilidad-${productoCotizacionId}`).textContent = `${data.utilidad}%`;
    
                    // Actualizamos los valores de administración, imprevistos y utilidad en el DOM
                    actualizarAIU(productoCotizacionId, data.administracion, data.imprevistos, data.utilidad);
                } else {
                    console.error('No se encontraron los porcentajes para el producto real');
                }
            })
            .catch(error => {
                console.error('Error al obtener los porcentajes:', error);
            });
    }
    
    function limpiarPorcentajes(productoCotizacionId) {
        document.getElementById(`porcentajeAdministracion-${productoCotizacionId}`).textContent = '%';
        document.getElementById(`porcentajeImprevistos-${productoCotizacionId}`).textContent = '%';
        document.getElementById(`porcentajeUtilidad-${productoCotizacionId}`).textContent = '%';
        // También se puede limpiar otros campos relacionados si es necesario
    }

    function actualizarAIU(productoId, porcentajeAdministracion, porcentajeImprevistos, porcentajeUtilidad) {
        // Obtener el costo directo del DOM
        const costoDirectoElement = document.getElementById(`costoDirecto-${productoId}`);
        const costoDirectoTexto = costoDirectoElement.textContent.replace(/\./g, '').replace(',', '.');
        const costoDirecto = parseFloat(costoDirectoTexto);
    
        if (isNaN(costoDirecto) || costoDirecto <= 0) {
            console.error(`Costo directo inválido para el producto ${productoId}`);
            return;
        }
    
        // Calcular los valores de administración, imprevistos y utilidad
        const administracion = (costoDirecto * porcentajeAdministracion) / 100;
        const imprevistos = (costoDirecto * porcentajeImprevistos) / 100;
        const utilidad = (costoDirecto * porcentajeUtilidad) / 100;
    
        // Actualizar los valores en el DOM
        document.getElementById(`administracion-${productoId}`).textContent = formatearPesosColombianos(administracion.toFixed(2));
        document.getElementById(`imprevistos-${productoId}`).textContent = formatearPesosColombianos(imprevistos.toFixed(2));
        document.getElementById(`utilidad-${productoId}`).textContent = formatearPesosColombianos(utilidad.toFixed(2));
    }


        /* NO HEMOS MODIFICADO MÁS ABAJO*/


  



        document.addEventListener('DOMContentLoaded', function() {
        actualizarNumeroProducto();
        });


        function actualizarResumenesDeCostos() {
        document.querySelectorAll('.producto').forEach(producto => {
            const productoId = producto.id.split('-')[1];
            actualizarTotalProducto(productoId);
        });
        }

        function editarProducto(productoId) {
        const productoDiv = document.getElementById(`producto-${productoId}`);

        // Convertir el h4 de descripción a un textarea editable
        const descripcionElement = productoDiv.querySelector('h4:nth-child(2)');
        const descripcionTexto = descripcionElement.textContent.replace("Descripción: ", "");
        descripcionElement.innerHTML = `<textarea>${descripcionTexto}</textarea>`;

        // Convertir los campos de medidas a inputs
        const medidasElement = productoDiv.querySelector('h4:nth-child(3)');
        const [alto, ancho, fondo] = medidasElement.textContent.split(' || ').map(texto => texto.split(': ')[1]);
        medidasElement.innerHTML = `
            <label>Alto (Cm):</label><input type="number" value="${alto}">
            <label>Ancho (Cm):</label><input type="number" value="${ancho}">
            <label>Fondo (Cm):</label><input type="number" value="${fondo}">
        `;
        }



        function toggleFormulario(numeroProducto) {
        const formulario = document.getElementById(`formAgregarItem-${numeroProducto}`);
        if (formulario.style.display === 'none' || formulario.style.display === '') {
            formulario.style.display = 'block';
        } else {
            formulario.style.display = 'none';
        }
        }


                // Función para agregar ítems temporales
                function agregarItemTemporal(productoId) {
                    const descripcion = document.getElementById(`nuevo-item-descripcion-${productoId}`).value.trim();
                    const precioInput = document.getElementById(`nuevo-item-precio-${productoId}`).value.trim();
                
                    // Convertir el precio a formato numérico
                    const precio = parseFloat(precioInput.replace(/\./g, '').replace(/,/g, '.'));
                
                    if (isNaN(precio)) {
                        alert("El precio ingresado no es válido. Asegúrese de usar el formato correcto.");
                        return;
                    }
                
                    const cantidad = parseInt(document.getElementById(`nuevo-item-cantidad-${productoId}`).value.trim(), 10);
                    
                    // Agregar el proveedor aquí
                    const proveedor = document.getElementById(`nuevo-item-proveedor-${productoId}`).value.trim();
                
                    if (!descripcion || isNaN(precio) || isNaN(cantidad) || cantidad <= 0 || !productoId || !proveedor) {
                        alert("Por favor, ingrese una descripción, precio, cantidad, proveedor y seleccione un producto.");
                        return;
                    }
                
                    // Asignar un itemId único temporal
                    const itemId = Date.now(); // Usar timestamp como identificador único temporal
                
                    // Agregar el ítem al contenedor del producto
                    const contenedor = document.getElementById(`itemsseleccionados-${productoId}`);
                
                    // Generar las celdas de cantidad y total dinámicamente
                    const valoresCantidad = [cantidad];
                    const cantidadCeldas = valoresCantidad.map((valor, i) => 
                        `<td><input type="number" min="1" value="${valor}" class="cantidad" data-index="${i}" onchange="actualizarTotalProducto(${productoId})" style="width: 70px;"></td>`
                    ).join('');
                
                    const totalCeldas = valoresCantidad.map(() => 
                        `<td class="total">0</td>`
                    ).join('');
                
                    const nuevaFila = document.createElement('tr');
                    nuevaFila.innerHTML = `
                        <td class="oculto">${itemId}</td>
                        <td class="oculto">Temporales</td>
                        <td>${descripcion}</td>
                        <td>Unidad</td>
                        <td>${formatearNumero(precio)}</td>
                        ${cantidadCeldas} <!-- Aquí se generan los td de cantidad -->
                        ${totalCeldas}    <!-- Aquí se generan los td de total -->
                        <td class="oculto">${proveedor}</td> <!-- Campo oculto para el proveedor -->
                        <td class="oculto">Temporal</td>
                        <td><button onclick="eliminarItemTemporal(this, ${itemId}, ${productoId})">Eliminar</button></td>
                    `;
                    contenedor.appendChild(nuevaFila);
                
                    limpiarFormularioTemporal(productoId);
                    // Actualizar total del producto
                    actualizarTotalProducto(productoId);
                }
                
                
                
                
                function limpiarFormularioTemporal(productoId) {
                    document.getElementById(`nuevo-item-descripcion-${productoId}`).value = '';
                    document.getElementById(`nuevo-item-precio-${productoId}`).value = '';
                    document.getElementById(`nuevo-item-cantidad-${productoId}`).value = '1';
                }
                
                
                

            

        // Función para ocultar un ítem de la tabla de sugeridos
 
        function actualizarNumeroProducto() {
            const itemNumberDiv = document.getElementById('itemNumber');
            if (itemNumberDiv) {
                if (numerosEliminados.length > 0) {
                    itemNumberDiv.textContent = Math.min(...numerosEliminados).toString();
                } else {
                    itemNumberDiv.textContent = (itemNumber + 1).toString();
                }
            }
        }


        function calcularPrecioUnitario(preciosEscalonados, cantidad) {
            // Encuentra el precio unitario adecuado basado en la cantidad
            for (const escalonado of preciosEscalonados) {
                if (cantidad >= escalonado.min_cantidad && (escalonado.max_cantidad === 0 || cantidad <= escalonado.max_cantidad)) {
                    return parseFloat(escalonado.precio_unitario.replace(/\./g, '').replace(/,/g, '.'));
                }
            }
            return 0; // Precio por defecto si no se encuentra el rango adecuado
        }

        function actualizarTotalProducto(itemNumber) {
            const contenedores = [
                document.getElementById(`materiaprima-${itemNumber}`),
                document.getElementById(`consumibles-${itemNumber}`),
                document.getElementById(`servicios-${itemNumber}`),
                document.getElementById(`manodeobra-${itemNumber}`),
                document.getElementById(`transporte-${itemNumber}`),
                document.getElementById(`itemsseleccionados-${itemNumber}`)
            ];

            const subtotalPorCantidad = Array(valoresCantidad.length).fill(0);

            contenedores.forEach(container => {
                if (container) {
                    const filas = container.querySelectorAll('tr');
                    filas.forEach(fila => {
                        const precioElement = fila.querySelector('td:nth-child(5)');
                        const cantidadInputs = fila.querySelectorAll('input.cantidad');

                        const preciosEscalonados = JSON.parse(fila.getAttribute('data-precios-escalonados') || '[]');

                        if (precioElement && cantidadInputs.length > 0) {
                            let precio = parseFloat(precioElement.textContent.trim().replace(/\./g, '').replace(/,/g, '.'));

                            if (preciosEscalonados.length > 0) {
                                cantidadInputs.forEach((input, index) => {
                                    const cantidad = parseFloat(input.value.trim()) || 0;
                                    const precioEscalonado = preciosEscalonados.find(pe => cantidad >= pe.min_cantidad && (cantidad <= pe.max_cantidad || pe.max_cantidad === 0));

                                    if (precioEscalonado) {
                                        precio = parseFloat(precioEscalonado.precio_unitario);
                                    }

                                    const subtotal = precio * cantidad;
                                    const totalElement = fila.querySelectorAll('.total')[index];
                                    if (totalElement) {
                                        totalElement.textContent = formatearNumero(subtotal);
                                    }
                                    subtotalPorCantidad[index] += subtotal;
                                });
                            } else {
                                cantidadInputs.forEach((input, index) => {
                                    const cantidad = parseFloat(input.value.trim()) || 0;
                                    const subtotal = precio * cantidad;
                                    const totalElement = fila.querySelectorAll('.total')[index];
                                    if (totalElement) {
                                        totalElement.textContent = formatearNumero(subtotal);
                                    }
                                    subtotalPorCantidad[index] += subtotal;
                                });
                            }
                        }
                    });
                }
            });

            const cantidadInputs = document.querySelectorAll('#cantidadUnidades .cantidad-input');
            cantidadInputs.forEach((input, index) => {
                const cantidadUnidades = parseFloat(input.value) || 1;
                
                // Buscar cuál input de utilidad está activo: porcentaje o valor manual
                const metodoUtilidad = document.querySelector(`input[name="opcionUtilidad-${itemNumber}-${index}"]:checked`).value;

                let nuevoValorUtilidad = null;

                if (metodoUtilidad === 'porcentaje') {
                    const utilidadInputPorcentaje = document.getElementById(`utilidadPorcentaje-${itemNumber}-${index}`);
                    nuevoValorUtilidad = utilidadInputPorcentaje ? parseFloat(utilidadInputPorcentaje.value) || null : null;
                } else if (metodoUtilidad === 'manual') {
                    const utilidadInputValor = document.getElementById(`utilidadValor-${itemNumber}-${index}`);
                    nuevoValorUtilidad = utilidadInputValor ? parseFloat(utilidadInputValor.value) || null : null;
                }

                if (nuevoValorUtilidad !== null) {
                    actualizarTotalesExtras(itemNumber, subtotalPorCantidad[index], nuevoValorUtilidad, cantidadUnidades, index);
                } else {
                    console.warn(`Utilidad seleccionada no encontrada para ${itemNumber}-${index}`);
                }
            });
        }

        // Llamada para actualizar todos los resúmenes de costos cuando se modifiquen los items
/*         function actualizarResumenDeCostos(productoId) {
            
            const productoElement = document.getElementById(`producto-${productoId}`);
            if (productoElement) {
                const costoDirecto = calcularCostoDirecto(productoId);
                const costoUnitario = calcularCostoUnitario(productoId);
                const administracion = calcularAdministracion(productoId);
                const imprevistos = calcularImprevistos(productoId);
                const utilidad = calcularUtilidad(productoId);
                const ofertaAntesIVA = calcularOfertaAntesIVA(productoId);
                const iva = calcularIVA(productoId);
                const valorOferta = calcularValorOferta(productoId);

                const resumenCostos = document.querySelector(`#resumen-costos-${productoId}`);
                if (resumenCostos) {
                    resumenCostos.querySelector(`#costo-directo-${productoId}`).textContent = `Costo Directo: ${costoDirecto}`;
                    resumenCostos.querySelector(`#costo-unitario-${productoId}`).textContent = `Costo Directo Unitario: ${costoUnitario}`;
                    resumenCostos.querySelector(`#administracion-${productoId}`).textContent = `Administración: ${administracion}`;
                    resumenCostos.querySelector(`#imprevistos-${productoId}`).textContent = `Imprevistos: ${imprevistos}`;
                    resumenCostos.querySelector(`#utilidad-${productoId}`).textContent = `Utilidad: ${utilidad}`;
                    resumenCostos.querySelector(`#oferta-antes-iva-${productoId}`).textContent = `Oferta Antes De IVA: ${ofertaAntesIVA}`;
                    resumenCostos.querySelector(`#iva-${productoId}`).textContent = `IVA: ${iva}`;
                    resumenCostos.querySelector(`#valor-oferta-${productoId}`).textContent = `Valor Oferta Impuestos Incluidos: ${valorOferta}`;
                    
                } else {
                    console.log(`No se encontró el resumen de costos para producto ${productoId}`);
                }
            } else {
                console.log(`No se encontró el producto para ID ${productoId}`);
            }
        }
 */
            
            
            function calcularPorcentaje(valor, porcentaje) {
                return (valor * porcentaje) / 100;
            }

            function calcularPorcentajeDesdeValorManual(costoDirecto, valorUtilidad) {
                if (costoDirecto > 0) {
                    return (valorUtilidad / costoDirecto) * 100;
                }
                return 0; // Evitar división por cero
            }
            
            // Calcular el porcentaje desde un valor manual
        function calcularPorcentajeDesdeValorManual(costoDirecto, valorUtilidad) {
        return (valorUtilidad / costoDirecto) * 100;
        }

        // Calcular el valor de la utilidad desde un porcentaje
        function calcularValorDesdePorcentaje(costoDirecto, porcentajeUtilidad) {
        return (costoDirecto * porcentajeUtilidad) / 100;
        }


            function actualizarTotalesExtras(itemNumber, costoDirecto, nuevoValorUtilidad = null, cantidadUnidades, index) {
                const productoElement = document.querySelector(`#producto-${itemNumber}`);
                if (productoElement) {
                    const administracionPorcentaje = parseFloat(productoElement.dataset.administracion);
                    const imprevistosPorcentaje = parseFloat(productoElement.dataset.imprevistos);
                    const porcentajeUtilidadMinimo = parseFloat(productoElement.dataset.utilidad); // Porcentaje mínimo de utilidad
            
                    let utilidadPorcentajeBase = parseFloat(productoElement.dataset.utilidad);
                    let utilidadPorcentaje = utilidadPorcentajeBase;
                    
                    // Verificación y cálculo del porcentaje de utilidad
                    if (nuevoValorUtilidad !== null) {
                        const opcionUtilidad = document.querySelector(`input[name="opcionUtilidad-${itemNumber}-${index}"]:checked`).value;
            
                        if (opcionUtilidad === 'manual') {
                            // Caso de valor manual: recalcular el porcentaje a partir del valor ingresado
                            utilidadPorcentaje = calcularPorcentajeDesdeValorManual(costoDirecto, nuevoValorUtilidad);
                            
                            if (utilidadPorcentaje < porcentajeUtilidadMinimo) {
                                // Si el porcentaje calculado es menor al mínimo, mostrar alerta y usar el porcentaje mínimo
                                alert(`El valor ingresado genera una utilidad menor al porcentaje mínimo permitido (${porcentajeUtilidadMinimo}%). Se ajustará al valor mínimo.`);
                                utilidadPorcentaje = porcentajeUtilidadMinimo;
                                nuevoValorUtilidad = calcularValorDesdePorcentaje(costoDirecto, utilidadPorcentaje);
                            }
                        } else {
                            // Caso de porcentaje ingresado directamente
                            utilidadPorcentaje = nuevoValorUtilidad;
            
                            if (utilidadPorcentaje < porcentajeUtilidadMinimo) {
                                // Si el porcentaje ingresado es menor al mínimo, mostrar alerta y ajustar
                                alert(`El porcentaje de utilidad ingresado es menor al porcentaje mínimo permitido (${porcentajeUtilidadMinimo}%). Se ajustará al mínimo.`);
                                utilidadPorcentaje = porcentajeUtilidadMinimo;
                            }
                        }
                    }
            
                    // Ahora que tenemos el porcentaje válido, calculamos los valores relacionados
                    const administracion = calcularPorcentaje(costoDirecto, administracionPorcentaje);
                    const imprevistos = calcularPorcentaje(costoDirecto, imprevistosPorcentaje);
                    const utilidad = calcularPorcentaje(costoDirecto, utilidadPorcentaje);
            
                    // Cálculo de la oferta antes de IVA
                    const ofertaAntesIva = costoDirecto + administracion + imprevistos + utilidad;
                    const iva = calcularPorcentaje(ofertaAntesIva, 19);
                    const valorOferta = ofertaAntesIva + iva;
                    const costoUnitario = costoDirecto / cantidadUnidades;
                    const precioUnitarioVenta = ofertaAntesIva / cantidadUnidades;
            
                    // Sumar los porcentajes
                    const sumaPorcentajes = administracionPorcentaje + imprevistosPorcentaje + utilidadPorcentaje;
            
                    // Actualizar los valores en la interfaz
                    document.getElementById(`costo-directo-${itemNumber}-${index}`).textContent = `Costo Directo: ${formatearNumero(costoDirecto)}`;
                    document.getElementById(`costo-unitario-${itemNumber}-${index}`).textContent = `Costo Directo Unitario: ${formatearNumero(costoUnitario)}`;
                    document.getElementById(`administracion-${itemNumber}-${index}`).innerHTML = `Administración: ${formatearNumero(administracion)} <span id="porcentaje-administracion-${itemNumber}-${index}">(${administracionPorcentaje}%)</span>`;
                    document.getElementById(`imprevistos-${itemNumber}-${index}`).innerHTML = `Imprevistos: ${formatearNumero(imprevistos)} <span id="porcentaje-imprevistos-${itemNumber}-${index}">(${imprevistosPorcentaje}%)</span>`;
                    document.getElementById(`utilidad-${itemNumber}-${index}`).innerHTML = `Utilidad: ${formatearNumero(utilidad)} <span id="porcentaje-utilidad-${itemNumber}-${index}">(${formatearNumero(utilidadPorcentaje)}%)</span>`;
                    document.getElementById(`oferta-antes-iva-${itemNumber}-${index}`).innerHTML = `Oferta Antes De IVA: ${formatearNumero(ofertaAntesIva)} <span style="color: #00b04f;">(${sumaPorcentajes}%)</span>`;
                    document.getElementById(`iva-${itemNumber}-${index}`).textContent = `IVA: ${formatearNumero(iva)}`;
                    document.getElementById(`valor-oferta-${itemNumber}-${index}`).textContent = `Valor Oferta Impuestos Incluidos: ${formatearNumero(valorOferta)}`;
                    document.getElementById(`precio-unitario-venta-${itemNumber}-${index}`).textContent = `Precio Unitario De Venta: ${formatearNumero(precioUnitarioVenta)}`;
                } else {
                    console.error('Error: Elemento del producto no encontrado');
                }
            }
            
            
            
            function cambiarMetodoUtilidad(itemNumber, index, metodo) {
                // Al cambiar el método, recalcular los totales
                actualizarTotalesExtras(itemNumber, calcularCostoDirecto(itemNumber), null, obtenerCantidadUnidades(itemNumber), index);
            }
            
            
            
            
            function formatearNumero(numero) {
                return numero.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            }
            
            
        function mostrarNotificacion(mensaje, tipo) {
            const notificacion = document.createElement('div');
            notificacion.className = `notificacion ${tipo}`;
            notificacion.textContent = mensaje;
            document.body.appendChild(notificacion);
            setTimeout(() => {
                notificacion.remove();
            }, 3000);
        }

        function mostrarNotificacion(itemDescripcion){
            const notificacion = document.createElement('div');

        }

        function eliminarItemSeleccionado(button) {
            const fila = button.closest('tr');
            const itemNumber = fila.closest('tbody').id.split('-')[1];
            fila.remove();
            actualizarTotalProducto(itemNumber); // Actualizar el total del producto después de eliminar el ítem
        }

        function eliminarItemTemporal(button, itemId, itemNumber) {
            // Encuentra la fila del ítem temporal que se va a eliminar
            const fila = button.closest('tr');
            if (fila) {
                // Elimina la fila del contenedor de ítems temporales
                fila.remove();
                // Actualiza el total del producto después de eliminar el ítem
                actualizarTotalProducto(itemNumber);
            } else {
                console.error('Error: Fila no encontrada');
            }
        }



        let isLoading = false;




        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('guardarCotizacionBtn').addEventListener('click', function() {
                // Capturar datos generales de la cotización
                const formData = new FormData();
                const fechaCotizacion = new Date().toISOString(); // Fecha y hora en formato ISO 8601

                // Captura otros datos
                formData.append('fechaCotizacion', fechaCotizacion);
                formData.append('clienteCotizacion', document.getElementById('cliente_cotizacion').value.trim());
                formData.append('contactoCotizacion', document.getElementById('contacto_cotizacion').value.trim());
                formData.append('proyectoCotizacion', document.getElementById('proyecto_cotizacion').value.trim());
                formData.append('vendedorCotizacion', document.getElementById('vendedor_cotizacion').value.trim());
                formData.append('negociacion', document.getElementById('negociacion').value.trim());
                formData.append('formaPago', document.getElementById('forma_pago').value.trim());
                formData.append('validezCotizacion', document.getElementById('validez_cotizacion').value.trim());

                // Captura el descuento y verifica si es null o vacío
                let descuentoCotizacion = document.getElementById('descuento_cotizacion').value.trim();
                descuentoCotizacion = descuentoCotizacion === '' || isNaN(descuentoCotizacion) ? 0 : parseFloat(descuentoCotizacion);
                formData.append('descuentoCotizacion', descuentoCotizacion);

                formData.append('ivaSeleccionado', document.getElementById('iva-select').value.trim());

                // Validar campos esenciales
                if (!formData.get('clienteCotizacion') || !formData.get('contactoCotizacion') || !formData.get('proyectoCotizacion') || !formData.get('vendedorCotizacion') || !formData.get('negociacion')) {
                    alert("Por favor, complete todos los campos obligatorios: Cliente, Contacto, Proyecto, Vendedor y Negociación.");
                    return;
                }

                // Capturar productos en la cotización
                const productos = [];
                const productoIdsCapturados = new Set();

                document.querySelectorAll('.producto').forEach(function(productoDiv) {
                    const productoId = productoDiv.id.split('-')[1];
                    if (productoIdsCapturados.has(productoId)) return;
                    productoIdsCapturados.add(productoId);

                    const productoSeleccionadoId = productoDiv.querySelector('input[name="producto_seleccionado_id"]').value;
                    const descripcionRaw = productoDiv.querySelector('h4').innerText;
                    const descripcion = descripcionRaw.replace(/^Descripción:\s*/, '').trim();
                    const medidasText = productoDiv.querySelector('h4:nth-of-type(2)').innerText;
                    const medidasMatch = medidasText.match(/Alto \(Cm\): (\d+) \|\| Ancho \(Cm\): (\d+) \|\| Fondo \(Cm\): (\d+)/);
                    const alto = medidasMatch ? parseFloat(medidasMatch[1]) : null;
                    const ancho = medidasMatch ? parseFloat(medidasMatch[2]) : null;
                    const fondo = medidasMatch ? parseFloat(medidasMatch[3]) : null;

                    const cantidadesSeleccionadas = [];
                    productoDiv.querySelectorAll('h4').forEach(function(cantidadH4) {
                        const cantidadText = cantidadH4.innerText;
                        const cantidadMatch = cantidadText.match(/Cantidad seleccionada \(\d+\): (\d+) unidades/);
                        if (cantidadMatch) {
                            cantidadesSeleccionadas.push(parseInt(cantidadMatch[1]));
                        }
                    });

                    const items = [];
                    productoDiv.querySelectorAll('tbody tr').forEach(function(itemRow) {
                        const cantidadInput = itemRow.querySelector('input[type="number"]');
                        if (cantidadInput) {
                            const itemId = itemRow.querySelector('td:nth-child(1)').innerText.trim();
                            const itemCantidad = cantidadInput.value;
                            const itemTotalText = itemRow.querySelector('td.total').innerText.trim();

                            // Reemplazar separadores de miles y cambiar coma por punto decimal
                            const itemTotal = parseFloat(itemTotalText.replace(/\./g, '').replace(',', '.'));

                            items.push({
                                itemId: parseInt(itemId),
                                itemCantidad: parseFloat(itemCantidad),
                                itemTotal: itemTotal
                            });
                        }
                    });

                    const resúmenesCostos = [];
                    productoDiv.querySelectorAll('.resumen-costos-individual').forEach(function(resumenDiv, index) {
                        const costoDirectoElement = resumenDiv.querySelector(`#costo-directo-${productoId}-${index}`);
                        const administracionElement = resumenDiv.querySelector(`#administracion-${productoId}-${index}`);
                        const imprevistosElement = resumenDiv.querySelector(`#imprevistos-${productoId}-${index}`);
                        const utilidadElement = resumenDiv.querySelector(`#utilidad-${productoId}-${index}`);
                        const ofertaAntesIvaElement = resumenDiv.querySelector(`#oferta-antes-iva-${productoId}-${index}`);
                        const ivaElement = resumenDiv.querySelector(`#iva-${productoId}-${index}`);
                        const valorOfertaElement = resumenDiv.querySelector(`#valor-oferta-${productoId}-${index}`);

                        if (costoDirectoElement && administracionElement && imprevistosElement && utilidadElement &&
                            ofertaAntesIvaElement && ivaElement && valorOfertaElement) {

                            const costoDirecto = parseFloat(costoDirectoElement.innerText.split(': ')[1].replace(/\./g, '').replace(',', '.'));
                            const administracion = parseFloat(administracionElement.innerText.split(': ')[1].replace(/\./g, '').replace(',', '.'));
                            const imprevistos = parseFloat(imprevistosElement.innerText.split(': ')[1].replace(/\./g, '').replace(',', '.'));
                            const utilidad = parseFloat(utilidadElement.innerText.split(': ')[1].replace(/\./g, '').replace(',', '.'));
                            const ofertaAntesIva = parseFloat(ofertaAntesIvaElement.innerText.split(': ')[1].replace(/\./g, '').replace(',', '.'));
                            const iva = parseFloat(ivaElement.innerText.split(': ')[1].replace(/\./g, '').replace(',', '.'));
                            const valorOferta = parseFloat(valorOfertaElement.innerText.split(': ')[1].replace(/\./g, '').replace(',', '.'));

                            resúmenesCostos.push({
                                costoDirecto: costoDirecto,
                                administracion: administracion,
                                imprevistos: imprevistos,
                                utilidad: utilidad,
                                ofertaAntesIva: ofertaAntesIva,
                                iva: iva,
                                valorOferta: valorOferta
                            });
                        } else {
                            console.error(`Algunos elementos de resumen no se encontraron para el producto ${productoId} y resumen ${index}.`);
                        }
                    });

                    productos.push({
                        productoId: parseInt(productoId),
                        productoSeleccionadoId: parseInt(productoSeleccionadoId),
                        descripcion: descripcion.trim(),
                        alto: alto,
                        ancho: ancho,
                        fondo: fondo,
                        cantidadesSeleccionadas: cantidadesSeleccionadas,
                        items: items,
                        resúmenesCostos: resúmenesCostos
                    });

                    // Agregar archivo de imagen si se ha cargado
                    const inputFile = productoDiv.querySelector(`input[type="file"]`);
                    if (inputFile && inputFile.files.length > 0) {
                        formData.append(`imagenProducto-${productoId}`, inputFile.files[0]); // Usar un nombre único para cada producto
                    }
                });

                formData.append('productos', JSON.stringify(productos)); // Agregar productos a FormData

                // Capturar items temporales en la cotización
                const itemsTemporales = [];

                document.querySelectorAll('tbody[id^="itemsseleccionados-"]').forEach(function(itemTemporalTbody) {
                    const productoId = itemTemporalTbody.id.split('-')[1]; // Extrae el ID del producto
                
                    itemTemporalTbody.querySelectorAll('tr').forEach(function(itemRow) {
                        const itemDescripcion = itemRow.querySelector('td:nth-child(3)').innerText.trim();
                        const itemUnidad = itemRow.querySelector('td:nth-child(4)').innerText.trim();
                        const itemPrecioUnitarioText = itemRow.querySelector('td:nth-child(5)').innerText.trim();
                        const itemCantidad = parseFloat(itemRow.querySelector('input[type="number"]').value.trim());
                        const itemProveedor = itemRow.querySelector('td:nth-child(8)').innerText.trim(); // Proveedor - corregido a la celda 8
                        const itemTotalText = itemRow.querySelector('td.total').innerText.trim(); // Total - asegúrate que sea la celda correcta
                
                        // Reemplazar separadores de miles y cambiar coma por punto decimal
                        const itemPrecioUnitario = parseFloat(itemPrecioUnitarioText.replace(/\./g, '').replace(',', '.'));
                        const itemTotal = parseFloat(itemTotalText.replace(/\./g, '').replace(',', '.'));
                
                        itemsTemporales.push({
                            descripcion: itemDescripcion,
                            unidad: itemUnidad,  
                            precioUnitario: itemPrecioUnitario,
                            cantidad: itemCantidad,
                            total: itemTotal,
                            proveedor: itemProveedor, // Proveedor ahora está correcto
                            productoId: parseInt(productoId)  
                        });
                    });
                });
                
                formData.append('itemsTemporales', JSON.stringify(itemsTemporales)); // Agregar los items temporales a FormData
                


                // Aquí va el nuevo código para ver lo que contiene el FormData
                console.log('Mostrando datos de FormData:');
                formData.forEach((value, key) => {
                    console.log(key + ': ' + value);
                });


                fetch('/guardar-cotizacion', {
                    method: 'POST',
                    body: formData // Enviar el FormData
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Cotización guardada exitosamente:', data);
                    if (data.success) {
                        alert('Cotización guardada con éxito.');
                        //window.location.href = '/listar_cotizaciones';
                    } else {
                        alert('Error al guardar la cotización.');
                    }
                })
                .catch(error => {
                    console.error('Error al guardar la cotización:', error);
                });
            });
        });



        // Declarar debounceTimeout en un ámbito superior
        let debounceTimeout;

        function debounceBuscar(event, productoId) {
        // Limpiar el timeout previo
        clearTimeout(debounceTimeout);

        // Asignar un nuevo timeout
        debounceTimeout = setTimeout(() => {
            const busqueda = event.target.value.trim(); // Obtener valor del input
            cargarTodosLosItems(productoId, 1, busqueda); // Llamar a la función con el término de búsqueda
        }, 300); // Esperar 300 ms antes de ejecutar
        }

});
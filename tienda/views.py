from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Producto, Categoria, Venta, DetalleVenta, Reseña, Proveedor
from django.db import transaction
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
# Utilidad para verificar si un usuario es administrador
def is_admin(user):
    return user.is_superuser

# Home para administrador
@login_required
@user_passes_test(is_admin)
def admin_home(request):
    return render(request, 'admin/home.html', {
        'titulo': 'Panel Administrativo',
    })

# Home para cliente
@login_required
def cliente_home(request):
    return render(request, 'cliente/home.html', {
        'titulo': 'Inicio del Cliente',
    })

# Listar productos con búsqueda, filtro y paginación
@login_required
@user_passes_test(is_admin)
def listar_productos(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria_id')
    sort_by = request.GET.get('sort_by', 'nombre')
    categorias = Categoria.objects.all()

    productos_list = Producto.objects.all()
    if query:
        productos_list = productos_list.filter(nombre__icontains=query)
    if categoria_id:
        productos_list = productos_list.filter(categoria_id=categoria_id)

    if sort_by in ['nombre', '-nombre', 'precio', '-precio', 'stock', '-stock']:
        productos_list = productos_list.order_by(sort_by)

    paginator = Paginator(productos_list, 5)
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)

    return render(request, 'productos/listar_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categoria_id': categoria_id,
        'sort_by': sort_by,
    })

# Crear producto
@login_required
@user_passes_test(is_admin)
def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        categoria_id = request.POST.get('categoria_id')
        imagen = request.FILES.get('imagen')  # Obtén el archivo de la imagen

        categoria = get_object_or_404(Categoria, id=categoria_id)

        Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria=categoria,
            imagen=imagen  # Guarda la imagen
        )
        messages.success(request, "Producto creado exitosamente.")
        return redirect('listar_productos')

    categorias = Categoria.objects.all()
    return render(request, 'productos/crear_producto.html', {'categorias': categorias})

# Editar producto
@login_required
@user_passes_test(is_admin)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion')
        producto.precio = request.POST.get('precio')
        producto.stock = request.POST.get('stock')
        categoria_id = request.POST.get('categoria_id')
        producto.categoria = get_object_or_404(Categoria, id=categoria_id)
        producto.save()
        messages.success(request, f"Producto '{producto.nombre}' actualizado exitosamente.")
        return redirect('listar_productos')

    categorias = Categoria.objects.all()
    return render(request, 'productos/editar_producto.html', {
        'producto': producto,
        'categorias': categorias,
    })

# Eliminar producto
@login_required
@user_passes_test(is_admin)
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, f"Producto '{producto.nombre}' eliminado exitosamente.")
        return redirect('listar_productos')

    return render(request, 'productos/eliminar_producto.html', {'producto': producto})

# Ver detalle de producto
@login_required
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'productos/detalle_producto.html', {'producto': producto})

# Estadísticas de productos
@login_required
@user_passes_test(is_admin)
def estadisticas_productos(request):
    productos_bajo_stock = Producto.objects.filter(stock__lte=10).order_by('stock')[:5]
    ventas_por_categoria = Producto.objects.values('categoria__nombre').annotate(
        total_stock=Sum('stock')
    ).order_by('-total_stock')

    context = {
        'productos_bajo_stock': productos_bajo_stock,
        'ventas_por_categoria': ventas_por_categoria,
    }

    return render(request, 'productos/estadisticas.html', context)

# Login de usuarios
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_home')
        else:
            return redirect('home_cliente')  # Cambiado de 'cliente_home' a 'home_cliente'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                messages.success(request, f"¡Bienvenido, administrador {user.username}!")
                return redirect('admin_home')
            else:
                messages.success(request, f"¡Bienvenido, {user.username}!")
                return redirect('home_cliente')  # Cambiado de 'cliente_home' a 'home_cliente'
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')

    return render(request, 'auth/login.html')
# Logout de usuarios
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

# Registro de usuarios
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Cuenta creada exitosamente. ¡Ahora puedes iniciar sesión!')
        return redirect('login')

    return render(request, 'auth/register.html')

# Añadir producto al carrito
def agregar_al_carrito(request, producto_id):
    # Verificar que el método sea POST
    if request.method == "POST":
        carrito = request.session.get('carrito', {})  # Obtener el carrito actual
        producto = get_object_or_404(Producto, id=producto_id)  # Obtener el producto

        # Agregar el producto al carrito o incrementar la cantidad
        if str(producto_id) in carrito:
            if producto.stock > 0:  # Verificar stock
                carrito[str(producto_id)]['cantidad'] += 1
                carrito[str(producto_id)]['subtotal'] = float(carrito[str(producto_id)]['cantidad'] * producto.precio)
                producto.stock -= 1  # Reducir el stock del producto
                producto.save()
                messages.success(request, f"Se agregó otra unidad de {producto.nombre} al carrito.")
            else:
                messages.error(request, "El producto está agotado.")
        else:
            if producto.stock > 0:  # Verificar stock
                carrito[str(producto_id)] = {
                    'nombre': producto.nombre,
                    'precio': float(producto.precio),
                    'cantidad': 1,
                    'subtotal': float(producto.precio),
                    'imagen': producto.imagen.url if producto.imagen else None,
                }
                producto.stock -= 1  # Reducir el stock del producto
                producto.save()
                messages.success(request, f"{producto.nombre} se agregó al carrito.")
            else:
                messages.error(request, "El producto está agotado y no se puede agregar al carrito.")

        # Guardar el carrito actualizado en la sesión
        request.session['carrito'] = carrito
        return redirect('home_cliente')
    else:
        messages.error(request, "Acción no permitida.")
        return redirect('home_cliente')
#Ver Carrito
def ver_carrito(request):
    """
    Muestra los productos en el carrito de compras.
    Calcula los subtotales por producto y el total general.
    Maneja productos eliminados de la base de datos.
    """
    carrito = request.session.get('carrito', {})
    total = 0
    carrito_actualizado = {}

    for producto_id, item in list(carrito.items()):
        try:
            # Verificar si el producto todavía existe en la base de datos
            producto = Producto.objects.get(id=producto_id)
            item['imagen'] = producto.imagen.url if producto.imagen else None
            item['subtotal'] = item['precio'] * item['cantidad']
            total += item['subtotal']
            carrito_actualizado[producto_id] = item
        except Producto.DoesNotExist:
            # Eliminar productos inexistentes del carrito
            continue

    # Actualizar el carrito en la sesión con datos consistentes
    request.session['carrito'] = carrito_actualizado

    return render(request, 'carrito/ver_carrito.html', {
        'carrito': carrito_actualizado,
        'total': total,
    })

# Actualizar cantidad de un producto
def actualizar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    cantidad = int(request.POST.get('cantidad', 1))

    if str(producto_id) in carrito:
        if cantidad > 0:
            carrito[str(producto_id)]['cantidad'] = cantidad
        else:
            # Elimina el producto si la cantidad es 0
            del carrito[str(producto_id)]

    request.session['carrito'] = carrito
    return redirect('ver_carrito')

# Eliminar producto del carrito
def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})

    # Verifica si el producto está en el carrito
    if str(producto_id) in carrito:
        if carrito[str(producto_id)]['cantidad'] > 1:
            # Si hay más de una unidad, reduce la cantidad
            carrito[str(producto_id)]['cantidad'] -= 1
            messages.success(request, "Se eliminó una unidad del producto.")
        else:
            # Si solo hay una unidad, elimina el producto por completo
            del carrito[str(producto_id)]
            messages.success(request, "Producto eliminado del carrito.")
        
        # Actualiza el carrito en la sesión
        request.session['carrito'] = carrito
    else:
        messages.error(request, "El producto no está en el carrito.")

    # Redirige a la vista del carrito
    return redirect('ver_carrito')

#Finalizar compra
@login_required
def finalizar_compra(request):
    """
    Procesa la compra, guarda los datos en la base de datos y limpia el carrito.
    """
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('ver_carrito')

    total_venta = 0
    detalles = []

    try:
        # Calcular total y preparar detalles
        for producto_id, item in carrito.items():
            producto = Producto.objects.get(id=producto_id)
            cantidad = item['cantidad']
            precio_unitario = producto.precio
            subtotal = cantidad * precio_unitario
            total_venta += subtotal

            detalles.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'subtotal': subtotal,
            })

        # Guardar datos en la base de datos
        with transaction.atomic():
            # Registrar la venta
            venta = Venta.objects.create(
                usuario=request.user,
                total_venta=total_venta,
                estado='Pagado',  # Cambiar según sea necesario
            )

            # Registrar los detalles de la venta
            for detalle in detalles:
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=detalle['producto'],
                    cantidad=detalle['cantidad'],
                    precio_unitario=detalle['precio_unitario'],
                    subtotal=detalle['subtotal'],
                )

        # Limpiar el carrito
        request.session['carrito'] = {}
        messages.success(request, "Compra realizada exitosamente.")
        return redirect('historial_compras')

    except Exception as e:
        messages.error(request, f"Ocurrió un error al procesar la compra: {e}")
        return redirect('ver_carrito')
    
#Historial de compras
@login_required
def historial_compras(request):
    # Depuración: Verifica el usuario autenticado
    print(f"Usuario autenticado: {request.user} (ID: {request.user.id})")
    
    # Recupera las ventas del usuario autenticado
    ventas = Venta.objects.filter(
        usuario=request.user  # Ventas asociadas al usuario
    ).prefetch_related('detalles__producto')  # Optimiza las consultas relacionadas
    
    # Depuración: Imprime las ventas recuperadas
    print(f"Ventas encontradas: {ventas}")
    
    if not ventas.exists():
        messages.info(request, "No tienes compras registradas.")
    
    # Renderiza la plantilla
    return render(request, 'ventas/historial_compras.html', {'ventas': ventas})

@login_required
def detalle_venta(request, venta_id):
    """
    Muestra el detalle de una venta específica del usuario.
    """
    # Obtén la venta solicitada del usuario actual
    venta = get_object_or_404(Venta, id=venta_id, usuario=request.user)

    # Renderiza la plantilla con el contexto de la venta
    return render(request, 'detalle_compra.html', {
        'venta': venta,
    })

@login_required
def procesar_pago(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "El carrito está vacío. Agrega productos antes de proceder al pago.")
        return redirect('ver_carrito')

    # Crear una nueva venta
    venta = Venta.objects.create(usuario=request.user, fecha_venta=now(), total_venta=0)

    total_venta = 0
    for producto_id, item in carrito.items():
        producto = Producto.objects.get(id=producto_id)
        cantidad = item['cantidad']
        precio_unitario = producto.precio
        subtotal = cantidad * precio_unitario

        # Crear detalle de la venta
        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal
        )

        # Actualizar el stock del producto
        producto.stock -= cantidad
        producto.save()

        total_venta += subtotal

    # Actualizar el total de la venta
    venta.total_venta = total_venta
    venta.save()

    # Limpiar el carrito
    del request.session['carrito']
    request.session.modified = True

    messages.success(request, f"Compra realizada exitosamente. ID de la venta: {venta.id}")
    return redirect('detalle_compra', venta_id=venta.id)

# Procesar pago con tarjeta
def procesar_pago_tarjeta(request):
    if request.method == "POST":
        numero_tarjeta = request.POST.get("numero_tarjeta")
        fecha_vencimiento = request.POST.get("fecha_vencimiento")
        cvv = request.POST.get("cvv")

        # Aquí iría la lógica para procesar el pago con tarjeta
        # Por ejemplo, conectarse con una pasarela de pago externa como Stripe o una simulación.

        messages.success(request, "Pago con tarjeta procesado exitosamente.")
        return redirect("cliente_home")  # Redirigir a la página principal del cliente

    messages.error(request, "Ocurrió un error al procesar el pago con tarjeta.")
    return redirect("ver_carrito")

# Procesar pago con PayPal
def procesar_pago_paypal(request):
    if request.method == "POST":
        correo_paypal = request.POST.get("correo_paypal")
        contrasena_paypal = request.POST.get("contrasena_paypal")

        # Aquí iría la lógica para procesar el pago con PayPal
        # Por ejemplo, conectarse con la API de PayPal o una simulación.

        messages.success(request, "Pago con PayPal procesado exitosamente.")
        return redirect("cliente_home")  # Redirigir a la página principal del cliente

    messages.error(request, "Ocurrió un error al procesar el pago con PayPal.")
    return redirect("ver_carrito")

@login_required
def confirmar_compra(request):
    carrito = request.session.get("carrito", {})
    total = sum(item["precio"] * item["cantidad"] for item in carrito.values())

    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("ver_carrito")

    if request.method == "POST":
        metodo_pago = request.POST.get("metodo_pago")
        if metodo_pago == "tarjeta":
            return redirect("procesar_pago_tarjeta")
        elif metodo_pago == "paypal":
            return redirect("procesar_pago_paypal")

    return render(request, "compra/confirmar_compra.html", {
        "carrito": carrito,
        "total": total,
    })
def home_cliente(request):
    """
    Vista para el home del cliente, donde se muestran los productos con filtros, un buscador
    y el carrito de compras.
    """
    # Obtener parámetros de búsqueda, categoría, rango de precios y orden
    query = request.GET.get('q', '').strip()  # Eliminar espacios en blanco
    categoria_id = request.GET.get('categoria', None)  # Filtrar por categoría
    precio = request.GET.get('precio', None)  # Rango de precios
    ordenar = request.GET.get('ordenar', None)  # Ordenar por

    # Obtener todos los productos inicialmente
    productos = Producto.objects.all()

    # Filtrar productos por búsqueda
    if query:
        productos = productos.filter(nombre__icontains=query)

    # Filtrar productos por categoría
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    # Filtrar productos por rango de precios
    if precio:
        rango = precio.split('-')
        if len(rango) == 2:
            productos = productos.filter(precio__gte=rango[0], precio__lte=rango[1])
        elif precio == '200':
            productos = productos.filter(precio__gte=200)

    # Filtrar productos con stock disponible
    productos = productos.filter(stock__gt=0)

    # Ordenar productos si se seleccionó una opción
    if ordenar:
        productos = productos.order_by(ordenar)

    # Obtener todas las categorías para los filtros
    categorias = Categoria.objects.all()

    # Obtener el carrito de compras de la sesión
    carrito = request.session.get('carrito', {})

    # Calcular el total del carrito
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())

    # Contexto para la plantilla
    contexto = {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categoria_id': int(categoria_id) if categoria_id else None,  # Convertir categoría a entero si existe
        'carrito': carrito,
        'total': total,
    }

    return render(request, 'cliente/home.html', contexto)


# Verifica si el usuario es administrador
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_home(request):
    return render(request, 'admin/home.html', {
        'titulo': 'Panel Administrativo',
    })
    
def tu_vista(request, producto_id):
    producto = Producto.objects.get(id=producto_id)

    # Define la función aquí
    def usuario_compro_producto(usuario, producto):
        """
        Verifica si el usuario ha comprado el producto.
        """
        return Venta.objects.filter(
            usuario=usuario,
            estado='Pagado',
            detalles__producto=producto
        ).exists()

    # Validación dentro de la vista
    if not usuario_compro_producto(request.user, producto):
        messages.error(request, "No puedes dejar una reseña porque no has comprado este producto.")
        return redirect('detalle_producto', producto_id=producto.id)
    
def detalle_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, pk=producto_id)
        reseñas = Reseña.objects.filter(producto=producto).values('estrellas', 'comentario')
        data = {
            "id": producto.id,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "precio": float(producto.precio),  # Asegúrate de convertir Decimal a float
            "stock": producto.stock,
            "imagen": producto.imagen.url if producto.imagen else "",
            "reseñas": list(reseñas),
        }
        return JsonResponse(data)
    except Producto.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def usuario_compro_producto(usuario, producto):
    """
    Verifica si el usuario ha comprado el producto.
    """
    return Venta.objects.filter(
        usuario=usuario,
        estado='Pagado',
        detalles__producto=producto  # Esto utiliza el related_name definido
    ).exists()


def agregar_resena(request, producto_id):
    """Permite a los usuarios autenticados dejar una reseña si compraron el producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    # Verificar si el usuario ya dejó una reseña para este producto
    if Reseña.objects.filter(usuario=request.user, producto=producto).exists():
        messages.error(request, "Ya has dejado una reseña para este producto.")
        return redirect('detalle_producto', producto_id=producto.id)

    if request.method == 'POST':
        estrellas = request.POST.get('estrellas')
        comentario = request.POST.get('comentario')

        # Crear la reseña
        Reseña.objects.create(
            usuario=request.user,
            producto=producto,
            estrellas=estrellas,
            comentario=comentario
        )
        messages.success(request, "Tu reseña ha sido guardada exitosamente.")
        return redirect('detalle_producto', producto_id=producto.id)

    return redirect('detalle_producto', producto_id=producto.id)
@login_required
def crear_resena(request, producto_id):
    """
    Permite a los usuarios autenticados dejar una reseña si compraron el producto.
    """
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        estrellas = request.POST.get('estrellas')
        comentario = request.POST.get('comentario')

        # Validar campos requeridos
        if not estrellas or not comentario:
            messages.error(request, "Por favor completa todos los campos.")
            return redirect('home_cliente')

        # Verificar si el usuario ya dejó una reseña para este producto
        if Reseña.objects.filter(usuario=request.user, producto=producto).exists():
            messages.error(request, "Ya has dejado una reseña para este producto.")
            return redirect('home_cliente')

        # Crear la reseña
        Reseña.objects.create(
            producto=producto,
            usuario=request.user,
            estrellas=int(estrellas),
            comentario=comentario
        )
        messages.success(request, "Reseña y comentario añadidos correctamente.")
        return redirect('home_cliente')

    messages.error(request, "Método no permitido.")
    return redirect('home_cliente')
@csrf_exempt
def api_detalle_producto(request, producto_id):
    """
    API para obtener los detalles del producto, reseñas y si el usuario ha comprado el producto.
    """
    producto = get_object_or_404(Producto, id=producto_id)
    reseñas = producto.reseñas.all()
    usuario_compro_producto = False

    # Verifica si el usuario ha comprado este producto
    if request.user.is_authenticated:
        usuario_compro_producto = Venta.objects.filter(
            usuario=request.user,
            estado='Pagado',
            detalles__producto=producto
        ).exists()

    # Construye la respuesta JSON
    data = {
        "id": producto.id,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio": float(producto.precio),
        "stock": producto.stock,
        "imagen": producto.imagen.url if producto.imagen else '',
        "reseñas": [
            {
                "usuario": reseña.usuario.username,
                "estrellas": reseña.estrellas,
                "comentario": reseña.comentario,
            }
            for reseña in reseñas
        ],
        "usuario_compro_producto": usuario_compro_producto,
    }
    return JsonResponse(data)
@login_required
def detalle_compra(request, venta_id):
    """
    Muestra el detalle de una compra específica realizada por el usuario.
    """
    # Obtener la venta asociada al usuario autenticado
    venta = get_object_or_404(Venta, id=venta_id, usuario=request.user)
    
    # Preparar el contexto para pasar a la plantilla
    contexto = {
        'venta': venta,
        'detalles': venta.detalles.all()  # Acceder a los detalles de la venta
    }
    
    # Renderizar la plantilla
    return render(request, 'historial/detalle_compra.html', contexto)

# Listar proveedores
def listar_proveedores(request):
    proveedores_list = Proveedor.objects.all()  # Obtener todos los proveedores
    paginator = Paginator(proveedores_list, 5)  # Muestra 5 proveedores por página
    page_number = request.GET.get('page')
    proveedores = paginator.get_page(page_number)
    return render(request, 'proveedores/listar_proveedores.html', {'proveedores': proveedores})
@csrf_protect
# Crear proveedor
def crear_proveedor(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        ruc = request.POST.get('ruc')
        contacto = request.POST.get('contacto')
        direccion = request.POST.get('direccion')

        if Proveedor.objects.filter(ruc=ruc).exists():
            messages.error(request, 'El RUC ya está registrado.')
        else:
            Proveedor.objects.create(
                nombre=nombre,
                ruc=ruc,
                contacto=contacto,
                direccion=direccion
            )
            messages.success(request, 'Proveedor creado exitosamente.')
            return redirect('listar_proveedores')

    return render(request, 'proveedores/crear_proveedor.html')
@csrf_protect
# Editar proveedor
def editar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        proveedor.nombre = request.POST.get('nombre')
        proveedor.ruc = request.POST.get('ruc')
        proveedor.contacto = request.POST.get('contacto')
        proveedor.direccion = request.POST.get('direccion')
        proveedor.save()
        messages.success(request, 'Proveedor actualizado exitosamente.')
        return redirect('listar_proveedores')

    return render(request, 'proveedores/editar_proveedor.html', {'proveedor': proveedor})
@csrf_protect
# Eliminar proveedor
def eliminar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado exitosamente.')
        return redirect('listar_proveedores')

    return render(request, 'proveedores/eliminar_proveedor.html', {'proveedor': proveedor})
from django.urls import path
from . import views

urlpatterns = [
    # Productos
    path('productos/', views.listar_productos, name='listar_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/detalle/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('productos/<int:producto_id>/reseña/', views.crear_resena, name='crear_resena'),  # Ruta para reseñas de productos

    # Carrito de compras
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),

    # Compra y Pago
    path('compra/confirmar/', views.confirmar_compra, name='confirmar_compra'),
    path('compra/procesar/', views.procesar_pago, name='procesar_pago'),
    path('compra/tarjeta/', views.procesar_pago_tarjeta, name='procesar_pago_tarjeta'),

    # Historial de compras
    path('historial/', views.historial_compras, name='historial_compras'),
    path('historial/detalle/<int:venta_id>/', views.detalle_compra, name='detalle_compra'),

    # Estadísticas
    path('estadisticas/', views.estadisticas_productos, name='estadisticas_productos'),

    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Homes
    path('admin_dashboard/', views.admin_home, name='admin_home'),
    path('', views.home_cliente, name='home_cliente'),  # Página principal del cliente

    # API
    path('api/productos/<int:producto_id>/', views.api_detalle_producto, name='api_detalle_producto'),
    
     # Proveedores
    path('proveedores/', views.listar_proveedores, name='listar_proveedores'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/editar/<int:proveedor_id>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),

]

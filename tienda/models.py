from django.db import models
from django.contrib.auth.models import User  # Importa el modelo User
class Categoria(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
class Venta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=50,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Pagado', 'Pagado'),
            ('Cancelado', 'Cancelado'),
        ],
        default='Pendiente'  # Valor por defecto
    )


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle de Venta {self.venta.id} - {self.producto.nombre}"


class Reseña(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='reseñas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estrellas = models.PositiveIntegerField()
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reseña {self.producto.nombre} - {self.usuario.username}"

from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=11, unique=True)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
class Transaccion(models.Model):
    venta = models.ForeignKey('Venta', on_delete=models.CASCADE, related_name='transacciones')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_transaccion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transacción {self.id} - Venta {self.venta.id}"

class HistorialProveedor(models.Model):
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE, related_name='historial')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='historial_proveedores')
    fecha_suministro = models.DateTimeField(auto_now_add=True)
    cantidad_suministrada = models.PositiveIntegerField()

    def __str__(self):
        return f"Historial - {self.proveedor.nombre} - {self.producto.nombre}"

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(
        max_length=50,
        choices=[
            ('Pedido', 'Pedido'),
            ('Envio', 'Envio'),
            ('Promocion', 'Promoción'),
        ]
    )
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación {self.tipo} - {self.usuario.username}"

class Entrega(models.Model):
    venta = models.ForeignKey('Venta', on_delete=models.CASCADE, related_name='entregas')
    tipo_ubicacion = models.CharField(
        max_length=50,
        choices=[
            ('Domicilio', 'Domicilio'),
            ('Sede', 'Sede'),
        ]
    )
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_entrega = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        # Validación para que el campo dirección sea obligatorio si es Domicilio
        if self.tipo_ubicacion == 'Domicilio' and not self.direccion:
            raise ValidationError('La dirección es obligatoria para entregas a domicilio.')

    def __str__(self):
        return f"Entrega - {self.tipo_ubicacion} - Venta {self.venta.id}"

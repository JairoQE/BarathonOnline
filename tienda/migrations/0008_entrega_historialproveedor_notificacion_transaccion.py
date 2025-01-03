# Generated by Django 5.0.10 on 2024-12-28 06:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0007_proveedor'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entrega',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_ubicacion', models.CharField(choices=[('Domicilio', 'Domicilio'), ('Sede', 'Sede')], max_length=50)),
                ('direccion', models.CharField(blank=True, max_length=255, null=True)),
                ('fecha_entrega', models.DateTimeField(auto_now_add=True)),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entregas', to='tienda.venta')),
            ],
        ),
        migrations.CreateModel(
            name='HistorialProveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_suministro', models.DateTimeField(auto_now_add=True)),
                ('cantidad_suministrada', models.PositiveIntegerField()),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial_proveedores', to='tienda.producto')),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial', to='tienda.proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('Pedido', 'Pedido'), ('Envio', 'Envio'), ('Promocion', 'Promoción')], max_length=50)),
                ('mensaje', models.TextField()),
                ('fecha_envio', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_transaccion', models.DateTimeField(auto_now_add=True)),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transacciones', to='tienda.venta')),
            ],
        ),
    ]

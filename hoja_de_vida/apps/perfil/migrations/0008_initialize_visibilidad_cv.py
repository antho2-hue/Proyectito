# Generated migration to initialize VisibilidadCV

from django.db import migrations
from apps.perfil.models import DatosPersonales, VisibilidadCV


def initialize_visibilidad_cv(apps, schema_editor):
    """
    Función para crear registros de VisibilidadCV para todos los perfiles activos.
    Se ejecuta cuando se corre la migración.
    """
    DatosPersonales = apps.get_model('perfil', 'DatosPersonales')
    VisibilidadCV = apps.get_model('perfil', 'VisibilidadCV')
    
    # Obtener todos los perfiles activos
    perfiles = DatosPersonales.objects.filter(perfilactivo=1)
    
    for perfil in perfiles:
        # Crear o actualizar el registro de visibilidad
        VisibilidadCV.objects.get_or_create(
            perfil=perfil,
            defaults={
                'mostrar_datos_personales': True,
                'mostrar_experiencias': True,
                'mostrar_cursos': True,
                'mostrar_reconocimientos': True,
                'mostrar_productos_academicos': True,
                'mostrar_productos_laborales': True,
            }
        )


def reverse_func(apps, schema_editor):
    """Función inversa - no hace nada"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0007_alter_datospersonales_fechanacimiento'),
    ]

    operations = [
        migrations.RunPython(initialize_visibilidad_cv, reverse_func),
    ]

#!/usr/bin/env python
"""
Script para inicializar registros de VisibilidadCV para todos los perfiles activos.
Ejecutar con: python manage.py shell < initialize_visibilidad.py
O: python manage.py shell
   >>> exec(open('initialize_visibilidad.py').read())
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.perfil.models import DatosPersonales, VisibilidadCV

def initialize_visibilidad():
    """Crear registros de VisibilidadCV para todos los perfiles activos que no los tengan"""
    
    # Obtener todos los perfiles activos
    perfiles = DatosPersonales.objects.filter(perfilactivo=1)
    
    created_count = 0
    already_exists = 0
    
    for perfil in perfiles:
        # Intentar obtener el registro de visibilidad
        visibilidad, created = VisibilidadCV.objects.get_or_create(
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
        
        if created:
            created_count += 1
            print(f"✅ Creado: VisibilidadCV para {perfil.nombres} {perfil.apellidos}")
        else:
            already_exists += 1
            print(f"ℹ️ Ya existe: VisibilidadCV para {perfil.nombres} {perfil.apellidos}")
    
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN:")
    print(f"   ✅ Registros creados: {created_count}")
    print(f"   ℹ️ Registros existentes: {already_exists}")
    print(f"   📈 Total: {created_count + already_exists}")
    print(f"{'='*60}")

if __name__ == '__main__':
    initialize_visibilidad()

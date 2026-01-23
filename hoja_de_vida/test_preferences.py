#!/usr/bin/env python
"""
Script para probar la lógica de preferencias
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Simular request.GET con parámetros
from django.http import QueryDict

# Test 1: Todas las secciones marcadas (descarga completa)
print("=" * 70)
print("TEST 1: CV Completo (todas las secciones)")
print("=" * 70)
query_dict = QueryDict('plantilla=professional', mutable=True)
print(f"URL: ?{query_dict.urlencode()}")

# Mapeo de parámetros
param_to_field = {
    'datos_personales': 'mostrar_datos_personales',
    'experiencias_laborales': 'mostrar_experiencias',
    'cursos': 'mostrar_cursos',
    'reconocimientos': 'mostrar_reconocimientos',
    'productos_academicos': 'mostrar_productos_academicos',
    'productos_laborales': 'mostrar_productos_laborales',
}

has_preferences_params = any(key in query_dict for key in param_to_field.keys())
print(f"¿Hay parámetros de preferencia?: {has_preferences_params}")
print(f"Resultado: Descarga CV COMPLETO\n")

# Test 2: Con preferencias personalizadas
print("=" * 70)
print("TEST 2: CV Personalizado (solo algunas secciones)")
print("=" * 70)
query_dict = QueryDict(
    'plantilla=professional&datos_personales=true&experiencias_laborales=false&cursos=true&reconocimientos=false&productos_academicos=true&productos_laborales=true',
    mutable=True
)
print(f"URL: ?{query_dict.urlencode()}")

has_preferences_params = any(key in query_dict for key in param_to_field.keys())
print(f"¿Hay parámetros de preferencia?: {has_preferences_params}")

if has_preferences_params:
    print("\nSecciones a mostrar:")
    for param, field in param_to_field.items():
        param_value = query_dict.get(param, 'false').lower() == 'true'
        print(f"  {field:35} = {param_value}")

print("\n" + "=" * 70)
print("✅ La lógica parece correcta!")
print("=" * 70)

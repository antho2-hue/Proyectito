import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.perfil.models import DatosPersonales
from apps.trayectoria.models import Reconocimiento

perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
if perfil:
    print("=== ANÁLISIS DETALLADO DEL QUERYSET ===")

    # Query sin distinct
    reconocimientos_sin_distinct = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    )

    # Query con distinct
    reconocimientos_con_distinct = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).distinct()

    print(f"Sin distinct: {reconocimientos_sin_distinct.count()} registros")
    print(f"Con distinct: {reconocimientos_con_distinct.count()} registros")

    # Mostrar SQL queries para ver si hay joins
    print(f"\nSQL sin distinct: {reconocimientos_sin_distinct.query}")
    print(f"\nSQL con distinct: {reconocimientos_con_distinct.query}")

    # Verificar si hay duplicados por ID
    ids_sin_distinct = list(reconocimientos_sin_distinct.values_list('idreconocimiento', flat=True))
    ids_con_distinct = list(reconocimientos_con_distinct.values_list('idreconocimiento', flat=True))

    print(f"\nIDs sin distinct: {ids_sin_distinct}")
    print(f"IDs con distinct: {ids_con_distinct}")

    # Verificar duplicados
    if len(ids_sin_distinct) != len(set(ids_sin_distinct)):
        print("¡HAY DUPLICADOS POR ID en el queryset sin distinct!")
        from collections import Counter
        duplicates = [item for item, count in Counter(ids_sin_distinct).items() if count > 1]
        print(f"IDs duplicados: {duplicates}")
    else:
        print("No hay duplicados por ID")

    # Mostrar todos los campos para verificar si hay diferencias
    print("\n=== TODOS LOS REGISTROS ===")
    for i, r in enumerate(reconocimientos_sin_distinct, 1):
        print(f"{i}. ID: {r.idreconocimiento}, Tipo: {r.tiporeconocimiento}, Activo: {r.activarparaqueseveaenfront}")

else:
    print('No se encontró perfil activo')

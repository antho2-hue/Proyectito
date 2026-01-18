import os
import django
from django.test import Client
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

client = Client()
response = client.get('/')

if response.status_code == 200:
    html_content = response.content.decode('utf-8')

    print("=== ANÁLISIS DETALLADO DEL HTML RENDERIZADO ===")

    # Buscar todas las etiquetas H2 que contienen "Reconocimientos"
    h2_matches = re.findall(r'<h2[^>]*class="[^"]*section-title[^"]*"[^>]*>Reconocimientos</h2>', html_content)
    print(f"Encabezados H2 con clase 'section-title' que dicen 'Reconocimientos': {len(h2_matches)}")

    # Buscar todas las secciones con clase main-section
    main_sections = re.findall(r'<section[^>]*class="[^"]*main-section[^"]*"[^>]*>.*?</section>', html_content, re.DOTALL)
    print(f"Total de secciones con clase 'main-section': {len(main_sections)}")

    # Filtrar las que contienen "Reconocimientos"
    reconocimientos_sections = [s for s in main_sections if 'Reconocimientos' in s]
    print(f"Secciones 'main-section' que contienen 'Reconocimientos': {len(reconocimientos_sections)}")

    # Mostrar cada sección encontrada con más detalle
    for i, section in enumerate(reconocimientos_sections, 1):
        print(f"\n--- SECCIÓN {i} DETALLADA ---")

        # Extraer el ID de la sección si existe
        id_match = re.search(r'id="([^"]*)"', section)
        if id_match:
            print(f"ID de la sección: {id_match.group(1)}")

        # Contar elementos award-card en esta sección
        award_cards = section.count('<div class="award-card">')
        print(f"Elementos 'award-card' en esta sección: {award_cards}")

        # Mostrar el contenido de la sección (primeros 200 caracteres)
        content_preview = section[:200] + "..." if len(section) > 200 else section
        print(f"Contenido preview: {content_preview}")

    # Verificar si hay algún duplicado por ID o clase
    section_ids = re.findall(r'<section[^>]*id="([^"]*)"[^>]*>', html_content)
    duplicate_ids = [id for id in section_ids if section_ids.count(id) > 1]
    if duplicate_ids:
        print(f"\nIDs de sección duplicados encontrados: {set(duplicate_ids)}")

    # Verificar si hay algún problema con el template o el contexto
    template_errors = re.findall(r'TemplateSyntaxError|NoReverseMatch|VariableDoesNotExist', html_content)
    if template_errors:
        print(f"\nErrores de template encontrados: {template_errors}")

    print(f"\n=== RESUMEN ===")
    print(f"Total de encabezados 'Reconocimientos': {len(h2_matches)}")
    print(f"Total de secciones con reconocimientos: {len(reconocimientos_sections)}")

    if len(h2_matches) == 1 and len(reconocimientos_sections) == 1:
        print("✅ RESULTADO: Solo hay 1 sección de Reconocimientos en el HTML")
    else:
        print("❌ RESULTADO: Hay múltiples secciones de Reconocimientos")

else:
    print(f"Error HTTP: {response.status_code}")
    print("Contenido del error:")
    print(response.content.decode('utf-8')[:1000])




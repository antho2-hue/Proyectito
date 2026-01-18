import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

client = Client()
response = client.get('/')

if response.status_code == 200:
    html_content = response.content.decode('utf-8')

    print("=== VERIFICACIÓN DETALLADA DE RECONOCIMIENTOS ===")

    # Buscar todas las secciones que contienen "Reconocimiento"
    import re

    # Buscar títulos de sección
    sections = re.findall(r'<h2[^>]*>Reconocimientos</h2>', html_content)
    print(f"Títulos de sección 'Reconocimientos': {len(sections)}")

    # Buscar secciones completas
    full_sections = re.findall(r'<section[^>]*>.*?</section>', html_content, re.DOTALL)
    reconocimientos_sections = [s for s in full_sections if 'Reconocimientos' in s]
    print(f"Secciones completas que contienen 'Reconocimientos': {len(reconocimientos_sections)}")

    # Mostrar el contenido de cada sección
    for i, section in enumerate(reconocimientos_sections, 1):
        print(f"\n--- SECCIÓN {i} ---")
        # Extraer solo el contenido relevante
        title_match = re.search(r'<h2[^>]*>Reconocimientos</h2>', section)
        if title_match:
            print("Contiene título 'Reconocimientos'")

        # Contar award-card en esta sección
        award_cards = section.count('award-card')
        print(f"Elementos award-card en esta sección: {award_cards}")

    # Buscar todos los elementos que podrían contener reconocimientos
    all_award_cards = html_content.count('<div class="award-card">')
    print(f"\nTotal de elementos award-card en todo el HTML: {all_award_cards}")

    # Mostrar si hay algún duplicado por ID o clase
    ids = re.findall(r'id="([^"]*)"', html_content)
    duplicate_ids = [id for id in ids if ids.count(id) > 1]
    if duplicate_ids:
        print(f"IDs duplicados encontrados: {set(duplicate_ids)}")

    print("\n=== FIN VERIFICACIÓN ===")

else:
    print(f"Error HTTP: {response.status_code}")




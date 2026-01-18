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

    print("=== VERIFICACIÓN FINAL DE DUPLICADOS ===")

    # Buscar todas las secciones h2 que contienen "Reconocimientos"
    h2_matches = re.findall(r'<h2[^>]*>Reconocimientos</h2>', html_content)
    print(f"Títulos H2 'Reconocimientos': {len(h2_matches)}")

    # Buscar todas las secciones que contienen el texto "Reconocimientos"
    sections = re.findall(r'<section[^>]*>.*?</section>', html_content, re.DOTALL)
    reconocimientos_sections = [s for s in sections if 'Reconocimientos' in s]
    print(f"Secciones completas con 'Reconocimientos': {len(reconocimientos_sections)}")

    # Buscar todos los divs con clase award-card
    award_cards = re.findall(r'<div[^>]*class="[^"]*award-card[^"]*"[^>]*>.*?</div>', html_content, re.DOTALL)
    print(f"Elementos award-card: {len(award_cards)}")

    # Mostrar el contenido de cada sección encontrada
    for i, section in enumerate(reconocimientos_sections, 1):
        print(f"\n--- SECCIÓN {i} ---")
        # Extraer el contenido relevante
        lines = section.split('\n')
        for line in lines:
            if 'Reconocimientos' in line or 'Privado' in line or 'Entidad:' in line or 'Fecha:' in line:
                print(line.strip())

    # Verificar si hay algún comentario HTML o algo que pueda estar causando duplicados
    print(f"\nTotal de líneas en HTML: {len(html_content.splitlines())}")
    print(f"Tamaño total del HTML: {len(html_content)} caracteres")

    # Buscar cualquier duplicado de contenido específico
    privado_count = html_content.count('Privado - fdfsdf')
    print(f"Apariciones de 'Privado - fdfsdf': {privado_count}")

else:
    print(f"Error HTTP: {response.status_code}")




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

    print("=== VERIFICACIÓN FINAL CORREGIDA ===")

    # Contar secciones con "Reconocimientos"
    h2_matches = re.findall(r'<h2[^>]*>Reconocimientos</h2>', html_content)
    print(f"Títulos H2 'Reconocimientos': {len(h2_matches)}")

    # Contar elementos award-card
    award_cards = html_content.count('<div class="award-card">')
    print(f"Elementos award-card: {award_cards}")

    # Contar apariciones del contenido específico
    privado_count = html_content.count('Privado - fdfsdf')
    print(f"Apariciones del contenido 'Privado - fdfsdf': {privado_count}")

    if len(h2_matches) == 1 and award_cards == 1 and privado_count == 1:
        print("✅ ¡PROBLEMA RESUELTO! Solo hay 1 sección de Reconocimientos")
    else:
        print("❌ Todavía hay duplicados")

else:
    print(f"Error HTTP: {response.status_code}")
    print(response.content.decode('utf-8')[:500])




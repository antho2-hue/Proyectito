import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

client = Client()
response = client.get('/')

if response.status_code == 200:
    html_content = response.content.decode('utf-8')

    # Contar cuántas veces aparece "Reconocimientos"
    count_reconocimientos = html_content.count('Reconocimientos')
    print(f'Aparece "Reconocimientos" {count_reconocimientos} veces en el HTML')

    # Buscar secciones de reconocimientos
    import re
    reconocimientos_sections = re.findall(r'<section[^>]*>.*?Reconocimientos.*?</section>', html_content, re.DOTALL)
    print(f'Secciones completas de reconocimientos encontradas: {len(reconocimientos_sections)}')

    # Buscar award-card
    award_cards = html_content.count('award-card')
    print(f'Elementos award-card encontrados: {award_cards}')

    if count_reconocimientos > 1:
        print('¡HAY DUPLICADOS EN EL HTML!')
    else:
        print('No hay duplicados en el HTML renderizado')
else:
    print(f'Error: {response.status_code}')




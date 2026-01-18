import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.test import Client

client = Client()
for path in ['/descargar-cv/', '/descargar-cv-completo/']:
    r = client.get(path)
    print(path, 'status', r.status_code, 'content-type', r.get('Content-Type'))
    print('len', len(r.content))
    print('headers:', dict(r.items()))
    print()
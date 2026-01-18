#!/usr/bin/env python
"""Genera PDFs llamando a las vistas internamente con RequestFactory.
No requiere el servidor en ejecución.
Guarda: test_cv_local.pdf y test_cv_local_full.pdf
"""
import os
import sys
import django
from django.test.client import RequestFactory

# Prepare Django
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.perfil.views import descargar_cv_pdf, descargar_cv_completo_pdf
from django.core.handlers.wsgi import WSGIRequest
from django.test.client import RequestFactory

OUT_DIR = os.path.normpath(os.path.join(ROOT, 'out'))
os.makedirs(OUT_DIR, exist_ok=True)

factory = RequestFactory()

# Helper to save response content
def save_response(resp, name):
    if hasattr(resp, 'status_code') and resp.status_code != 200:
        print(f"Error: response status {resp.status_code}")
        return False
    data = getattr(resp, 'content', None)
    if not data:
        print("No content in response")
        return False
    path = os.path.join(OUT_DIR, name)
    with open(path, 'wb') as fh:
        fh.write(data)
    print(f"Saved: {path} ({len(data)} bytes)")
    return True

print('Generating single CV PDF...')
req = factory.get('/descargar-cv/', HTTP_HOST='127.0.0.1:8000')
resp = descargar_cv_pdf(req)
save_response(resp, 'test_cv_local.pdf')

print('\nGenerating full CV PDF (check_all=1)...')
req2 = factory.get('/descargar-cv-completo/', {'check_all': '1'}, HTTP_HOST='127.0.0.1:8000')
resp2 = descargar_cv_completo_pdf(req2)
save_response(resp2, 'test_cv_local_full.pdf')

print('\nDone.')

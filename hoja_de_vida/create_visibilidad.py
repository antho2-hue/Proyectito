#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.perfil.models import DatosPersonales, VisibilidadCV

perfiles = DatosPersonales.objects.all()
print(f'Total perfiles: {perfiles.count()}')

for p in perfiles:
    v, created = VisibilidadCV.objects.get_or_create(perfil=p)
    status = 'created' if created else 'already exists'
    print(f'Perfil {p.pk}: VisibilidadCV {status}')

print('Done!')

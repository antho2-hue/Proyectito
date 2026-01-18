import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.perfil.models import DatosPersonales
from apps.trayectoria.models import Reconocimiento

perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
if perfil:
    reconocimientos = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True
    )
    print(f'Total reconocimientos: {reconocimientos.count()}')
    print(f'Distinct reconocimientos: {reconocimientos.distinct().count()}')

    print('\nReconocimientos encontrados:')
    for r in reconocimientos:
        print(f'- ID: {r.pk} | Tipo: {r.tiporeconocimiento} | Descripción: {r.descripcionreconocimiento}')
else:
    print('No se encontró perfil activo')

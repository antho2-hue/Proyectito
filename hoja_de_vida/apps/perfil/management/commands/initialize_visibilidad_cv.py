from django.core.management.base import BaseCommand
from apps.perfil.models import DatosPersonales, VisibilidadCV


class Command(BaseCommand):
    help = 'Inicializar registros de VisibilidadCV para todos los perfiles activos'

    def handle(self, *args, **options):
        # Obtener todos los perfiles activos
        perfiles = DatosPersonales.objects.filter(perfilactivo=1)
        
        created_count = 0
        already_exists = 0
        
        for perfil in perfiles:
            # Intentar obtener el registro de visibilidad
            visibilidad, created = VisibilidadCV.objects.get_or_create(
                perfil=perfil,
                defaults={
                    'mostrar_datos_personales': True,
                    'mostrar_experiencias': True,
                    'mostrar_cursos': True,
                    'mostrar_reconocimientos': True,
                    'mostrar_productos_academicos': True,
                    'mostrar_productos_laborales': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Creado: VisibilidadCV para {perfil.nombres} {perfil.apellidos}"
                    )
                )
            else:
                already_exists += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"ℹ️ Ya existe: VisibilidadCV para {perfil.nombres} {perfil.apellidos}"
                    )
                )
        
        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS(f"📊 RESUMEN:"))
        self.stdout.write(self.style.SUCCESS(f"   ✅ Registros creados: {created_count}"))
        self.stdout.write(self.style.WARNING(f"   ℹ️ Registros existentes: {already_exists}"))
        self.stdout.write(self.style.SUCCESS(f"   📈 Total: {created_count + already_exists}"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))

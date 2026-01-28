from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from .models import (
    ExperienciaLaboral,
    Reconocimiento,
    CursoRealizado,
    ProductoAcademico,
    ProductoLaboral,
    VentaGarage,
)
from .forms_admin import CursoRealizadoAdminForm, ReconocimientoAdminForm, VentaGarageAdminForm, ExperienciaLaboralAdminForm
from .services.azure_storage import upload_pdf


@admin.register(ExperienciaLaboral)
class ExperienciaLaboralAdmin(admin.ModelAdmin):
    form = ExperienciaLaboralAdminForm
    list_display = ('cargodesempenado', 'activarparaqueseveaenfront')

    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el perfil del usuario si no existe
        if not obj.idperfilconqueestaactivo:
            from apps.perfil.models import DatosPersonales
            try:
                obj.idperfilconqueestaactivo = DatosPersonales.objects.first()
            except:
                pass
        
        # If a file was uploaded, send to Azure and save URL
        uploaded = form.cleaned_data.get('certificado_subir')
        if uploaded:
            url = upload_pdf(uploaded, filename=uploaded.name)
            obj.rutacertificado = url
        super().save_model(request, obj, form, change)


@admin.register(Reconocimiento)
class ReconocimientoAdmin(admin.ModelAdmin):
    form = ReconocimientoAdminForm
    list_display = ('descripcionreconocimiento', 'activarparaqueseveaenfront')

    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el perfil del usuario si no existe
        if not obj.idperfilconqueestaactivo:
            from apps.perfil.models import DatosPersonales
            try:
                obj.idperfilconqueestaactivo = DatosPersonales.objects.first()
            except:
                pass
        
        # If a file was uploaded, send to Azure and save URL
        uploaded = form.cleaned_data.get('certificado_subir')
        if uploaded:
            url = upload_pdf(uploaded, filename=uploaded.name)
            obj.rutacertificado = url
        super().save_model(request, obj, form, change)


@admin.register(CursoRealizado)
class CursoRealizadoAdmin(admin.ModelAdmin):
    form = CursoRealizadoAdminForm
    list_display = ('nombrecurso', 'activarparaqueseveaenfront')

    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el perfil del usuario si no existe
        if not obj.idperfilconqueestaactivo:
            from apps.perfil.models import DatosPersonales
            try:
                obj.idperfilconqueestaactivo = DatosPersonales.objects.first()
            except:
                pass
        
        uploaded = form.cleaned_data.get('certificado_subir')
        if uploaded:
            try:
                url = upload_pdf(uploaded, filename=uploaded.name)
                obj.rutacertificado = url
            except Exception as exc:
                messages.error(request, f'Error al subir a Azure: {exc}')
        super().save_model(request, obj, form, change)


@admin.register(ProductoAcademico)
class ProductoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('nombrerecurso', 'activarparaqueseveaenfront')
    
    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el perfil del usuario si no existe
        if not obj.idperfilconqueestaactivo:
            from apps.perfil.models import DatosPersonales
            try:
                obj.idperfilconqueestaactivo = DatosPersonales.objects.first()
            except:
                pass
        super().save_model(request, obj, form, change)


@admin.register(ProductoLaboral)
class ProductoLaboralAdmin(admin.ModelAdmin):
    list_display = ('nombreproducto', 'activarparaqueseveaenfront')
    
    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el perfil del usuario si no existe
        if not obj.idperfilconqueestaactivo:
            from apps.perfil.models import DatosPersonales
            try:
                obj.idperfilconqueestaactivo = DatosPersonales.objects.first()
            except:
                pass
        super().save_model(request, obj, form, change)


@admin.register(VentaGarage)
class VentaGarageAdmin(admin.ModelAdmin):
    """Admin para VentaGarage con soporte para imágenes PNG/JPG."""
    form = VentaGarageAdminForm
    list_display = ('nombreproducto', 'estado_disponibilidad', 'activarparaqueseveaenfront')
    list_filter = ('estado_disponibilidad', 'activarparaqueseveaenfront')
    
    def get_fieldsets(self, request, obj=None):
        """Retorna fieldsets diferentes para crear vs cambiar."""
        if obj is None:  # Adding
            return (
                ('Información del Producto', {
                    'fields': ('nombreproducto', 'descripcion', 'estadoproducto', 'valordelbien')
                }),
                ('Imagen', {
                    'fields': ('imagen_subir',),
                    'description': 'Sube una imagen PNG o JPG del producto. Máximo 10MB.'
                }),
                ('Fecha de Publicación', {
                    'fields': ('fecha_publicacion',)
                }),
                ('Control de Disponibilidad', {
                    'fields': ('estado_disponibilidad',),
                    'description': 'Solo administradores pueden cambiar este estado. Vendido = producto no disponible pero visible.'
                }),
                ('Visibilidad en Frontend', {
                    'fields': ('activarparaqueseveaenfront',)
                }),
            )
        else:  # Changing
            return (
                ('Información del Producto', {
                    'fields': ('nombreproducto', 'descripcion', 'estadoproducto', 'valordelbien')
                }),
                ('Imagen', {
                    'fields': ('imagen_subir',),
                    'description': 'Sube una imagen PNG o JPG del producto. Máximo 10MB.'
                }),
                ('Fecha de Publicación', {
                    'fields': ('fecha_publicacion',)
                }),
                ('Control de Disponibilidad', {
                    'fields': ('estado_disponibilidad',),
                    'description': 'Solo administradores pueden cambiar este estado. Vendido = producto no disponible pero visible.'
                }),
                ('Visibilidad en Frontend', {
                    'fields': ('activarparaqueseveaenfront',)
                }),
            )
    
    def save_model(self, request, obj, form, change):
        """Procesa la imagen subida y la guarda en Azure."""
        # Asignar automáticamente el perfil del usuario si no existe
        if not obj.idperfilconqueestaactivo:
            from apps.perfil.models import DatosPersonales
            try:
                obj.idperfilconqueestaactivo = DatosPersonales.objects.first()
            except:
                pass
        
        uploaded = form.cleaned_data.get('imagen_subir')
        if uploaded:
            try:
                # Usar servicios de Azure para subir imagen
                url = upload_pdf(uploaded, filename=uploaded.name)  # Este servicio acepta cualquier archivo
                obj.rutaimagen = url
                messages.success(request, 'Imagen subida correctamente a Azure')
            except Exception as exc:
                messages.error(request, f'Error al subir imagen a Azure: {exc}')
        super().save_model(request, obj, form, change)

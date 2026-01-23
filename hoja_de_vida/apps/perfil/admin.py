from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import DatosPersonales, VisibilidadCV

from apps.documentos.services.azure_storage import upload_profile_image, upload_template_image


class DatosPersonalesAdminForm(forms.ModelForm):
    # transient upload field shown in admin only
    foto_perfil_file = forms.FileField(required=False, help_text='Subir una imagen PNG (se almacenará en Azure)')
    fondo_professional_file = forms.FileField(required=False, help_text='Subir imagen de fondo para plantilla Professional (jpg/png/gif/webp)')
    fondo_modern_file = forms.FileField(required=False, help_text='Subir imagen de fondo para plantilla Modern (jpg/png/gif/webp)')

    class Meta:
        model = DatosPersonales
        fields = '__all__'

    def clean_foto_perfil_file(self):
        f = self.cleaned_data.get('foto_perfil_file')
        if f:
            name = getattr(f, 'name', '')
            if not name.lower().endswith('.png'):
                raise ValidationError('Solo se permiten imágenes PNG (.png)')
            # If content_type is available, also check it
            content_type = getattr(f, 'content_type', '')
            if content_type and content_type != 'image/png':
                raise ValidationError('Solo se permiten imágenes PNG (content-type debe ser image/png)')
        return f

    def clean_fondo_professional_file(self):
        f = self.cleaned_data.get('fondo_professional_file')
        if f:
            name = getattr(f, 'name', '').lower()
            if not name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                raise ValidationError('Formato no válido. Use PNG/JPG/JPEG/GIF/WEBP')
        return f

    def clean_fondo_modern_file(self):
        f = self.cleaned_data.get('fondo_modern_file')
        if f:
            name = getattr(f, 'name', '').lower()
            if not name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                raise ValidationError('Formato no válido. Use PNG/JPG/JPEG/GIF/WEBP')
        return f


@admin.register(DatosPersonales)
class DatosPersonalesAdmin(admin.ModelAdmin):
    form = DatosPersonalesAdminForm
    list_display = ('apellidos', 'nombres', 'numerocedula', 'perfilactivo')

    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'numerocedula', 'descripcionperfil', 'perfilactivo')
        }),
        ('Datos de Contacto', {
            'fields': ('telefonoconvencional', 'telefonofijo', 'sitioweb', 'direcciondomiciliaria', 'direcciontrabajo')
        }),
        ('Información Demográfica', {
            'fields': ('nacionalidad', 'lugarnacimiento', 'fechanacimiento', 'sexo', 'estadocivil', 'licenciaconducir')
        }),
        ('Medios Multimedia', {
            'fields': ('foto_perfil_file', 'foto_perfil_url', 'fondo_professional_file', 'fondo_professional_url', 'fondo_modern_file', 'fondo_modern_url'),
            'description': 'Sube tus imágenes aquí. Se almacenarán automáticamente en Azure.'
        }),
    )

    class Media:
        css = {
            'all': ('perfil/css/cyberadmin.css',)
        }
        js = ('perfil/js/cyberadmin.js',)

    def save_model(self, request, obj, form, change):
        # If a PNG was uploaded via the admin form, upload to Azure and store URL
        f = form.cleaned_data.get('foto_perfil_file') if hasattr(form, 'cleaned_data') else None
        if f:
            try:
                url = upload_profile_image(f)
                obj.foto_perfil_url = url
            except Exception as exc:
                # Raise ValidationError so admin shows the problem
                raise ValidationError(f'Error subiendo la imagen a Azure: {exc}')

        # Template background uploads
        f_prof = form.cleaned_data.get('fondo_professional_file') if hasattr(form, 'cleaned_data') else None
        if f_prof:
            try:
                url = upload_template_image(f_prof)
                obj.fondo_professional_url = url
            except Exception as exc:
                raise ValidationError(f'Error subiendo fondo Professional a Azure: {exc}')

        f_mod = form.cleaned_data.get('fondo_modern_file') if hasattr(form, 'cleaned_data') else None
        if f_mod:
            try:
                url = upload_template_image(f_mod)
                obj.fondo_modern_url = url
            except Exception as exc:
                raise ValidationError(f'Error subiendo fondo Modern a Azure: {exc}')

        super().save_model(request, obj, form, change)


@admin.register(VisibilidadCV)
class VisibilidadCVAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'mostrar_datos_personales', 'mostrar_experiencias', 'mostrar_cursos')
    
    def has_add_permission(self, request):
        return False
    
    fieldsets = (
        ('🔐 CONTROL DE VISIBILIDAD DEL CV PÚBLICO', {
            'fields': ('perfil', 'mostrar_datos_personales', 'mostrar_experiencias', 'mostrar_cursos', 'mostrar_reconocimientos', 'mostrar_productos_academicos', 'mostrar_productos_laborales'),
            'description': '⚠️ IMPORTANTE: Marca qué secciones deseas mostrar en tu CV público. Desmarcar una sección la ocultará completamente del CV que compartes con empresas.',
            'classes': ('wide', 'extrapretty')
        }),
    )

# Global admin branding
admin.site.site_header = "📄 HOJA DE VIDA MODERNA — Panel"
admin.site.site_title = "HOJA DE VIDA MODERNA"
admin.site.index_title = "Dashboard"

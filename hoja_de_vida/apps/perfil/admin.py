from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import DatosPersonales

from apps.documentos.services.azure_storage import upload_profile_image


class DatosPersonalesAdminForm(forms.ModelForm):
    # transient upload field shown in admin only
    foto_perfil_file = forms.FileField(required=False, help_text='Subir una imagen PNG (se almacenará en Azure)')

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


@admin.register(DatosPersonales)
class DatosPersonalesAdmin(admin.ModelAdmin):
    form = DatosPersonalesAdminForm
    list_display = ('apellidos', 'nombres', 'numerocedula', 'perfilactivo')

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

        super().save_model(request, obj, form, change)

# Global admin branding
admin.site.site_header = "CYBERADMIN — Panel"
admin.site.site_title = "CYBERADMIN"
admin.site.index_title = "Dashboard"

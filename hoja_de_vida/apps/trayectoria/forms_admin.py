"""Static admin forms for trayectoria models. Safe and non-invasive."""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CursoRealizado, Reconocimiento, VentaGarage, ExperienciaLaboral


class CursoRealizadoAdminForm(forms.ModelForm):
    """Static form for CursoRealizado in Django Admin."""
    certificado_subir = forms.FileField(required=False, label=_('Certificado (PDF)'))

    class Meta:
        model = CursoRealizado
        fields = '__all__'

    def clean_certificado_subir(self):
        f = self.cleaned_data.get('certificado_subir')
        if not f:
            return f
        content_type = getattr(f, 'content_type', None)
        name = getattr(f, 'name', '')
        if content_type and content_type != 'application/pdf':
            raise forms.ValidationError(_('Sólo se aceptan archivos PDF (content-type inválido).'))
        if not name.lower().endswith('.pdf'):
            raise forms.ValidationError(_('El archivo debe tener extensión .pdf'))
        return f

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar horas >= 1
        totalhoras = cleaned_data.get('totalhoras')
        if totalhoras is not None and totalhoras < 1:
            raise forms.ValidationError(_('Las horas totales deben ser mayor o igual a 1.'))
        
        # Validar que fechainicio <= fechafin
        fechainicio = cleaned_data.get('fechainicio')
        fechafin = cleaned_data.get('fechafin')
        
        if fechainicio and fechafin:
            if fechainicio > fechafin:
                raise forms.ValidationError(
                    _('La fecha de inicio no puede ser mayor que la fecha de fin.')
                )
        
        return cleaned_data


class ReconocimientoAdminForm(forms.ModelForm):
    """Static form for Reconocimiento in Django Admin."""
    certificado_subir = forms.FileField(required=False, label=_('Certificado (PDF)'))

    class Meta:
        model = Reconocimiento
        fields = '__all__'

    def clean_certificado_subir(self):
        f = self.cleaned_data.get('certificado_subir')
        if not f:
            return f
        content_type = getattr(f, 'content_type', None)
        name = getattr(f, 'name', '')
        if content_type and content_type != 'application/pdf':
            raise forms.ValidationError(_('Sólo se aceptan archivos PDF (content-type inválido).'))
        if not name.lower().endswith('.pdf'):
            raise forms.ValidationError(_('El archivo debe tener extensión .pdf'))
        return f

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class ExperienciaLaboralAdminForm(forms.ModelForm):
    """Static form for ExperienciaLaboral in Django Admin."""
    certificado_subir = forms.FileField(required=False, label=_('Certificado (PDF)'))

    class Meta:
        model = ExperienciaLaboral
        fields = '__all__'

    def clean_certificado_subir(self):
        f = self.cleaned_data.get('certificado_subir')
        if not f:
            return f
        content_type = getattr(f, 'content_type', None)
        name = getattr(f, 'name', '')
        if content_type and content_type != 'application/pdf':
            raise forms.ValidationError(_('Sólo se aceptan archivos PDF (content-type inválido).'))
        if not name.lower().endswith('.pdf'):
            raise forms.ValidationError(_('El archivo debe tener extensión .pdf'))
        return f

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que fechainiciogestion <= fechafingestion
        fechainiciogestion = cleaned_data.get('fechainiciogestion')
        fechafingestion = cleaned_data.get('fechafingestion')
        
        if fechainiciogestion and fechafingestion:
            if fechainiciogestion > fechafingestion:
                raise forms.ValidationError(
                    _('La fecha de inicio de gestión no puede ser mayor que la fecha de fin.')
                )
        
        return cleaned_data


class VentaGarageAdminForm(forms.ModelForm):
    """Static form for VentaGarage in Django Admin - permite subir imágenes PNG/JPG."""
    imagen_subir = forms.FileField(required=False, label=_('Imagen del Producto (PNG/JPG)'))

    class Meta:
        model = VentaGarage
        fields = [
            'nombreproducto',
            'estadoproducto',
            'descripcion',
            'valordelbien',
            'estado_disponibilidad',
            'activarparaqueseveaenfront',
            'fecha_publicacion',
        ]

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario e asigna automáticamente el perfil si es una nueva instancia."""
        super().__init__(*args, **kwargs)
        
        # Si es una nueva instancia (no tiene pk), asignar automáticamente el perfil
        if self.instance.pk is None:
            from apps.perfil.models import DatosPersonales
            try:
                self.instance.idperfilconqueestaactivo = DatosPersonales.objects.first()
            except:
                pass

    def clean_imagen_subir(self):
        f = self.cleaned_data.get('imagen_subir')
        if not f:
            return f
        
        # Validar extensión
        name = getattr(f, 'name', '').lower()
        allowed_extensions = ('.png', '.jpg', '.jpeg')
        
        if not any(name.endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError(_('Solo se aceptan imágenes PNG o JPG'))
        
        # Validar tamaño (máximo 10MB)
        if f.size > 10 * 1024 * 1024:
            raise forms.ValidationError(_('La imagen no debe superar 10MB'))
        
        return f
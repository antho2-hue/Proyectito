"""Static admin forms for trayectoria models. Safe and non-invasive."""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CursoRealizado, Reconocimiento


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

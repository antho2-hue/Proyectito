"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from apps.perfil.views import hoja_vida_publica, cv_hacker_neon, descargar_cv_pdf, descargar_cv_completo_pdf, ver_foto_perfil, seleccionar_plantilla, fondo_professional, fondo_modern, selector_cv, descargar_cv_personalizado, descargar_cv_personalizado_plantilla
from apps.trayectoria.views import ver_certificado_curso, ver_certificado_reconocimiento, ver_certificado_experiencia, venta_garage, ver_imagen_producto, descargar_imagen_producto, ver_todos_los_productos

urlpatterns = [
    path('', hoja_vida_publica, name='hoja_vida_publica'),
    path('hacker-neon/', cv_hacker_neon, name='cv_hacker_neon'),
    path('descargar-cv/', descargar_cv_pdf, name='descargar_cv_pdf'),
    path('descargar-cv-completo/', descargar_cv_completo_pdf, name='descargar_cv_completo_pdf'),
    path('selector-cv/', selector_cv, name='selector_cv'),
    path('descargar-cv-personalizado/', descargar_cv_personalizado, name='descargar_cv_personalizado'),
    path('descargar-cv-personalizado-plantilla/', descargar_cv_personalizado_plantilla, name='descargar_cv_personalizado_plantilla'),

    # Venta de Garaje
    path('venta-garage/', venta_garage, name='venta_garage'),
    path('todos-los-productos/', ver_todos_los_productos, name='ver_todos_los_productos'),
    path('producto/<int:producto_id>/imagen/', ver_imagen_producto, name='ver_imagen_producto'),
    path('producto/<int:producto_id>/descargar-imagen/', descargar_imagen_producto, name='descargar_imagen_producto'),

    # Certificate proxy endpoints
    path('certificados/curso/<int:curso_id>/', ver_certificado_curso, name='ver_certificado_curso'),
    path('certificados/reconocimiento/<int:reconocimiento_id>/', ver_certificado_reconocimiento, name='ver_certificado_reconocimiento'),
    path('certificados/experiencia/<int:experiencia_id>/', ver_certificado_experiencia, name='ver_certificado_experiencia'),

    # Secure profile photo endpoint
    path('foto-perfil/', ver_foto_perfil, name='ver_foto_perfil'),
    path('fondo-professional/', fondo_professional, name='fondo_professional'),
    path('fondo-modern/', fondo_modern, name='fondo_modern'),
    path('seleccionar-plantilla/', seleccionar_plantilla, name='seleccionar_plantilla'),
    path('admin/', admin.site.urls),
]

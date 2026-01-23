from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseServerError
import os
from urllib.parse import urlparse
import mimetypes

from azure.storage.blob import BlobServiceClient

from .models import CursoRealizado, Reconocimiento, ExperienciaLaboral, VentaGarage
from apps.perfil.models import DatosPersonales


# Create your views here.

def _download_blob_from_url(blob_url: str):
    """Download blob bytes and return (bytes, filename).

    Expects blob_url like: https://<account>.blob.core.windows.net/<container>/<blob_path>
    """
    conn_str = os.environ.get('AZURE_STORAGE_CONNECTION_STRING') or os.environ.get('AZURE_CONNECTION_STRING')
    if not conn_str:
        raise RuntimeError('AZURE_STORAGE_CONNECTION_STRING is not set in environment')

    parsed = urlparse(blob_url)
    path = parsed.path.lstrip('/')
    if '/' not in path:
        raise ValueError('Invalid blob URL')
    container, blob_path = path.split('/', 1)

    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    blob_client = blob_service_client.get_blob_client(container=container, blob=blob_path)

    downloader = blob_client.download_blob()
    data = downloader.readall()
    filename = os.path.basename(blob_path)
    return data, filename


def _serve_pdf_response(data: bytes, filename: str, inline: bool = True):
    resp = HttpResponse(data, content_type='application/pdf')
    disposition = 'inline' if inline else 'attachment'
    resp['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    return resp


def ver_certificado_curso(request, curso_id):
    curso = get_object_or_404(CursoRealizado, pk=curso_id)
    if not curso.rutacertificado:
        return HttpResponse('No existe certificado para este curso.', status=404)

    download = request.GET.get('download', '0') in ('1', 'true', 'True', 'yes')

    try:
        data, filename = _download_blob_from_url(curso.rutacertificado)
        return _serve_pdf_response(data, filename, inline=not download)
    except Exception as exc:
        return HttpResponseServerError(f'Error al descargar el certificado: {exc}')


def ver_certificado_reconocimiento(request, reconocimiento_id):
    reconocimiento = get_object_or_404(Reconocimiento, pk=reconocimiento_id)
    if not reconocimiento.rutacertificado:
        return HttpResponse('No existe certificado para este reconocimiento.', status=404)

    download = request.GET.get('download', '0') in ('1', 'true', 'True', 'yes')

    try:
        data, filename = _download_blob_from_url(reconocimiento.rutacertificado)
        return _serve_pdf_response(data, filename, inline=not download)
    except Exception as exc:
        return HttpResponseServerError(f'Error al descargar el certificado: {exc}')


def ver_certificado_experiencia(request, experiencia_id):
    experiencia = get_object_or_404(ExperienciaLaboral, pk=experiencia_id)
    if not experiencia.rutacertificado:
        return HttpResponse('No existe certificado para esta experiencia.', status=404)

    download = request.GET.get('download', '0') in ('1', 'true', 'True', 'yes')

    try:
        data, filename = _download_blob_from_url(experiencia.rutacertificado)
        return _serve_pdf_response(data, filename, inline=not download)
    except Exception as exc:
        return HttpResponseServerError(f'Error al descargar el certificado: {exc}')


# ========================================
# NUEVAS VISTAS: VENTA DE GARAJE
# ========================================

def venta_garage(request):
    """
    Vista para mostrar todos los productos de venta de garaje.
    Solo muestra productos activos (activarparaqueseveaenfront=True)
    """
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        return render(request, 'trayectoria/venta_garage.html', {
            'perfil': None,
            'productos': [],
            'mensaje': 'Perfil no encontrado'
        })
    
    # Obtener todos los productos de venta de garaje activos
    productos = VentaGarage.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True
    ).order_by('nombreproducto')
    
    # Preparar datos para el template
    productos_data = []
    for producto in productos:
        tiene_img = bool(producto.rutaimagen)
        img_url = producto.rutaimagen if tiene_img else ""
        
        productos_data.append({
            'id': producto.idventagarage,
            'nombre': producto.nombreproducto,
            'descripcion': producto.descripcion,
            'estado_condicion': producto.estadoproducto,  # Bueno/Regular
            'estado_disponibilidad': producto.estado_disponibilidad,  # Disponible/Vendido
            'valor': producto.valordelbien,
            'tiene_imagen': tiene_img,
            'imagen_url': img_url,
            'fecha_publicacion': producto.fecha_publicacion,  # Añadido: fecha de publicación
        })
    
    context = {
        'perfil': perfil,
        'productos': productos_data,
        'total_productos': len(productos),
        'disponibles': sum(1 for p in productos_data if p['estado_disponibilidad'] == 'Disponible'),
    }
    
    return render(request, 'trayectoria/venta_garage.html', context)


def ver_imagen_producto(request, producto_id):
    """
    Vista proxy para servir la imagen del producto de venta de garaje.
    Similar a ver_foto_perfil, redirige desde Azure.
    """
    producto = get_object_or_404(VentaGarage, pk=producto_id)
    
    if not producto.rutaimagen:
        return HttpResponse('No existe imagen para este producto.', status=404)
    
    if not producto.activarparaqueseveaenfront:
        return HttpResponse('Este producto no está disponible.', status=404)
    
    try:
        data, filename = _download_blob_from_url(producto.rutaimagen)
    except Exception as exc:
        return HttpResponseServerError(f'Error al descargar la imagen: {exc}')
    
    # Determinar MIME type
    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = 'image/png'
    
    resp = HttpResponse(data, content_type=mime)
    resp['Content-Disposition'] = f'inline; filename="{filename}"'
    return resp


def descargar_imagen_producto(request, producto_id):
    """
    Vista para descargar la imagen del producto de venta de garaje.
    """
    producto = get_object_or_404(VentaGarage, pk=producto_id)
    
    if not producto.rutaimagen:
        return HttpResponse('No existe imagen para este producto.', status=404)
    
    if not producto.activarparaqueseveaenfront:
        return HttpResponse('Este producto no está disponible.', status=404)
    
    try:
        data, filename = _download_blob_from_url(producto.rutaimagen)
    except Exception as exc:
        return HttpResponseServerError(f'Error al descargar la imagen: {exc}')
    
    # Determinar MIME type
    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = 'image/png'
    
    resp = HttpResponse(data, content_type=mime)
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp

def ver_todos_los_productos(request):
    """
    Vista para mostrar todos los productos académicos y laborales.
    Similar a venta_garage pero para productos académicos y laborales.
    """
    from apps.perfil.models import DatosPersonales
    from apps.trayectoria.models import ProductoAcademico, ProductoLaboral
    
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        return render(request, 'trayectoria/todos_productos.html', {
            'perfil': None,
            'productos_academicos': [],
            'productos_laborales': [],
            'mensaje': 'Perfil no encontrado'
        })
    
    # Obtener todos los productos académicos
    productos_academicos = ProductoAcademico.objects.filter(
        idperfilconqueestaactivo=perfil
    ).order_by('nombrerecurso')
    
    # Obtener todos los productos laborales
    productos_laborales = ProductoLaboral.objects.filter(
        idperfilconqueestaactivo=perfil
    ).order_by('-fechaproducto')
    
    # Preparar datos para el template
    academicos_data = []
    for producto in productos_academicos:
        academicos_data.append({
            'id': producto.idproductoacademico,
            'nombre': producto.nombrerecurso,
            'clasificador': producto.clasificador,
            'descripcion': producto.descripcion,
        })
    
    laborales_data = []
    for producto in productos_laborales:
        laborales_data.append({
            'id': producto.idproductoslaborales,
            'nombre': producto.nombreproducto,
            'fecha': producto.fechaproducto,
            'descripcion': producto.descripcion,
        })
    
    context = {
        'perfil': perfil,
        'productos_academicos': academicos_data,
        'productos_laborales': laborales_data,
        'total_academicos': len(academicos_data),
        'total_laborales': len(laborales_data),
        'total_productos': len(academicos_data) + len(laborales_data),
    }
    
    return render(request, 'trayectoria/todos_productos.html', context)
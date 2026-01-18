from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseServerError
import os
from urllib.parse import urlparse

from azure.storage.blob import BlobServiceClient

from .models import CursoRealizado, Reconocimiento, ExperienciaLaboral


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


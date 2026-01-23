from django.shortcuts import render, get_object_or_404
from apps.perfil.models import DatosPersonales
from apps.trayectoria.models import (
    ExperienciaLaboral,
    CursoRealizado,
    Reconocimiento,
    ProductoAcademico,
    ProductoLaboral,
    VentaGarage,
)
from apps.trayectoria.views import _download_blob_from_url

from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
import os
import base64
import mimetypes
from django.urls import reverse
from weasyprint import HTML, CSS
from pypdf import PdfWriter, PdfReader


def _render_html_to_pdf(html: str, request) -> bytes:
    """Render HTML to PDF using WeasyPrint only.

    Returns raw PDF bytes. Raises RuntimeError with a helpful message on failure.
    """
    base_url = request.build_absolute_uri('/')
    try:
        # Force A4 and set reasonable margins (can be overridden by the template CSS)
        pdf_bytes = HTML(string=html, base_url=base_url).write_pdf(
            stylesheets=[CSS(string='@page { size: A4; margin: 15mm }')]
        )
        return pdf_bytes
    except Exception as exc:
        # Provide a clear error so the developer can install WeasyPrint system deps if needed
        raise RuntimeError(f'WeasyPrint PDF generation failed: {exc}')


def _prepare_html_for_pdf(html: str, request=None) -> str:
    """Ensure relative asset URLs become absolute so WeasyPrint can fetch them.

    This function intentionally does NOT modify CSS variables or strip fonts so the original
    template CSS and design are preserved exactly.
    """
    if request is not None:
        try:
            from django.urls import reverse

            # Convert profile photo proxy relative URL to absolute
            photo_url = request.build_absolute_uri(reverse('ver_foto_perfil'))
            html = html.replace('src="/foto-perfil/"', f'src="{photo_url}"')

            # Convert static references to absolute URLs
            static_base = request.build_absolute_uri('/static/')
            html = html.replace('src="/static/', f'src="{static_base}')
            html = html.replace('href="/static/', f'href="{static_base}')
        except Exception:
            pass

    return html


def get_pdf_css():
    """Return the PDF CSS contents for tests and debugging.

    Prefer the PDF-specific stylesheet under `static/perfil/css/pdf/cv_pdf.css`.
    """
    base_dir = os.path.dirname(__file__)
    candidates = [
        os.path.normpath(os.path.join(base_dir, 'static', 'perfil', 'css', 'pdf', 'cv_template_web.css')),
        os.path.normpath(os.path.join(base_dir, 'static', 'perfil', 'css', 'pdf', 'cv_pdf.css')),
        os.path.normpath(os.path.join(base_dir, 'static', 'perfil', 'css', 'cv_clean.css')),
    ]
    for css_path in candidates:
        try:
            with open(css_path, 'r', encoding='utf-8') as fh:
                return fh.read()
        except Exception:
            continue
    return ''





def hoja_vida_publica(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        # Create default profile if none exists with all required fields
        from datetime import date
        perfil = DatosPersonales.objects.create(
            nombres="Perfil",
            apellidos="Predeterminado",
            descripcionperfil="Perfil por defecto",
            perfilactivo=1,
            nacionalidad="Colombia",
            lugarnacimiento="Bogotá",
            fechanacimiento=date.today(),
            numerocedula="1234567890",
            sexo="H",
            estadocivil="Soltero",
            licenciaconducir="B1",
            telefonoconvencional="3001234567",
            telefonofijo="6012345678",
            direcciontrabajo="Calle 123",
            direcciondomiciliaria="Carrera 456",
            sitioweb="https://example.com"
        )

    # Obtain active experiences for the profile and group them by company (respetando control de visibilidad)
    visibilidad = getattr(perfil, 'visibilidad_cv', None)
    mostrar_experiencias = visibilidad.mostrar_experiencias if visibilidad else True
    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if mostrar_experiencias else ExperienciaLaboral.objects.none()

    # Order each company's experiences by start date desc and order companies
    # by the most recent experience date (desc).
    from django.db.models import Max

    companies = (
        experiencias_qs
        .values('nombrempresa')
        .annotate(latest=Max('fechainiciogestion'))
        .order_by('-latest')
    )

    experiencias = []
    for c in companies:
        company_name = c['nombrempresa']
        company_experiences = (
            experiencias_qs.filter(nombrempresa=company_name)
            .order_by('-fechainiciogestion')
        )
        experiencias.append({'empresa': company_name, 'experiencias': company_experiences})

    cursos = CursoRealizado.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechainicio') if visibilidad and visibilidad.mostrar_cursos else CursoRealizado.objects.none()

    reconocimientos = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechareconocimiento') if visibilidad and visibilidad.mostrar_reconocimientos else Reconocimiento.objects.none()

    productos_academicos = ProductoAcademico.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if visibilidad and visibilidad.mostrar_productos_academicos else ProductoAcademico.objects.none()

    productos_laborales = ProductoLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechaproducto') if visibilidad and visibilidad.mostrar_productos_laborales else ProductoLaboral.objects.none()

    # Convert profile photo to base64 for PDF embedding
    foto_base64 = None
    foto_perfil_proxy_url = None

    if getattr(perfil, 'foto_perfil_url', None):
        try:
            # Download the photo from Azure blob
            data, filename = _download_blob_from_url(perfil.foto_perfil_url)
            
            # Convert to base64
            foto_base64 = base64.b64encode(data).decode('utf-8')
            
            # Determine mime type
            mime, _ = mimetypes.guess_type(filename or 'photo.jpg')
            if not mime:
                mime = 'image/jpeg'
            
            # Create data URI for embedding in PDF
            foto_perfil_proxy_url = f"data:{mime};base64,{foto_base64}"
        except Exception as e:
            # Fallback: use proxy URL (works for web but not PDF)
            foto_perfil_proxy_url = f"{request.scheme}://{request.get_host()}/foto-perfil/"
            print(f"Error converting photo to base64: {e}")

    context = {
        'perfil': perfil,
        'visibilidad': visibilidad,
        'datos_personales': perfil,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'foto_perfil_proxy_url': foto_perfil_proxy_url,
    }

    # Public render - use new clean template
    response = render(request, 'perfil/cv_clean.html', context)
    return response


def cv_hacker_neon(request):
    """Vista especial del CV con estilo hacker neon completo."""
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        return render(request, 'perfil/error.html', {'error': 'Perfil no encontrado'})

    # Get all related data (same logic as hoja_vida_publica)
    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    )

    # Order each company's experiences by start date desc and order companies
    # by the most recent experience date (desc).
    from django.db.models import Max

    companies = (
        experiencias_qs
        .values('nombrempresa')
        .annotate(latest=Max('fechainiciogestion'))
        .order_by('-latest')
    )

    experiencias = []
    for c in companies:
        company_name = c['nombrempresa']
        company_experiences = (
            experiencias_qs.filter(nombrempresa=company_name)
            .order_by('-fechainiciogestion')
        )
        experiencias.append({'empresa': company_name, 'experiencias': company_experiences})

    cursos = CursoRealizado.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechainicio')

    reconocimientos = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechareconocimiento')

    productos_academicos = ProductoAcademico.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    )

    productos_laborales = ProductoLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechaproducto')

    # Get skills and interests
    habilidades = perfil.habilidades.split(',') if perfil.habilidades else []
    intereses = perfil.intereses if perfil.intereses else None

    context = {
        'perfil': perfil,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'habilidades': habilidades,
        'intereses': intereses,
    }

    # Provide the same photo proxy URL used by the PDF path so browsers can fetch the image
    foto_perfil_proxy_url = None
    if getattr(perfil, 'foto_perfil_url', None):
        foto_perfil_proxy_url = f"{request.scheme}://{request.get_host()}/foto-perfil/"
    context['foto_perfil_proxy_url'] = foto_perfil_proxy_url

    # Render with hacker neon template
    response = render(request, 'perfil/cv_hacker_neon.html', context)
    return response


def seleccionar_plantilla(request):
    """Vista para seleccionar plantilla de CV."""
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    return render(request, 'perfil/seleccionar_plantilla.html', {'perfil': perfil})


def descargar_cv_pdf(request):
    """Generate a PDF of the public CV using the selected template."""
    from django.http import HttpResponse

    # Obtener plantilla seleccionada (por defecto: professional)
    plantilla = request.GET.get('plantilla', 'professional')

    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        # Create default profile if none exists with all required fields
        from datetime import date
        try:
            perfil = DatosPersonales.objects.create(
                nombres="Perfil",
                apellidos="Predeterminado",
                descripcionperfil="Perfil por defecto",
                perfilactivo=1,
                nacionalidad="Colombia",
                lugarnacimiento="Bogotá",
                fechanacimiento=date.today(),
                numerocedula="1234567890",
                sexo="H",
                estadocivil="Soltero",
                licenciaconducir="B1",
                telefonoconvencional="3001234567",
                telefonofijo="6012345678",
                direcciontrabajo="Calle 123",
                direcciondomiciliaria="Carrera 456",
                sitioweb="https://example.com"
            )
        except Exception as e:
            return HttpResponse(f'Error creando perfil: {str(e)}', status=500)

    # Respeta controles de visibilidad del admin
    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if visibilidad.mostrar_experiencias else ExperienciaLaboral.objects.none()

    from django.db.models import Max

    companies = (
        experiencias_qs
        .values('nombrempresa')
        .annotate(latest=Max('fechainiciogestion'))
        .order_by('-latest')
    )

    experiencias = []
    for c in companies:
        company_name = c['nombrempresa']
        company_experiences = (
            experiencias_qs.filter(nombrempresa=company_name)
            .order_by('-fechainiciogestion')
        )
        experiencias.append({'empresa': company_name, 'experiencias': company_experiences})

    cursos = CursoRealizado.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechainicio')

    reconocimientos = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechareconocimiento') if visibilidad and visibilidad.mostrar_reconocimientos else Reconocimiento.objects.none()

    productos_academicos = ProductoAcademico.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if visibilidad and visibilidad.mostrar_productos_academicos else ProductoAcademico.objects.none()

    productos_laborales = ProductoLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechaproducto') if visibilidad and visibilidad.mostrar_productos_laborales else ProductoLaboral.objects.none()

    # Convert profile photo to base64 for PDF embedding
    foto_perfil_proxy_url = None
    if getattr(perfil, 'foto_perfil_url', None):
        try:
            # Download the photo from Azure blob
            data, filename = _download_blob_from_url(perfil.foto_perfil_url)

            # Convert to base64
            foto_base64 = base64.b64encode(data).decode('utf-8')

            # Determine mime type
            mime, _ = mimetypes.guess_type(filename or 'photo.jpg')
            if not mime:
                mime = 'image/jpeg'

            # Create data URI for embedding in PDF
            foto_perfil_proxy_url = f"data:{mime};base64,{foto_base64}"
        except Exception as e:
            # Fallback: use proxy URL (works for web but not PDF)
            foto_perfil_proxy_url = f"{request.scheme}://{request.get_host()}/foto-perfil/"
            print(f"Error converting photo to base64: {e}")

    # Preparar intereses
    intereses_list = []
    if getattr(perfil, 'intereses', None):
        intereses_list = [i.strip() for i in perfil.intereses.split(',') if i.strip()]

    context = {
        'perfil': perfil,
        'datos_personales': perfil,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'foto_perfil_proxy_url': foto_perfil_proxy_url,
        'certificates': [],
        'intereses_list': intereses_list,
    }

    # Seleccionar template según plantilla
    if plantilla == 'modern':
        template_name = 'perfil/pdf/cv_modern_clean.html'
        html = render_to_string(template_name, context, request=request)
        # No aplicar _prepare_html_for_pdf para mantener estilos inline
        pdf_bytes = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
    else:
        # Template professional por defecto
        template_name = 'perfil/pdf/cv_template_web.html'
        html = render_to_string(template_name, context, request=request)
        html = _prepare_html_for_pdf(html, request)

        try:
            # Leer el CSS
            base_dir = os.path.dirname(__file__)
            css_path = os.path.join(base_dir, 'static', 'perfil', 'css', 'pdf', 'cv_template_web.css')

            with open(css_path, 'r', encoding='utf-8') as f:
                css_text = f.read()

            pdf_bytes = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(
                stylesheets=[CSS(string=css_text)]
            )
        except Exception as e:
            return HttpResponse(f'Error generating PDF: {str(e)}', status=500)

    # After generating the CV PDF, append any uploaded certificates (courses, experiences, recognitions)
    try:
        from pypdf import PdfMerger

        merger = PdfMerger()
        merger.append(BytesIO(pdf_bytes))

        cursos_with_cert = CursoRealizado.objects.filter(idperfilconqueestaactivo=perfil).exclude(rutacertificado__isnull=True).exclude(rutacertificado__exact='').order_by('pk')
        experiencias_with_cert = ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil).exclude(rutacertificado__isnull=True).exclude(rutacertificado__exact='').order_by('pk')
        reconocimientos_with_cert = Reconocimiento.objects.filter(idperfilconqueestaactivo=perfil).exclude(rutacertificado__isnull=True).exclude(rutacertificado__exact='').order_by('pk')

        def append_certificate(cert_bytes, filename='', titulo=''):
            lower = (filename or '').lower()
            try:
                # If the certificate is an image, render it inside the wrapper with the title
                if lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    b64 = base64.b64encode(cert_bytes).decode('ascii')
                    mime, _ = mimetypes.guess_type(filename)
                    if not mime:
                        mime = 'image/png'
                    data_uri = f"data:{mime};base64,{b64}"
                    cert_html = render_to_string('perfil/pdf/certificado_wrapper.html', {
                        'titulo': titulo or '',
                        'image_data_uri': data_uri,
                    })
                    cert_html = _prepare_html_for_pdf(cert_html, request)
                    cert_pdf = HTML(string=cert_html, base_url=request.build_absolute_uri('/')).write_pdf(
                        stylesheets=[CSS(string='@page { size: A4; margin: 15mm }')]
                    )
                    merger.append(BytesIO(cert_pdf))
                else:
                    # For PDFs, try to overlay the title on the first certificate page.
                    try:
                        title_html = render_to_string('perfil/pdf/certificado_wrapper.html', {
                            'titulo': titulo or '',
                            'image_data_uri': '__title_only__',
                        })
                        title_html = _prepare_html_for_pdf(title_html, request)
                        title_pdf_bytes = HTML(string=title_html, base_url=request.build_absolute_uri('/')).write_pdf(
                            stylesheets=[CSS(string='@page { size: A4; margin: 15mm }')]
                        )

                        cert_reader = PdfReader(BytesIO(cert_bytes))
                        title_reader = PdfReader(BytesIO(title_pdf_bytes))
                        if len(cert_reader.pages) == 0:
                            return

                        # Attempt to merge overlay onto the certificate's first page
                        try:
                            first = cert_reader.pages[0]
                            if len(title_reader.pages) > 0:
                                first.merge_page(title_reader.pages[0])
                            writer = PdfWriter()
                            writer.add_page(first)
                            for p in cert_reader.pages[1:]:
                                writer.add_page(p)
                            buf = BytesIO()
                            writer.write(buf)
                            merger.append(BytesIO(buf.getvalue()))
                        except Exception:
                            # Fallback: prepend title pages then certificate pages
                            writer = PdfWriter()
                            for p in title_reader.pages:
                                writer.add_page(p)
                            for p in cert_reader.pages:
                                writer.add_page(p)
                            buf = BytesIO()
                            writer.write(buf)
                            merger.append(BytesIO(buf.getvalue()))
                    except Exception:
                        # fallback: append original bytes
                        merger.append(BytesIO(cert_bytes))
            except Exception:
                return

        for curso in cursos_with_cert:
            try:
                cert_url = getattr(curso, 'rutacertificado', None)
                if cert_url:
                    cert_bytes, filename = _download_blob_from_url(cert_url)
                    title = f"Cursos realizados - {getattr(curso, 'nombrecurso', '')}"
                    append_certificate(cert_bytes, filename or '', title)
            except Exception:
                continue

        for exp in experiencias_with_cert:
            try:
                cert_url = getattr(exp, 'rutacertificado', None)
                if cert_url:
                    cert_bytes, filename = _download_blob_from_url(cert_url)
                    title = f"Experiencia laboral - {getattr(exp, 'cargodesempenado', '')} en {getattr(exp, 'nombrempresa', '')}"
                    append_certificate(cert_bytes, filename or '', title)
            except Exception:
                continue

        for recon in reconocimientos_with_cert:
            try:
                cert_url = getattr(recon, 'rutacertificado', None)
                if cert_url:
                    cert_bytes, filename = _download_blob_from_url(cert_url)
                    title = f"Reconocimiento - {getattr(recon, 'descripcionreconocimiento', '')}"
                    append_certificate(cert_bytes, filename or '', title)
            except Exception:
                continue

        out = BytesIO()
        merger.write(out)
        merger.close()
        out.seek(0)
        merged_bytes = out.getvalue()
        response = HttpResponse(merged_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cv_{plantilla}_completo.pdf"'
        return response
    except Exception:
        # If merging fails for any reason, return the original CV PDF
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cv_{plantilla}.pdf"'
        return response


def descargar_cv_completo_pdf(request):
    """Generate a complete PDF of the CV with selected certificates."""
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        from datetime import date
        try:
            perfil = DatosPersonales.objects.create(
                nombres="Perfil",
                apellidos="Predeterminado",
                descripcionperfil="Perfil por defecto",
                perfilactivo=1,
                nacionalidad="Colombia",
                lugarnacimiento="Bogotá",
                fechanacimiento=date.today(),
                numerocedula="1234567890",
                sexo="H",
                estadocivil="Soltero",
                licenciaconducir="B1",
                telefonoconvencional="3001234567",
                telefonofijo="6012345678",
                direcciontrabajo="Calle 123",
                direcciondomiciliaria="Carrera 456",
                sitioweb="https://example.com"
            )
        except Exception as e:
            return HttpResponse(f'Error creando perfil: {str(e)}', status=500)

    # Respeta controles de visibilidad del admin
    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if visibilidad.mostrar_experiencias else ExperienciaLaboral.objects.none()

    from django.db.models import Max

    companies = (
        experiencias_qs
        .values('nombrempresa')
        .annotate(latest=Max('fechainiciogestion'))
        .order_by('-latest')
    )

    experiencias = []
    for c in companies:
        company_name = c['nombrempresa']
        company_experiences = (
            experiencias_qs.filter(nombrempresa=company_name)
            .order_by('-fechainiciogestion')
        )
        experiencias.append({'empresa': company_name, 'experiencias': company_experiences})

    cursos = CursoRealizado.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechainicio') if visibilidad and visibilidad.mostrar_cursos else CursoRealizado.objects.none()

    reconocimientos = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechareconocimiento') if visibilidad and visibilidad.mostrar_reconocimientos else Reconocimiento.objects.none()

    productos_academicos = ProductoAcademico.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if visibilidad and visibilidad.mostrar_productos_academicos else ProductoAcademico.objects.none()

    productos_laborales = ProductoLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechaproducto') if visibilidad and visibilidad.mostrar_productos_laborales else ProductoLaboral.objects.none()

    ventas_garage = VentaGarage.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('nombreproducto')
    
    # ===============================
# 1. Generar PDF base del CV
# ===============================

    # Generar HTML del CV base
    context = {
        'perfil': perfil,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas_garage': ventas_garage,
    }

    html = render_to_string(
        'perfil/pdf/cv_template_web.html',
        context,
        request=request
    )

    html = _prepare_html_for_pdf(html, request)

    css_path = os.path.join(
        os.path.dirname(__file__),
        'static',
        'perfil',
        'css',
        'pdf',
        'cv_template_web.css'
    )

    with open(css_path, 'r', encoding='utf-8') as f:
        css_text = f.read()

    pdf_bytes = HTML(
        string=html,
        base_url=request.build_absolute_uri('/')
    ).write_pdf(
        stylesheets=[CSS(string=css_text)]
    )


    # Collect all available certificates for selection
    certificados_meta = []

    # Add certificates from experiences
    for exp in experiencias_qs:
        if getattr(exp, 'rutacertificado', None):
            certificados_meta.append({
                'model': exp,
                'titulo': f"Certificado Experiencia - {exp.cargodesempenado} en {exp.nombrempresa}",
                'tipo': 'experiencia'
            })

    # Add certificates from courses
    for curso in cursos:
        if getattr(curso, 'rutacertificado', None):
            certificados_meta.append({
                'model': curso,
                'titulo': f"Certificado Curso - {curso.nombrecurso}",
                'tipo': 'curso'
            })

    # Add certificates from recognitions
    for recon in reconocimientos:
        if getattr(recon, 'rutacertificado', None):
            certificados_meta.append({
                'model': recon,
                'titulo': f"Certificado Reconocimiento - {recon.descripcionreconocimiento}",
                'tipo': 'reconocimiento'
            })

    # Determine which certificates to include based on GET params (supports individual selection)
    requested = request.GET.getlist('certificados')
    check_all = request.GET.get('check_all') or request.GET.get('select_all')

    if check_all:
        # CHECK ALL: Include ALL certificates from all three tables
        selected_meta = certificados_meta
    elif requested:
        # requested values are like 'experiencia_5' or 'curso_3' or 'reconocimiento_2'
        selected_meta = []
        for token in requested:
            parts = token.split('_')
            if len(parts) != 2:
                continue
            tipo, pk = parts[0], parts[1]
            for cm in certificados_meta:
                model = cm['model']
                try:
                    if str(getattr(model, 'pk', '')) == pk:
                        selected_meta.append(cm)
                        break
                except Exception:
                    continue
    else:
        # No certificates requested
        selected_meta = []

    # If there are certificates selected, merge them into the PDF
    if selected_meta:
        writer = PdfWriter()

        # Add all CV pages
        try:
            cv_reader = PdfReader(BytesIO(pdf_bytes))
            for page in cv_reader.pages:
                writer.add_page(page)
        except Exception as e:
            return HttpResponse(f'Error processing CV PDF: {str(e)}', status=500)

        # Add each selected certificate
        for cert_meta in selected_meta:
            try:
                model = cert_meta['model']
                titulo = cert_meta['titulo']

                # Get the blob URL from the model
                cert_url = getattr(model, 'rutacertificado', None)
                if cert_url:
                    # Download certificate from Azure
                    cert_bytes, filename = _download_blob_from_url(cert_url)
                    filename = filename or ''
                    lower = filename.lower()

                    # If image -> embed as preview page
                    if lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        b64 = base64.b64encode(cert_bytes).decode('ascii')
                        mime, _ = mimetypes.guess_type(filename)
                        if not mime:
                            mime = 'image/png'
                        data_uri = f"data:{mime};base64,{b64}"

                        cert_html = render_to_string('perfil/pdf/certificado_wrapper.html', {
                            'titulo': titulo,
                            'image_data_uri': data_uri,
                        })
                        cert_html = _prepare_html_for_pdf(cert_html, request)
                        try:
                            cert_pdf_bytes = HTML(string=cert_html, base_url=request.build_absolute_uri('/')).write_pdf(
                                stylesheets=[CSS(string='@page { size: A4; margin: 15mm }')]
                            )
                            cert_reader = PdfReader(BytesIO(cert_pdf_bytes))
                            for page in cert_reader.pages:
                                writer.add_page(page)
                        except Exception:
                            pass
                    else:
                        # Treat as PDF: overlay the title onto the first page of the certificate
                        title_html = render_to_string('perfil/pdf/certificado_wrapper.html', {
                            'titulo': titulo,
                            'image_data_uri': '__title_only__',
                        })
                        title_html = _prepare_html_for_pdf(title_html, request)
                        try:
                            title_pdf_bytes = HTML(string=title_html, base_url=request.build_absolute_uri('/')).write_pdf(
                                stylesheets=[CSS(string='@page { size: A4; margin: 15mm }')]
                            )
                            title_reader = PdfReader(BytesIO(title_pdf_bytes))
                        except Exception:
                            title_reader = None

                        try:
                            cert_reader = PdfReader(BytesIO(cert_bytes))
                            if len(cert_reader.pages) == 0:
                                continue

                            # Try overlaying the title onto the first certificate page
                            try:
                                if title_reader and len(title_reader.pages) > 0:
                                    cert_first = cert_reader.pages[0]
                                    cert_first.merge_page(title_reader.pages[0])
                                    writer.add_page(cert_first)
                                    for p in cert_reader.pages[1:]:
                                        writer.add_page(p)
                                else:
                                    for p in cert_reader.pages:
                                        writer.add_page(p)
                            except Exception:
                                # Fallback: append title pages first, then certificate pages
                                if title_reader and len(title_reader.pages) > 0:
                                    for p in title_reader.pages:
                                        writer.add_page(p)
                                for p in cert_reader.pages:
                                    writer.add_page(p)
                        except Exception:
                            pass
            except Exception:
                pass

        # Write the final merged PDF
        out_buf = BytesIO()
        writer.write(out_buf)
        response = HttpResponse(out_buf.getvalue(), content_type='application/pdf')
    else:
        # No certificates, just return CV
        response = HttpResponse(pdf_bytes, content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename="cv_completo.pdf"'
    return response


# --- Secure photo proxy view ---
from apps.trayectoria.views import _download_blob_from_url


def ver_foto_perfil(request):
    """Proxy view to serve the profile photo from Azure without exposing the blob URL."""
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        # Create default profile if none exists with all required fields
        from datetime import date
        try:
            perfil = DatosPersonales.objects.create(
                nombres="Perfil",
                apellidos="Predeterminado",
                descripcionperfil="Perfil por defecto",
                perfilactivo=1,
                nacionalidad="Colombia",
                lugarnacimiento="Bogotá",
                fechanacimiento=date.today(),
                numerocedula="1234567890",
                sexo="H",
                estadocivil="Soltero",
                licenciaconducir="B1",
                telefonoconvencional="3001234567",
                telefonofijo="6012345678",
                direcciontrabajo="Calle 123",
                direcciondomiciliaria="Carrera 456",
                sitioweb="https://example.com"
            )
        except Exception as e:
            return HttpResponse(f'Error creando perfil: {str(e)}', status=500)
    blob_url = getattr(perfil, 'foto_perfil_url', None)
    if not blob_url:
        return HttpResponse('No profile photo available.', status=404)

    # Primary attempt: use existing helper that downloads from Azure blobs.
    try:
        data, filename = _download_blob_from_url(blob_url)
    except Exception:
        # Fallback: try a direct HTTP fetch (works for public URLs or SAS URLs).
        try:
            from urllib.request import urlopen
            from urllib.parse import urlparse

            resp_fetch = urlopen(blob_url)
            data = resp_fetch.read()
            filename = os.path.basename(urlparse(blob_url).path) or 'profile.png'
        except Exception as exc:
            return HttpResponse(f'Error fetching profile photo: {exc}', status=500)

    # Guess mime type from filename; default to PNG to preserve previous behavior
    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = 'image/png'

    resp = HttpResponse(data, content_type=mime)
    resp['Content-Disposition'] = f'inline; filename="{filename}"'
    return resp


def fondo_professional(request):
    """Proxy to serve the professional template background image stored in Azure."""
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        return HttpResponse('No profile found.', status=404)
    blob_url = getattr(perfil, 'fondo_professional_url', None)
    if not blob_url:
        return HttpResponse('No background uploaded.', status=404)

    try:
        data, filename = _download_blob_from_url(blob_url)
    except Exception:
        try:
            from urllib.request import urlopen
            from urllib.parse import urlparse
            resp_fetch = urlopen(blob_url)
            data = resp_fetch.read()
            filename = os.path.basename(urlparse(blob_url).path) or 'background.png'
        except Exception as exc:
            return HttpResponse(f'Error fetching background: {exc}', status=500)

    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = 'image/png'
    resp = HttpResponse(data, content_type=mime)
    resp['Content-Disposition'] = f'inline; filename="{filename}"'
    return resp


def fondo_modern(request):
    """Proxy to serve the modern template background image stored in Azure."""
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        return HttpResponse('No profile found.', status=404)
    blob_url = getattr(perfil, 'fondo_modern_url', None)
    if not blob_url:
        return HttpResponse('No background uploaded.', status=404)

    try:
        data, filename = _download_blob_from_url(blob_url)
    except Exception:
        try:
            from urllib.request import urlopen
            from urllib.parse import urlparse
            resp_fetch = urlopen(blob_url)
            data = resp_fetch.read()
            filename = os.path.basename(urlparse(blob_url).path) or 'background.png'
        except Exception as exc:
            return HttpResponse(f'Error fetching background: {exc}', status=500)

    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = 'image/png'
    resp = HttpResponse(data, content_type=mime)
    resp['Content-Disposition'] = f'inline; filename="{filename}"'
    return resp


# ========================================
# NUEVA FUNCIONALIDAD: SELECTOR DE CV
# ========================================

def selector_cv(request):
    """
    Vista para seleccionar qué secciones incluir en el CV personalizado.
    Muestra un formulario interactivo con checkboxes para cada sección.
    """
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        from datetime import date
        perfil = DatosPersonales.objects.create(
            nombres="Perfil",
            apellidos="Predeterminado",
            descripcionperfil="Perfil por defecto",
            perfilactivo=1,
            nacionalidad="Colombia",
            lugarnacimiento="Bogotá",
            fechanacimiento=date.today(),
            numerocedula="1234567890",
            sexo="H",
            estadocivil="Soltero",
            licenciaconducir="B1",
            telefonoconvencional="3001234567",
            telefonofijo="6012345678",
            direcciontrabajo="Calle 123",
            direcciondomiciliaria="Carrera 456",
            sitioweb="https://example.com"
        )

    # Obtener controles de visibilidad
    visibilidad = getattr(perfil, 'visibilidad_cv', None)

    # Obtener todas las secciones de datos (respeta controles de admin)
    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if visibilidad and visibilidad.mostrar_experiencias else ExperienciaLaboral.objects.none()

    from django.db.models import Max

    companies = (
        experiencias_qs
        .values('nombrempresa')
        .annotate(latest=Max('fechainiciogestion'))
        .order_by('-latest')
    )

    experiencias = []
    for c in companies:
        company_name = c['nombrempresa']
        company_experiences = (
            experiencias_qs.filter(nombrempresa=company_name)
            .order_by('-fechainiciogestion')
        )
        experiencias.append({'empresa': company_name, 'experiencias': company_experiences})

    cursos = CursoRealizado.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechainicio') if visibilidad and visibilidad.mostrar_cursos else CursoRealizado.objects.none()

    reconocimientos = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechareconocimiento') if visibilidad and visibilidad.mostrar_reconocimientos else Reconocimiento.objects.none()

    productos_academicos = ProductoAcademico.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if visibilidad and visibilidad.mostrar_productos_academicos else ProductoAcademico.objects.none()

    productos_laborales = ProductoLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechaproducto') if visibilidad and visibilidad.mostrar_productos_laborales else ProductoLaboral.objects.none()

    # Preparar foto para mostrar
    foto_perfil_proxy_url = None
    if getattr(perfil, 'foto_perfil_url', None):
        foto_perfil_proxy_url = f"{request.scheme}://{request.get_host()}/foto-perfil/"

    context = {
        'perfil': perfil,
        'foto_perfil_proxy_url': foto_perfil_proxy_url,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        # Información sobre qué secciones tienen datos
        'tiene_experiencias': len(experiencias) > 0,
        'tiene_cursos': len(cursos) > 0,
        'tiene_reconocimientos': len(reconocimientos) > 0,
        'tiene_productos_academicos': len(productos_academicos) > 0,
        'tiene_productos_laborales': len(productos_laborales) > 0,
    }

    return render(request, 'perfil/selector_cv.html', context)


def descargar_cv_personalizado(request):
    """
    Genera un PDF del CV con solo las secciones seleccionadas.
    Las secciones se envían como parámetros GET en el formato:
    - datos_personales=on
    - experiencias_laborales=on
    - cursos=on
    - reconocimientos=on
    - productos_academicos=on
    - productos_laborales=on
    
    (Esta función es para compatibilidad hacia atrás - usa Professional por defecto)
    """
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        from datetime import date
        perfil = DatosPersonales.objects.create(
            nombres="Perfil",
            apellidos="Predeterminado",
            descripcionperfil="Perfil por defecto",
            perfilactivo=1,
            nacionalidad="Colombia",
            lugarnacimiento="Bogotá",
            fechanacimiento=date.today(),
            numerocedula="1234567890",
            sexo="H",
            estadocivil="Soltero",
            licenciaconducir="B1",
            telefonoconvencional="3001234567",
            telefonofijo="6012345678",
            direcciontrabajo="Calle 123",
            direcciondomiciliaria="Carrera 456",
            sitioweb="https://example.com"
        )

    # Obtener secciones seleccionadas desde GET
    incluir_datos_personales = request.GET.get('datos_personales') == 'on'
    incluir_experiencias = request.GET.get('experiencias_laborales') == 'on'
    incluir_cursos = request.GET.get('cursos') == 'on'
    incluir_reconocimientos = request.GET.get('reconocimientos') == 'on'
    incluir_productos_academicos = request.GET.get('productos_academicos') == 'on'
    incluir_productos_laborales = request.GET.get('productos_laborales') == 'on'

    # Obtener todas las secciones
    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if incluir_experiencias else ExperienciaLaboral.objects.none()

    from django.db.models import Max

    companies = (
        experiencias_qs
        .values('nombrempresa')
        .annotate(latest=Max('fechainiciogestion'))
        .order_by('-latest')
    )

    experiencias = []
    for c in companies:
        company_name = c['nombrempresa']
        company_experiences = (
            experiencias_qs.filter(nombrempresa=company_name)
            .order_by('-fechainiciogestion')
        )
        experiencias.append({'empresa': company_name, 'experiencias': company_experiences})

    cursos = CursoRealizado.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechainicio') if incluir_cursos else CursoRealizado.objects.none()

    reconocimientos = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechareconocimiento') if incluir_reconocimientos else Reconocimiento.objects.none()

    productos_academicos = ProductoAcademico.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if incluir_productos_academicos else ProductoAcademico.objects.none()

    productos_laborales = ProductoLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechaproducto') if incluir_productos_laborales else ProductoLaboral.objects.none()

    # Preparar foto
    foto_perfil_proxy_url = None
    if getattr(perfil, 'foto_perfil_url', None):
        try:
            data, filename = _download_blob_from_url(perfil.foto_perfil_url)
            foto_base64 = base64.b64encode(data).decode('utf-8')
            mime, _ = mimetypes.guess_type(filename or 'photo.jpg')
            if not mime:
                mime = 'image/jpeg'
            foto_perfil_proxy_url = f"data:{mime};base64,{foto_base64}"
        except Exception:
            foto_perfil_proxy_url = f"{request.scheme}://{request.get_host()}/foto-perfil/"

    context = {
        'perfil': perfil,
        'datos_personales': perfil if incluir_datos_personales else None,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'foto_perfil_proxy_url': foto_perfil_proxy_url,
    }

    # Usar template PDF existente
    html = render_to_string('perfil/pdf/cv_template_web.html', context, request=request)
    html = _prepare_html_for_pdf(html, request)

    try:
        base_dir = os.path.dirname(__file__)
        css_path = os.path.join(base_dir, 'static', 'perfil', 'css', 'pdf', 'cv_template_web.css')

        with open(css_path, 'r', encoding='utf-8') as f:
            css_text = f.read()

        pdf_bytes = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(
            stylesheets=[CSS(string=css_text)]
        )
    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}', status=500)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cv_personalizado.pdf"'
    return response


def descargar_cv_personalizado_plantilla(request):
    """
    Genera un PDF del CV personalizado con las secciones seleccionadas.
    Permite elegir entre 'professional' y 'modern' plantillas.
    
    Las secciones se envían como parámetros GET:
    - plantilla=professional|modern
    - datos_personales=on
    - experiencias_laborales=on
    - cursos=on
    - reconocimientos=on
    - productos_academicos=on
    - productos_laborales=on
    """
    plantilla = request.GET.get('plantilla', 'professional')
    
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        from datetime import date
        perfil = DatosPersonales.objects.create(
            nombres="Perfil",
            apellidos="Predeterminado",
            descripcionperfil="Perfil por defecto",
            perfilactivo=1,
            nacionalidad="Colombia",
            lugarnacimiento="Bogotá",
            fechanacimiento=date.today(),
            numerocedula="1234567890",
            sexo="H",
            estadocivil="Soltero",
            licenciaconducir="B1",
            telefonoconvencional="3001234567",
            telefonofijo="6012345678",
            direcciontrabajo="Calle 123",
            direcciondomiciliaria="Carrera 456",
            sitioweb="https://example.com"
        )

    # Obtener secciones seleccionadas desde GET
    incluir_datos_personales = request.GET.get('datos_personales') == 'on'
    incluir_experiencias = request.GET.get('experiencias_laborales') == 'on'
    incluir_cursos = request.GET.get('cursos') == 'on'
    incluir_reconocimientos = request.GET.get('reconocimientos') == 'on'
    incluir_productos_academicos = request.GET.get('productos_academicos') == 'on'
    incluir_productos_laborales = request.GET.get('productos_laborales') == 'on'

    # Combina las selecciones del usuario con los controles del admin
    # Solo muestra si AMBOS lo permiten
    incluir_experiencias = incluir_experiencias and visibilidad.mostrar_experiencias
    incluir_cursos = incluir_cursos and visibilidad.mostrar_cursos
    incluir_reconocimientos = incluir_reconocimientos and visibilidad.mostrar_reconocimientos
    incluir_productos_academicos = incluir_productos_academicos and visibilidad.mostrar_productos_academicos
    incluir_productos_laborales = incluir_productos_laborales and visibilidad.mostrar_productos_laborales
    incluir_datos_personales = incluir_datos_personales and visibilidad.mostrar_datos_personales

    # Obtener todas las secciones basadas en las selecciones
    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if incluir_experiencias else ExperienciaLaboral.objects.none()

    from django.db.models import Max

    companies = (
        experiencias_qs
        .values('nombrempresa')
        .annotate(latest=Max('fechainiciogestion'))
        .order_by('-latest')
    )

    experiencias = []
    for c in companies:
        company_name = c['nombrempresa']
        company_experiences = (
            experiencias_qs.filter(nombrempresa=company_name)
            .order_by('-fechainiciogestion')
        )
        experiencias.append({'empresa': company_name, 'experiencias': company_experiences})

    cursos = CursoRealizado.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechainicio') if incluir_cursos else CursoRealizado.objects.none()

    reconocimientos = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechareconocimiento') if incluir_reconocimientos else Reconocimiento.objects.none()

    productos_academicos = ProductoAcademico.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ) if incluir_productos_academicos else ProductoAcademico.objects.none()

    productos_laborales = ProductoLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechaproducto') if incluir_productos_laborales else ProductoLaboral.objects.none()

    # Preparar foto
    foto_perfil_proxy_url = None
    if getattr(perfil, 'foto_perfil_url', None):
        try:
            data, filename = _download_blob_from_url(perfil.foto_perfil_url)
            foto_base64 = base64.b64encode(data).decode('utf-8')
            mime, _ = mimetypes.guess_type(filename or 'photo.jpg')
            if not mime:
                mime = 'image/jpeg'
            foto_perfil_proxy_url = f"data:{mime};base64,{foto_base64}"
        except Exception:
            foto_perfil_proxy_url = f"{request.scheme}://{request.get_host()}/foto-perfil/"

    # Preparar intereses
    intereses_list = []
    if getattr(perfil, 'intereses', None):
        intereses_list = [i.strip() for i in perfil.intereses.split(',') if i.strip()]

    context = {
        'perfil': perfil,
        'datos_personales': perfil if incluir_datos_personales else None,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'foto_perfil_proxy_url': foto_perfil_proxy_url,
        'certificates': [],
        'intereses_list': intereses_list,
    }

    # Seleccionar template según plantilla
    if plantilla == 'modern':
        template_name = 'perfil/pdf/cv_modern_clean.html'
        html = render_to_string(template_name, context, request=request)
        # No aplicar _prepare_html_for_pdf para mantener estilos inline
        pdf_bytes = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
        filename = 'cv_modern_personalizado.pdf'
    else:
        # Template professional por defecto
        template_name = 'perfil/pdf/cv_template_web.html'
        html = render_to_string(template_name, context, request=request)
        html = _prepare_html_for_pdf(html, request)

        try:
            base_dir = os.path.dirname(__file__)
            css_path = os.path.join(base_dir, 'static', 'perfil', 'css', 'pdf', 'cv_template_web.css')

            with open(css_path, 'r', encoding='utf-8') as f:
                css_text = f.read()

            pdf_bytes = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(
                stylesheets=[CSS(string=css_text)]
            )
        except Exception as e:
            return HttpResponse(f'Error generating PDF: {str(e)}', status=500)
        
        filename = 'cv_professional_personalizado.pdf'

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response




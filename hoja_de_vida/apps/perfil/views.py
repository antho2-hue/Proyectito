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

    # Obtain active experiences for the profile and group them by company.
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

    # Venta Garage: visible records ordered by product name (ascending)
    ventas_garage = VentaGarage.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('nombreproducto')

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
        'datos_personales': perfil,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas_garage': ventas_garage,
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

    ventas_garage = VentaGarage.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('nombreproducto')

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
        'ventas_garage': ventas_garage,
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

    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    )

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

    ventas_garage = VentaGarage.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('nombreproducto')

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

    context = {
        'perfil': perfil,
        'datos_personales': perfil,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas_garage': ventas_garage,
        'foto_perfil_proxy_url': foto_perfil_proxy_url,
        'certificates': [],
    }

    # Render the PDF-specific template
    html = render_to_string('perfil/pdf/cv_template_web.html', context, request=request)
    html = _prepare_html_for_pdf(html, request)

    try:
        # Seleccionar CSS según plantilla
        if plantilla == 'modern':
            css_file = 'cv_modern_clean.css'
        else:  # professional por defecto
            css_file = 'cv_template_web.css'

        # Leer el CSS
        base_dir = os.path.dirname(__file__)
        css_path = os.path.join(base_dir, 'static', 'perfil', 'css', 'pdf', css_file)

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

    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    )

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


# Hoja de Vida (Django Project)

Proyecto Django minimal para una hoja de vida profesional.

## Quick start

1. Activate the virtual environment (Windows PowerShell):

   ```powershell
   C:\Users\HP\Desktop\Proyecto\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies (already done by this setup):

   ```powershell
   pip install -r requirements.txt  # if you add one
   ```

3. Run the development server:

   ```powershell
   python manage.py runserver
   ```

Notes:
- No models or views created yet. Create apps inside the `apps/` package and add them to `INSTALLED_APPS` in `config/settings.py`.
- Apps created in this setup:
  - `apps.perfil` — personal profile data
  - `apps.trayectoria` — work experience, education, courses
  - `apps.documentos` — PDF documents (certificates, diplomas)
  - `apps.accounts` — admin access and authentication

Models added (ready for migrations):
- `apps.perfil.models.DatosPersonales` -> table `DATOSPERSONALES`
- `apps.trayectoria.models.ExperienciaLaboral` -> table `EXPERIENCIALABORAL`
- `apps.trayectoria.models.Reconocimiento` -> table `RECONOCIMIENTOS`
- `apps.trayectoria.models.CursoRealizado` -> table `CURSOSREALIZADOS`
- `apps.trayectoria.models.ProductoAcademico` -> table `PRODUCTOSACADEMICOS`
- `apps.trayectoria.models.ProductoLaboral` -> table `PRODUCTOSLABORALES`
- `apps.trayectoria.models.VentaGarage` -> table `VENTAGARAGE`


Azure Blob Storage (optional - certificates storage)
- Install SDK: `pip install azure-storage-blob`
- Environment variables (required):
  - `AZURE_STORAGE_CONNECTION_STRING` - Connection string for your storage account (preferred name)
  - `AZURE_STORAGE_CONTAINER` - Container name (default: `certificados`)
  - Note: the code also falls back to `AZURE_CONNECTION_STRING` / `AZURE_CONTAINER` if present for backward compatibility.
- Utility: `apps/trayectoria/services/azure_storage.py` exposes `upload_pdf(file_obj, filename=None)` which uploads a PDF and returns the blob URL.
- Admin upload: In `apps/trayectoria/admin.py` the admin forms for `CursoRealizado` and `Reconocimiento` include an optional **Certificado (PDF)** upload field; when a PDF is uploaded it is sent to Azure and `rutacertificado` is set to the returned URL.

PDF generation
- We now use WeasyPrint to render the real HTML/CSS (same template used for the public CV) into A4 PDFs with correct pagination.
  - Install: `pip install weasyprint`
  - Note: On Windows you may need system dependencies (GTK/Cairo/Pango, etc.). See https://weasyprint.org/docs/ for platform install notes.
  - The views `apps/perfil/views.py` implement the PDF endpoints `/descargar-cv/` and `/descargar-cv-completo/` using WeasyPrint and `request.build_absolute_uri('/')` as `base_url` so static files, fonts and Azure-hosted images are loaded correctly.

Notes:
- Files are NOT stored in `MEDIA_ROOT` — only the public URL is saved in the DB.
- Ensure your container allows public access or you provide SAS URLs depending on your security model.
- Test the flow by setting the env vars and uploading a PDF in the admin; the `rutacertificado` field will be updated with the Azure URL..
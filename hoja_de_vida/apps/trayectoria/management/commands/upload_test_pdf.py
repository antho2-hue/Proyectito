import io
import sys
import traceback
from django.core.management.base import BaseCommand
from azure.core.exceptions import AzureError

from apps.trayectoria.services.azure_storage import upload_pdf, _get_container_client


# Minimal PDF bytes (1-page, simple). Generated, small and free to use.
MINIMAL_PDF = (
    b"%PDF-1.1\n"
    b"1 0 obj<</Type /Catalog /Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type /Pages /Kids [3 0 R] /Count 1>>endobj\n"
    b"3 0 obj<</Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
    b"4 0 obj<</Length 44>>stream\nBT /F1 12 Tf 20 180 Td (Prueba de certificado) Tj ET\nendstream endobj\n"
    b"5 0 obj<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>endobj\n"
    b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000225 00000 n \n0000000330 00000 n \ntrailer<</Size 6 /Root 1 0 R>>\nstartxref\n390\n%%EOF\n"
)


class Command(BaseCommand):
    help = 'Upload a small test PDF to the Azure "certificados" container and print the resulting blob URL.'

    def handle(self, *args, **options):
        # Build in-memory file-like object
        file_obj = io.BytesIO(MINIMAL_PDF)
        file_obj.name = 'prueba_certificado.pdf'

        # Check container and connection early for clearer errors
        try:
            container_client = _get_container_client()
        except RuntimeError as exc:
            self.stderr.write('\nERROR: Configuration problem - ' + str(exc) + '\n')
            self.stderr.write('Check that the environment variable AZURE_STORAGE_CONNECTION_STRING is set and valid.\n')
            sys.exit(1)
        except Exception as exc:  # broad catch to show clear message
            self.stderr.write('\nERROR: Unexpected problem while creating container client: ' + str(exc) + '\n')
            traceback.print_exc()
            sys.exit(1)

        # Check that container exists
        try:
            if not container_client.exists():
                self.stderr.write(f"ERROR: The container '{container_client.container_name}' does not exist or is inaccessible.\n")
                self.stderr.write('Confirm the container exists in your storage account and that the connection string has the required permissions.\n')
                sys.exit(1)
        except AzureError as exc:
            self.stderr.write('\nERROR: Connection or permissions error when checking container: ' + str(exc) + '\n')
            self.stderr.write('Verify the connection string and that the account has access to the container.\n')
            sys.exit(1)
        except Exception as exc:
            self.stderr.write('\nERROR: Unexpected error when checking container: ' + str(exc) + '\n')
            traceback.print_exc()
            sys.exit(1)

        # Upload: use fixed blob name 'prueba_certificado.pdf' so the blob has a predictable name
        try:
            blob_client = container_client.get_blob_client('prueba_certificado.pdf')
            file_obj.seek(0)
            data = file_obj.read()
            blob_client.upload_blob(data, overwrite=True, content_type='application/pdf')
            url = blob_client.url
        except RuntimeError as exc:
            self.stderr.write('\nERROR: Upload failed: ' + str(exc) + '\n')
            sys.exit(1)
        except AzureError as exc:
            self.stderr.write('\nERROR: Azure error during upload: ' + str(exc) + '\n')
            sys.exit(1)
        except Exception as exc:
            self.stderr.write('\nERROR: Unexpected exception during upload: ' + str(exc) + '\n')
            traceback.print_exc()
            sys.exit(1)

        # Success
        self.stdout.write('\n✅ Upload successful!')
        self.stdout.write('Blob URL: ' + url + '\n')
        self.stdout.write('Now verify in the Azure Portal that the blob appears inside the container "certificados".')

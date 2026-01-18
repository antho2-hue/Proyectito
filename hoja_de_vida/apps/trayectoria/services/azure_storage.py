import os
import uuid
from azure.storage.blob import BlobServiceClient


def _get_container_client():
    # Prefer AZURE_STORAGE_CONNECTION_STRING; fall back to legacy AZURE_CONNECTION_STRING
    conn_str = os.environ.get('AZURE_STORAGE_CONNECTION_STRING') or os.environ.get('AZURE_CONNECTION_STRING')
    # Prefer AZURE_STORAGE_CONTAINER; fall back to AZURE_CONTAINER
    container = os.environ.get('AZURE_STORAGE_CONTAINER') or os.environ.get('AZURE_CONTAINER', 'certificados')
    if not conn_str:
        raise RuntimeError('AZURE_STORAGE_CONNECTION_STRING is not set. Set AZURE_STORAGE_CONNECTION_STRING in the environment.')
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    return blob_service_client.get_container_client(container)


def upload_pdf(file_obj, filename=None):
    """Upload a file-like object to Azure Blob Storage and return the blob URL.

    - file_obj: file-like object (e.g., Django UploadedFile or BytesIO)
    - filename: optional desired filename (if None, use uuid + original name)

    Returns the public URL to the uploaded blob (container must allow public access).
    Raises RuntimeError on configuration errors or upload failures.
    """
    container_client = _get_container_client()

    if filename:
        base_name = filename
    else:
        base_name = getattr(file_obj, 'name', None) or 'file'

    ext = os.path.splitext(base_name)[1] or '.pdf'
    blob_name = f"{uuid.uuid4().hex}{ext}"

    blob_client = container_client.get_blob_client(blob_name)

    # upload
    try:
        # If file_obj has chunks() (UploadedFile), read it accordingly
        if hasattr(file_obj, 'chunks'):
            data = b''.join(chunk for chunk in file_obj.chunks())
        else:
            data = file_obj.read()
        blob_client.upload_blob(data, overwrite=True, content_type='application/pdf')
    except Exception as exc:
        raise RuntimeError(f'Failed to upload blob: {exc}')

    # Construct URL
    return blob_client.url

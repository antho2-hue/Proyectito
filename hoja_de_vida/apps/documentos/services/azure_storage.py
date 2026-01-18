import os
import uuid
from django.conf import settings
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError


def _get_blob_service_client():
    conn_str = os.environ.get('AZURE_STORAGE_CONNECTION_STRING') or os.environ.get('AZURE_CONNECTION_STRING')
    if not conn_str:
        raise RuntimeError('AZURE_STORAGE_CONNECTION_STRING is not set. Set AZURE_STORAGE_CONNECTION_STRING in the environment.')
    return BlobServiceClient.from_connection_string(conn_str)


def upload_profile_image(file_obj, filename=None):
    """Upload a PNG image to Azure Blob Storage and return the blob URL (container kept private).

    Behavior:
      - Uses the container specified in Django settings: `AZURE_STORAGE_CONTAINER` (required).
      - Creates the container if it does not exist and enforces private access when possible.
      - Validates that uploaded file is PNG (by extension or content_type when available).
      - Returns the internal blob URL (not a public SAS); the container is private by default.

    Raises RuntimeError on configuration or upload failures.
    """
    # Use container defined in Django settings (exact requirement)
    container = getattr(settings, 'AZURE_STORAGE_CONTAINER', None)
    if not container:
        raise RuntimeError('AZURE_STORAGE_CONTAINER setting not found. Please set AZURE_STORAGE_CONTAINER in Django settings.')

    blob_service_client = _get_blob_service_client()
    container_client = blob_service_client.get_container_client(container)

    # Ensure container exists (create if missing). Keep it private (public_access=None).
    try:
        container_client.create_container()
    except ResourceExistsError:
        pass
    except Exception as exc:
        raise RuntimeError(f'Error ensuring Azure container exists: {exc}')

    # Attempt to set container ACL to private to ensure no public access (best-effort).
    try:
        container_client.set_container_access_policy(public_access=None)
    except Exception:
        # not fatal — continue even if we cannot change ACL due to permissions
        pass

    # Validate PNG: prefer content_type, fallback to extension
    name = filename or getattr(file_obj, 'name', '') or ''
    _, ext = os.path.splitext(name)
    ext = ext.lower()
    content_type = getattr(file_obj, 'content_type', '') or ''

    if not (ext == '.png' or content_type == 'image/png'):
        raise RuntimeError('Only PNG images are allowed (file must be .png and/or content_type image/png).')

    blob_name = f"{uuid.uuid4().hex}.png"
    blob_client = container_client.get_blob_client(blob_name)

    # Read data robustly from UploadedFile or file-like
    try:
        if hasattr(file_obj, 'chunks'):
            data = b''.join(chunk for chunk in file_obj.chunks())
        else:
            data = file_obj.read()
    except Exception as exc:
        raise RuntimeError(f'Error reading uploaded image: {exc}')

    # Upload and set content type explicitly
    try:
        blob_client.upload_blob(data, overwrite=True, content_type='image/png')
    except Exception as exc:
        raise RuntimeError(f'Failed to upload image blob to Azure: {exc}')

    # Return internal blob URL (container is private; this URL is not a public SAS)
    return blob_client.url
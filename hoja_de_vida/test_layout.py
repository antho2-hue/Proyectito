#!/usr/bin/env python
"""Test the CV layout and generate PDFs for visual inspection."""

import os
import sys
import django
from urllib.request import urlopen
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

def fetch_and_save_pdf(url, filename):
    """Fetch a PDF from a URL and save it locally."""
    try:
        print(f"\nFetching {url}...")
        time.sleep(1)  # Give server time to respond
        response = urlopen(url, timeout=10)
        if response.status == 200:
            with open(filename, 'wb') as f:
                f.write(response.read())
            print(f"✓ Saved {filename} ({len(response.read())} bytes)")
            return True
        else:
            print(f"✗ HTTP {response.status}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

# Test URLs
base_url = 'http://127.0.0.1:8000'
cv_url = f'{base_url}/descargar-cv/'
full_cv_url = f'{base_url}/descargar-cv-completo/?check_all=1'

print("=" * 60)
print("CV LAYOUT TEST - PDF Generation")
print("=" * 60)

# Generate single CV PDF
print("\n1. Testing single CV PDF (Check)...")
fetch_and_save_pdf(cv_url, 'test_cv_layout.pdf')

# Generate full CV with certificates PDF
print("\n2. Testing full CV PDF with certificates (Check All)...")
fetch_and_save_pdf(full_cv_url, 'test_cv_layout_full.pdf')

print("\n" + "=" * 60)
print("PDF files saved for visual inspection:")
print("  - test_cv_layout.pdf (single CV)")
print("  - test_cv_layout_full.pdf (full CV with certs)")
print("=" * 60)

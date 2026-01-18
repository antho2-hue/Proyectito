#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now we can import Django modules
from apps.perfil.views import get_pdf_css, descargar_cv_pdf
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def test_pdf_css():
    """Test if PDF CSS can be loaded."""
    print("Testing PDF CSS loading...")
    css = get_pdf_css()
    print(f"CSS length: {len(css)} characters")
    if css:
        print("✓ CSS loaded successfully")
        print(f"First 200 chars: {css[:200]}...")
    else:
        print("✗ CSS loading failed")
    return bool(css)

def test_pdf_view():
    """Test PDF view rendering and full CV export."""
    print("\nTesting PDF view...")
    factory = RequestFactory()
    request = factory.get('/descargar-cv/', HTTP_HOST='127.0.0.1:8000', SERVER_NAME='127.0.0.1', SERVER_PORT='8000')
    request.user = AnonymousUser()

    try:
        response = descargar_cv_pdf(request)
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            print("✓ PDF view works correctly")
            print(f"Content type: {response.get('Content-Type')}")
            print(f"Content disposition: {response.get('Content-Disposition')}")
            pdf_bytes = response.content
            if b'Check All' in pdf_bytes or b'Check' in pdf_bytes:
                print("✓ 'Check' text found in PDF bytes")
            else:
                print("⚠ 'Check' text NOT found in PDF bytes (may be rendered as glyphs or not embedded)")
        else:
            print("✗ PDF view failed")
            print(f"Response content: {response.content[:500]}")
    except Exception as e:
        print(f"✗ Exception in PDF view: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Now test full CV with certificates (Check All)
    print("\nTesting full CV (Check All)...")
    request2 = factory.get('/descargar-cv-completo/', {'check_all': '1'}, HTTP_HOST='127.0.0.1:8000', SERVER_NAME='127.0.0.1', SERVER_PORT='8000')
    request2.user = AnonymousUser()
    try:
        from apps.perfil.views import descargar_cv_completo_pdf
        resp2 = descargar_cv_completo_pdf(request2)
        print(f"Full CV Response status: {resp2.status_code}")
        if resp2.status_code == 200:
            print("✓ Full CV PDF generated")
            return True
        else:
            print("✗ Full CV PDF failed")
            return False
    except Exception as e:
        print(f"✗ Exception generating full CV: {e}")
        return False

if __name__ == '__main__':
    print("Testing PDF functionality...\n")

    css_ok = test_pdf_css()
    view_ok = test_pdf_view()

    print("\nResults:")
    print(f"CSS loading: {'✓' if css_ok else '✗'}")
    print(f"PDF view: {'✓' if view_ok else '✗'}")
    print(f"Overall: {'✓ All tests passed' if css_ok and view_ok else '✗ Some tests failed'}")

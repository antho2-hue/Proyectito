from pathlib import Path
import dj_database_url
import os

# =========================================================
# BASE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-dev-key-only-for-local"
)

DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "curriculo.onrender.com",
]

if DEBUG:
    ALLOWED_HOSTS.append("*")

# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps
    "apps.perfil.apps.PerfilConfig",
    "apps.trayectoria.apps.TrayectoriaConfig",
    "apps.documentos.apps.DocumentosConfig",
    "apps.accounts.apps.AccountsConfig",
]

# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# =========================================================
# DATABASE
# =========================================================

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        ssl_require=False
    )
}

# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =========================================================
# I18N
# =========================================================

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if DEBUG:
    STATICFILES_DIRS = [
        BASE_DIR / "static",
        BASE_DIR / "apps" / "perfil" / "static",
    ]

if DEBUG:
    # Use the simple staticfiles storage in development to avoid manifest lookup errors
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# MEDIA files (user uploaded) - used in DEBUG and by deployment
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =========================================================
# AZURE BLOB STORAGE (OPCIONAL)
# =========================================================

AZURE_STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER", "certificados")

# Azure es opcional - la app funciona sin él

# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# =========================================================
# DJANGO ADMIN CUSTOMIZATION - VAPORWAVE THEME
# =========================================================

ADMIN_SITE_HEADER = "📄 HOJA DE VIDA MODERNA"
ADMIN_SITE_TITLE = "HDV - Administrador"
ADMIN_INDEX_TITLE = "Centro de Control - Perfil Profesional"
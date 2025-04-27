# indspice_backend/settings.py

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Production Setting: SECRET_KEY ---
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY and os.environ.get('DJANGO_DEBUG', 'False') != 'True':
    raise ValueError("DJANGO_SECRET_KEY environment variable not set in production!")
# -------------------------------------

# --- Production Setting: DEBUG ---
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
# --------------------------------

# --- Production Setting: ALLOWED_HOSTS ---
# Read from env var, split by comma. Add your MAIN backend hostnames here.
# Example value for ALLOWED_HOSTS env var: "api.indspiceorganics.com,your-app.onrender.com"
ALLOWED_HOSTS_STRING = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',') if host.strip()]

if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

if not DEBUG and not ALLOWED_HOSTS:
     raise ValueError("ALLOWED_HOSTS environment variable is empty or not set in production!")
# --------------------------------------


# Application definition
INSTALLED_APPS = [
    'corsheaders',
    'whitenoise.runserver_nostatic', # If using whitenoise
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'contact_api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # If using whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'indspice_backend.urls'

TEMPLATES = [ # ... Keep your template settings ...
    { # ... (your template config) ...
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'indspice_backend.wsgi.application'

# --- Production Setting: DATABASES ---
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}' if DEBUG else None,
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}
if DATABASES['default'] is None and not DEBUG:
    raise ValueError("DATABASE_URL environment variable not set in production!")
# ------------------------------------

# Password validation
AUTH_PASSWORD_VALIDATORS = [ # Keep validators...
     { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
     { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
     { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
     { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Production Setting: Static files ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # If using whitenoise
# ---------------------------------------

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Production Setting: Email (Zoho SMTP) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('ZOHO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('ZOHO_APP_PASSWORD')

if not DEBUG:
    if not EMAIL_HOST_USER: raise ValueError("ZOHO_EMAIL_USER env var not set!")
    if not EMAIL_HOST_PASSWORD: raise ValueError("ZOHO_APP_PASSWORD env var not set!")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ADMIN_EMAIL = ['info@indspiceorganics.com'] # Correct recipient
# ---------------------------------------

# --- Production Setting: CORS ---
# Allow requests explicitly from your frontend domain(s)
CORS_ALLOWED_ORIGINS = [
    "https://indspiceorganics.com",
    "https://www.indspiceorganics.com",
]
# Allow localhost only when in debug mode
if DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        "http://localhost:5173", # Replace 5173 if your dev port is different
        "http://127.0.0.1:5173",
    ])

CORS_ALLOW_ALL_ORIGINS = False # Ensure this is False
# CORS_ALLOW_CREDENTIALS = True # Uncomment if needed later for cookies/auth
# ----------------------------

# --- Production Setting: CSRF ---
# Trust requests coming from your frontend domain(s)
CSRF_TRUSTED_ORIGINS = [
    "https://indspiceorganics.com",
    "https://www.indspiceorganics.com",
]
# Add localhost only for debug mode convenience
if DEBUG:
     CSRF_TRUSTED_ORIGINS.extend([
        "http://localhost:5173", # Replace 5173 if your dev port is different
        "http://127.0.0.1:5173",
    ])

CSRF_COOKIE_SECURE = not DEBUG # Use secure cookie only in production (HTTPS)
SESSION_COOKIE_SECURE = not DEBUG # Use secure cookie only in production (HTTPS)
# ---------------------------
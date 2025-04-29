# indspice_backend/settings.py

import os
from pathlib import Path
# import dj_database_url # No longer needed for this setup

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# CORE SETTINGS (Set via Environment Variables in Production)
# ==============================================================================

# --- SECRET KEY ---
# Load from environment variable. Generate a strong key for production.
# NEVER commit your production key.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
# ------------------

# --- DEBUG MODE ---
# Defaults to False (production) unless overridden by env var
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
# ------------------

# --- ALLOWED HOSTS ---
# Read comma-separated hosts from environment variable.
# Example Production Env Var: ALLOWED_HOSTS="api.indspiceorganics.com,your-app-name.onrender.com"
ALLOWED_HOSTS_STRING = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',') if host.strip()]

# Automatically add Render's hostname if provided by the platform
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    # Prevent duplicates if already included in ALLOWED_HOSTS env var
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Add localhost/127.0.0.1 ONLY when running locally in Debug mode
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])
# ---------------------


# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    'corsheaders',
    # Django Core Apps (keep for basic functionality/potential future use)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Your custom apps
    'contact_api',
    # 'whitenoise.runserver_nostatic', # Only needed if using whitenoise AND DEBUG=True
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Should be high up
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware', # Add ONLY if serving static files via Django/Gunicorn
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', # Keep active
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'indspice_backend.urls'

TEMPLATES = [
    {
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


# ==============================================================================
# DATABASE (Dummy Configuration - Not Used by Contact API)
# ==============================================================================
# Provide a minimal config to satisfy Django, even if not actively used by your API.
# Using ':memory:' prevents creation of a db.sqlite3 file locally.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
# ==============================================================================


# ==============================================================================
# Password validation (Keep standard validators)
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]
# ==============================================================================


# ==============================================================================
# Internationalization & Static Files
# ==============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles' # Define only if using collectstatic (e.g., for Admin)
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # Define only if using whitenoise
# ==============================================================================


# ==============================================================================
# Default primary key field type
# ==============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ==============================================================================


# ==============================================================================
# EMAIL CONFIGURATION (Using Gmail SMTP via Environment Variables)
# ==============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('GMAIL_USER')         # Example: indspiceorganics@gmail.com
EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD') # Your Google App Password

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or 'noreply@indspiceorganics.com' # Fallback if env var missing
ADMIN_EMAIL = ['info@indspiceorganics.com'] # Address receiving the contact form notifications
# ==============================================================================


# ==============================================================================
# SECURITY SETTINGS (CORS, CSRF - Rely on Environment Variables for Production)
# ==============================================================================

# --- CORS ---
# Example Production Env Var: CORS_ALLOWED_ORIGINS="https://indspiceorganics.com,https://www.indspiceorganics.com"
CORS_ALLOWED_ORIGINS_STRING = os.environ.get('CORS_ALLOWED_ORIGINS', '')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS_STRING.split(',') if origin.strip()]
if DEBUG: # Allow local frontend only during local development
    CORS_ALLOWED_ORIGINS.extend([ f"http://localhost:{os.environ.get('FRONTEND_PORT', '5173')}", f"http://127.0.0.1:{os.environ.get('FRONTEND_PORT', '5173')}"])
CORS_ALLOW_ALL_ORIGINS = False
# CORS_ALLOW_CREDENTIALS = True # Needed if frontend sends cookies/auth headers

# --- CSRF ---
# Example Production Env Var: CSRF_TRUSTED_ORIGINS="https://indspiceorganics.com,https://www.indspiceorganics.com"
CSRF_TRUSTED_ORIGINS_STRING = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_STRING.split(',') if origin.strip()]
if DEBUG: # Trust local frontend only during local development
     CSRF_TRUSTED_ORIGINS.extend([ f"http://localhost:{os.environ.get('FRONTEND_PORT', '5173')}", f"http://127.0.0.1:{os.environ.get('FRONTEND_PORT', '5173')}"])

# --- Secure Cookies in Production ---
CSRF_COOKIE_SECURE = not DEBUG # True if DEBUG is False
SESSION_COOKIE_SECURE = not DEBUG # True if DEBUG is False
# ==============================================================================


# ==============================================================================
# FINAL PRODUCTION CHECKS (Raise errors if critical env vars missing)
# ==============================================================================
if not DEBUG:
    if not SECRET_KEY: raise ValueError("DJANGO_SECRET_KEY environment variable not set!")
    if not ALLOWED_HOSTS: raise ValueError("ALLOWED_HOSTS not configured correctly!")
    if not EMAIL_HOST_USER: raise ValueError("GMAIL_USER environment variable not set!")
    if not EMAIL_HOST_PASSWORD: raise ValueError("GMAIL_APP_PASSWORD environment variable not set!")
    if not CORS_ALLOWED_ORIGINS: raise ValueError("CORS_ALLOWED_ORIGINS not configured correctly!")
    if not CSRF_TRUSTED_ORIGINS: raise ValueError("CSRF_TRUSTED_ORIGINS not configured correctly!")
    if EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
         print("WARNING: Using console EmailBackend in production (DEBUG=False)!")
# ==============================================================================
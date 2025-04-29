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
# Render automatically adds its own hostname. Add your custom API domain via env var.
# Example value for ALLOWED_HOSTS env var: "api.indspiceorganics.com"
ALLOWED_HOSTS_STRING = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',') if host.strip()]

# Add Render's provided hostname automatically if it exists (common pattern)
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

if not DEBUG and not ALLOWED_HOSTS:
     raise ValueError("ALLOWED_HOSTS environment variable is empty or not set correctly in production!")
# --------------------------------------


# Application definition
INSTALLED_APPS = [
    'corsheaders',
    'whitenoise.runserver_nostatic', # Static file serving helper for development
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Needed for static files AND whitenoise
    'contact_api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Should be high up
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <<< Whitenoise Middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', # CSRF Protection
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


# --- Production Setting: DATABASES ---
DATABASES = {
    'default': dj_database_url.config(
        # Fallback to SQLite only in local DEBUG mode if DATABASE_URL isn't set
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}' if DEBUG else None,
        conn_max_age=600, # Recommended for persistent connections
        # Require SSL for database connection when not in debug mode
        ssl_require=not DEBUG
    )
}
if DATABASES['default'] is None and not DEBUG:
    raise ValueError("DATABASE_URL environment variable not set in production!")
# ------------------------------------


# Password validation
AUTH_PASSWORD_VALIDATORS = [
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
# Directory where collectstatic will gather static files.
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Enable efficient serving and compression of static files with Whitenoise.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# ---------------------------------------


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Production Setting: Email (Gmail SMTP via Environment Variables) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('indspiceorganics@gmail.com')         # Set this env var on Render
EMAIL_HOST_PASSWORD = os.environ.get('tjdhcwlnrpblepxy') # Set this env var on Render (App Password)

# Add checks for required email env vars in production
if not DEBUG:
    if not EMAIL_HOST_USER: raise ValueError("GMAIL_USER environment variable not set!")
    if not EMAIL_HOST_PASSWORD: raise ValueError("GMAIL_APP_PASSWORD environment variable not set!")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER # Send from your Gmail address
ADMIN_EMAIL = ['info@indspiceorganics.com'] # Send notifications TO this address
# ----------------------------------------------------------------------


# --- Production Setting: CORS ---
# Allow requests explicitly from your frontend domain(s) in production
CORS_ALLOWED_ORIGINS = [
    "https://indspiceorganics.com",
    "https://www.indspiceorganics.com",
]
# Allow localhost only when in debug mode for local development
if DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        "http://localhost:5173", # Replace 5173 if your dev port differs
        "http://127.0.0.1:5173",
    ])
CORS_ALLOW_ALL_ORIGINS = False # Must be False in production
# CORS_ALLOW_CREDENTIALS = True # Uncomment if sending cookies/auth headers
# ----------------------------


# --- Production Setting: CSRF ---
# Trust POST requests coming from your frontend domain(s)
CSRF_TRUSTED_ORIGINS = [
    "https://indspiceorganics.com",
    "https://www.indspiceorganics.com",
]
# Add localhost only for debug mode convenience
if DEBUG:
     CSRF_TRUSTED_ORIGINS.extend([
        "http://localhost:5173", # Replace 5173 if your dev port differs
        "http://127.0.0.1:5173",
    ])
# Ensure CSRF/Session cookies use HTTPS in production
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
# ---------------------------

# --- Final Check for Production Readiness ---
if not DEBUG:
    if not ALLOWED_HOSTS: raise ValueError("ALLOWED_HOSTS is not configured correctly for production!")
    if not CORS_ALLOWED_ORIGINS: raise ValueError("CORS_ALLOWED_ORIGINS is not configured correctly for production!")
    if not CSRF_TRUSTED_ORIGINS: raise ValueError("CSRF_TRUSTED_ORIGINS is not configured correctly for production!")
    if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        print("WARNING: Using SQLite database in production (DEBUG=False)! Configure DATABASE_URL.")
    if EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
         print("WARNING: Using console EmailBackend in production (DEBUG=False)! Configure production email settings.")
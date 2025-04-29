"""
WSGI config for indspice_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
try:
    import dotenv
except ImportError:
    dotenv = None

if dotenv:
    # Adjust path if .env is one level up from wsgi.py
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(dotenv_path):
         dotenv.load_dotenv(dotenv_path=dotenv_path)
    else:
         # Fallback if running directly where wsgi.py is? Less common.
         dotenv.load_dotenv()
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'indspice_backend.settings')

application = get_wsgi_application()

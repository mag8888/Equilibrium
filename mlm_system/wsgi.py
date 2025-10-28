"""
WSGI config for mlm_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlm_system.settings')

application = get_wsgi_application()

# Авто-применение миграций на старте (защита, если платформа игнорирует start.sh)
try:
    call_command('migrate', interactive=False, run_syncdb=True, verbosity=0)
except Exception:
    # Не мешаем запуску, если миграции не могут выполниться здесь
    pass

"""
WSGI config for vercel_app project.

It exposes the WSGI callable as a module-level variable named ``app``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import sys
import types
from importlib.metadata import PackageNotFoundError, version as _version

# pkg_resources is not available in Vercel's Python 3.12 runtime.
# Provide a minimal shim so drf_yasg can import without errors.
if 'pkg_resources' not in sys.modules:
    _pkg = types.ModuleType('pkg_resources')

    class DistributionNotFound(Exception):
        pass

    def get_distribution(name):
        try:
            dist = types.SimpleNamespace(version=_version(name))
            return dist
        except PackageNotFoundError:
            raise DistributionNotFound(name)

    _pkg.DistributionNotFound = DistributionNotFound
    _pkg.get_distribution = get_distribution
    sys.modules['pkg_resources'] = _pkg

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vercel_app.settings')

app = get_wsgi_application()

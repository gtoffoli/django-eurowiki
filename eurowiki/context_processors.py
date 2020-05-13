from django.conf import settings
from .classes import Country

def processor(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.META.get('HTTP_HOST', '')
    path = request.path
    return {
        'site_name': settings.SITE_NAME,
        'path_no_language': path,
        'PROTOCOL': protocol,
        'HOST': host,
        'DOMAIN': host,
        'HAS_SAML2': settings.HAS_SAML2,
        'DJANGO_VERSION': settings.DJANGO_VERSION,
        'COUNTRIES':  [Country(qcode) for qcode in settings.EU_COUNTRY_LABELS.keys()],
    }

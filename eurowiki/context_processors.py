from django.conf import settings
from .classes import Country
from django.utils.translation import get_language

def country_predicates (language=None):
    labels = settings.PREDICATE_LABELS
    predicates = []
    for predicate_id in settings.EU_COUNTRY_PROPERTIES:
        predicates.append([predicate_id, labels.get(predicate_id).get(language)])
    return predicates


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
        'COUNTRIES':  [Country(id=qcode) for qcode in settings.EU_COUNTRY_LABELS.keys()],
        'COUNTRY_PREDICATES' : country_predicates(language=get_language()[:2]),
    }

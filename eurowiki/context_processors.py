from datetime import datetime
from django.conf import settings

def processor(request):
    path = request.path
    protocol = request.is_secure() and 'https' or 'http'
    host = request.META.get('HTTP_HOST', '')
    """
    is_primary_domain = False
    is_secondary_domain = False
    is_test_domain = False
    if host == settings.PRIMARY_DOMAIN:
        is_primary_domain = True
    elif host == settings.SECONDARY_DOMAIN:
        is_secondary_domain = True
    elif host == settings.TEST_DOMAIN:
        is_test_domain = True

    for code, name in settings.LANGUAGES:
        # path = path.replace('/%s/' % language[0], '/')
        if path.startswith('/' + code + '/'):
            path = path[len(code)+1:]
            break
    canonical = '%s://%s%s' % (protocol, settings.PRIMARY_DOMAIN, path)
    """
    return {
        'site_name': settings.SITE_NAME,
        """
        'path_no_language': path,
        'PRODUCTION': settings.PRODUCTION,
        """
        'PROTOCOL': protocol,
        'LANGUAGE_CODE': settings.LANGUAGE_CODE,
        'HOST': host,
        """
        'is_primary_domain': is_primary_domain,
        'is_secondary_domain': is_secondary_domain,
        'is_test_domain': is_test_domain,
        """
        'DOMAIN': host,
        # 'CANONICAL': canonical,
        'HAS_SAML2': settings.HAS_SAML2,
        'DJANGO_VERSION': settings.DJANGO_VERSION,
    }

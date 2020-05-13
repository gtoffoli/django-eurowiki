from django.conf import settings
from django.utils.translation import get_language

class Country(object):

    def __init__(self, qcode):
        self.qcode = qcode

    def labels(self):
        return settings.EU_COUNTRY_LABELS[self.qcode]

    def label(self, language=None):
        if not language:
            language = get_language()[:2]
        return self.labels()[language]

    def url(self):
        return '/country/{}/'.format(self.qcode)

from django.conf import settings
from django.utils.translation import get_language
from rdflib.term import Literal
from rdflib_django.utils import get_named_graph
from .utils import make_uriref, id_from_uriref, wd_get_image_url

class EurowikiBase(object):

    def __init__(self, uriref=None, id=None, graph=None):
        assert uriref or id
        if uriref:
            self.uriref = uriref
            self.id = id_from_uriref(uriref)
        elif id:
            self.id = id
            self.uriref = make_uriref(id)
        if not graph:
            graph_identifier = make_uriref('http://www.wikidata.org')
            graph = get_named_graph(graph_identifier)
        self.graph = graph

    def labels(self):
        return {}

    def label(self, language=None):
        if not language:
            language = get_language()[:2]
        return self.labels().get(language, self.labels().get('en', '')) or self.id

    def is_wikidata(self):
        return self.uriref.count(settings.WIKIDATA_BASE)

    def wd_url(self):
        return self.is_wikidata() and self.uriref.replace('http:', 'https:') or None

class Item(EurowikiBase):

    def url(self):
        return '/item/{}/'.format(self.id)

    def labels(self):
        return settings.OTHER_ITEM_LABELS.get(self.id, {})

    def properties(self, keys=[]):
        p_o_iterable = self.graph.predicate_objects(subject=self.uriref)
        if keys:
            p_o_iterable = [[p, o] for [p, o] in p_o_iterable if id_from_uriref(p) in keys]
        p_o_iterable = sorted(p_o_iterable, key=lambda p_o: settings.ORDERED_PREDICATE_KEYS.index(id_from_uriref(p_o[0])))
        props = []
        for p, o in p_o_iterable:
            if keys and not keys.count(id_from_uriref(p)):
                continue
            p = Predicate(uriref=p, graph=self.graph)
            if p.is_literal():
                if p.is_image():
                    o = Image(o)
            else:
                o = Item(uriref=o, graph=self.graph)
            props.append([p, o])
        return props

class Country(Item):

    def url(self):
        return '/country/{}/'.format(self.id)

    def labels(self):
        return settings.EU_COUNTRY_LABELS.get(self.id, {})

    def properties(self):
        return super(Country, self).properties(keys=settings.EU_COUNTRY_PROPERTIES)

    def banner_url(self):
        predicate = make_uriref('P948', prefix='wdt')
        banners = list(self.graph.objects(subject=self.uriref, predicate=predicate))
        return banners and wd_get_image_url(banners[0]) or None

class Predicate(EurowikiBase):

    def labels(self):
        return settings.PREDICATE_LABELS.get(self.id, {})

    def is_literal(self):
        return self.id in settings.LITERAL_PROPERTIES

    def is_image(self):
        return self.id in settings.IMAGE_PROPERTIES

class Image(str):

    def __init__(self, name):
        self.name = name

    def url(self):
        return wd_get_image_url(self.name)


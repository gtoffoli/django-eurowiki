from django.conf import settings
from django.utils.translation import get_language
from rdflib.term import Literal
from rdflib_django.utils import get_named_graph
from .utils import make_uriref, id_from_uriref

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

class Item(EurowikiBase):

    def is_literal(self):
        print('is_literal:', isinstance(self.uriref, Literal))
        return isinstance(self.uriref, Literal)

    def is_wikidata(self):
        return self.uriref.count(settings.WIKIDATA_BASE)

    def url(self):
        return '/item/{}/'.format(self.id)

    def wd_url(self):
        return self.is_wikidata() and self.uriref.replace('http:', 'https:') or None

    def labels(self):
        return settings.OTHER_ITEM_LABELS.get(self.id, {})

    def properties(self):
        p_o_iterable = self.graph.predicate_objects(subject=self.uriref)
        p_o_iterable = sorted(p_o_iterable, key=lambda p_o: settings.ORDERED_PREDICATE_KEYS.index(id_from_uriref(p_o[0])))
        props = []
        for p, o in p_o_iterable:
            p = Predicate(uriref=p, graph=self.graph)
            o = Item(uriref=o, graph=self.graph)
            props.append([p, o])
        return props

class Country(Item):

    def url(self):
        return '/country/{}/'.format(self.id)

    def labels(self):
        return settings.EU_COUNTRY_LABELS.get(self.id, {})

class Predicate(EurowikiBase):

    def labels(self):
        return settings.PREDICATE_LABELS.get(self.id, {})

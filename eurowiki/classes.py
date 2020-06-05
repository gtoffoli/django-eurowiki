from django.conf import settings
from django.utils.translation import get_language
from rdflib.term import Literal
from rdflib_django.utils import get_named_graph, get_conjunctive_graph
from .utils import make_uriref, id_from_uriref, wd_get_image_url

class EurowikiBase(object):

    # def __init__(self, uriref=None, id=None, graph=None):
    def __init__(self, uriref=None, id=None, graph=None, graph_identifier=None):
        assert uriref or id
        if uriref:
            self.uriref = uriref
            self.id = id_from_uriref(uriref)
        elif id:
            self.id = id
            self.uriref = make_uriref(id)
        if graph_identifier:
            graph = get_named_graph(graph_identifier)
        elif not graph:
            graph = get_conjunctive_graph()
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

    def properties(self, keys=[], language=None):
        if not language:
            language = get_language()[:2]
        p_o_iterable = self.graph.predicate_objects(subject=self.uriref)
        if keys:
            p_o_iterable = [[p, o] for [p, o] in p_o_iterable if id_from_uriref(p) in keys]
        p_o_iterable = sorted(p_o_iterable, key=lambda p_o: settings.ORDERED_PREDICATE_KEYS.index(id_from_uriref(p_o[0])))
        props = []
        lang_code_dict = {}
        value_dict = {}
        property_dict = {}
        for prop_id in settings.RDF_I18N_PROPERTIES:
            lang_code_dict[prop_id] = None
            value_dict[prop_id] = None
            property_dict[prop_id] = None
        for p, o in p_o_iterable:
            if keys and not keys.count(id_from_uriref(p)):
                continue
            p = Predicate(uriref=p, graph=self.graph)
            if p.is_literal():
                if p.is_image():
                    o = Image(o)
                else:
                    prop_id = p.id
                    if prop_id in settings.RDF_I18N_PROPERTIES:
                        lang = o.language
                        if lang==language:
                            lang_code_dict[prop_id] = lang
                            property_dict[prop_id] = p
                            value_dict[prop_id] = o.value
                        elif not value_dict[prop_id] and lang==settings.LANGUAGE_CODE:
                            lang_code_dict[prop_id] = lang
                            property_dict[prop_id] = p
                            value_dict[prop_id] = o.value
                        elif lang and (not value_dict[prop_id] or (lang_code_dict[prop_id] in settings.LANGUAGE_CODES and lang in settings.LANGUAGE_CODES and settings.LANGUAGE_CODES.index(lang)<settings.LANGUAGE_CODES.index(lang_code_dict[prop_id]))):
                            lang_code_dict[prop_id] = lang
                            property_dict[prop_id] = p
                            value_dict[prop_id] = o.value
                        print('', lang, o.value)
                        if lang:
                            continue
            else:
                o = Item(uriref=o, graph=self.graph)
            props.append([p, o])
        for prop_id in settings.RDF_I18N_PROPERTIES:
            if value_dict[prop_id]:
                props.append([property_dict[prop_id], value_dict[prop_id]])
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


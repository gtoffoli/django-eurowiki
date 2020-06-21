from django.conf import settings
from django.core.cache import cache
from django.utils.functional import cached_property
from django.utils.translation import get_language
from rdflib.term import BNode
from rdflib_django.utils import get_named_graph, get_conjunctive_graph
from .utils import make_uriref, id_from_uriref, wd_get_image_url

class EurowikiBase(object):

    def __init__(self, uriref=None, id=None, bnode=None, graph=None, graph_identifier=None, in_predicate=None):
        assert uriref or id or bnode
        self.uriref = self.id = self.bnode = None
        if uriref:
            self.uriref = uriref
            self.id = id_from_uriref(uriref)
        elif id:
            self.id = id
            self.uriref = make_uriref(id)
        else:
            self.bnode = bnode
        if graph_identifier:
            graph = get_named_graph(graph_identifier)
        elif not graph:
            graph = get_conjunctive_graph()
        self.graph = graph
        self.in_predicate = in_predicate

    def labels(self):
        return {}

    def label(self, language=None):
        if not language:
            language = get_language()[:2]
        labels = self.labels()
        lbl = labels.get(language, labels.get('en', ''))
        if not lbl:
            if not self.is_wikidata(): # self.bnode or isinstance(self, BNode): # why these alternatives do not work?
                lbl = settings.UNKNOWN_LABEL_DICT.get(language, '?')
            else:
                lbl = self.id
        return lbl

    def is_wikidata(self):
        return self.uriref and self.uriref.count(settings.WIKIDATA_BASE)

    def wd_url(self):
        return self.is_wikidata() and self.uriref.replace('http:', 'https:') or None

class Item(EurowikiBase):

    def url(self):
        # return '/item/{}/'.format(self.id)
        return '/item/{}/'.format(self.id)

    def labels(self):
        return settings.OTHER_ITEM_LABELS.get(self.id, {})

    def preferred_label(self, language=None):
        properties = self.properties(keys=['P1476', 'title', 'label',], exclude_keys=[], language=language)
        if properties:
            return properties[0][1]
        return self.label()

    def properties(self, keys=[], exclude_keys=['P1476', 'title', 'label',], language=None):
        if not keys:
            in_prop_id = self.in_predicate and self.in_predicate.id or None
            if in_prop_id and in_prop_id in settings.EW_TREE_KEYS:
                keys = settings.EW_TREE[in_prop_id]
            else:
                keys = settings.ORDERED_PREDICATE_KEYS
        if exclude_keys:
            keys = [key for key in keys if not key in exclude_keys]
        if not language:
            language = get_language()[:2]
        # get quads, to include context, remove subject and append placeholder for reified properties
        p_o_c_r_iterable = [[quad[1], quad[2], quad[3], None] for quad in self.graph.quads((self.uriref or self.bnode, None, None))]
        p_o_c_r_iterable = [[p, o, c, r] for p, o, c, r in p_o_c_r_iterable if id_from_uriref(p) in keys]
        # handle reified properties and build a triple for each
        RDF_STATEMENT = make_uriref('Statement', prefix='rdf')
        RDF_SUBJECT = make_uriref('subject', prefix='rdf')
        RDF_PREDICATE = make_uriref('predicate', prefix='rdf')
        RDF_OBJECT = make_uriref('object', prefix='rdf')
        quads = self.graph.quads((None, RDF_SUBJECT, self.uriref or self.bnode))
        for quad in quads:
            reified = quad[0]
            p = self.graph.value(subject=reified, predicate=RDF_PREDICATE)
            if not id_from_uriref(p) in keys:
                continue
            o = self.graph.value(subject=reified, predicate=RDF_OBJECT)
            c = quad[3]
            if reified:
                statements = list(self.graph.quads((reified, None, RDF_STATEMENT, None)))
                if statements:
                    reified = statements[0][1]
                    assert isinstance(reified, BNode)
            p_o_c_r_iterable.append((p, o, c, reified))
        # initialize memory for handling language-aware string literals
        lang_code_dict = {}
        value_dict = {}
        property_dict = {}
        context_dict = {}
        reified_dict = {}
        for prop_id in settings.RDF_I18N_PROPERTIES:
            lang_code_dict[prop_id] = None
            value_dict[prop_id] = None
            property_dict[prop_id] = None
            context_dict[prop_id] = None
            reified_dict[prop_id] = None
        props = []
        # iterate on our pseudo-quads
        for p, o, c, r in p_o_c_r_iterable:
            if not keys.count(id_from_uriref(p)):
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
                            context_dict[prop_id] = c
                            reified_dict[prop_id] = r
                        elif not value_dict[prop_id] and lang==settings.LANGUAGE_CODE:
                            lang_code_dict[prop_id] = lang
                            property_dict[prop_id] = p
                            value_dict[prop_id] = o.value
                            context_dict[prop_id] = c
                            reified_dict[prop_id] = r
                        elif lang and (not value_dict[prop_id] or (lang_code_dict[prop_id] in settings.LANGUAGE_CODES and lang in settings.LANGUAGE_CODES and settings.LANGUAGE_CODES.index(lang)<settings.LANGUAGE_CODES.index(lang_code_dict[prop_id]))):
                            lang_code_dict[prop_id] = lang
                            property_dict[prop_id] = p
                            value_dict[prop_id] = o.value
                            context_dict[prop_id] = c
                            reified_dict[prop_id] = r
                        if lang:
                            continue
            else:
                o = Item(uriref=o, graph=self.graph, in_predicate=p)
                if r:
                    r = Item(bnode=r, graph=self.graph, in_predicate=p)
            props.append([p, o, None, c, r])
        # append proper version of language-aware string literals
        for prop_id in settings.RDF_I18N_PROPERTIES:
            if value_dict[prop_id]:
                props.append([property_dict[prop_id], value_dict[prop_id], lang_code_dict[prop_id], context_dict[prop_id], reified_dict[prop_id]])
        # sort properties at the end of all processing
        props = sorted(props, key=lambda prop: keys.index(prop[0].id))
        # record the previous property in the tuple itself, so that it can be accessed in template 
        props_with_pp = []
        previous_p = None
        for prop in props:
            prop.append(previous_p)
            previous_p = prop[0]
            props_with_pp.append(prop)
        return props_with_pp

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

    def is_url(self):
        return self.id in settings.URL_PROPERTIES

    def is_repeatable(self):
        return self.id in settings.REPEATABLE_PROPERTIES

class Image(str):

    def __init__(self, name):
        self.name = name

    def url(self):
        return wd_get_image_url(self.name)

